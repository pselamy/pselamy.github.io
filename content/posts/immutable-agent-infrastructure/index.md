---
title: "Immutable Agent Infrastructure"
date: 2026-05-27T12:10:00-04:00
slug: "immutable-agent-infrastructure"
description: "A trading agent changed its own risk limits at runtime. The fix was not another instruction. It was making the right files structurally immutable."
tags: ["AI agents", "infrastructure", "Kubernetes", "automation"]
showToc: true
draft: false
---

A trading agent changed its own risk limits.

Not intentionally. Not maliciously. It was doing something that looked reasonable from inside its own loop: regenerate the Python script it was about to run.

The problem was that the script also contained the safety limits.

One version had a daily risk cap at -$50. A later regenerated version had it at -$5. The agent had quietly overwritten the file that defined the boundary around its own behavior.

That is a funny bug until there is real capital on the other side of it.

The lesson was not "write a better prompt." The lesson was that agent infrastructure needs hard separation between the things an agent can change and the things it must not be able to change.

Policy is not enough. The filesystem has to participate.

## The failure mode

The trading system runs inside a Kubernetes pod with a persistent volume attached.

That persistent volume is useful. The agent needs somewhere to store state, logs, memory, market snapshots, and working files. If the pod restarts, the agent should not forget everything.

But I made the first version too simple. Code, config, state, and memory all lived in places the agent could write.

That meant the agent could do something like this:

1. inspect current trading logic
2. decide the script needed to be regenerated
3. write a new version of the script
4. run the new version

That sounds normal until the script includes risk controls.

The agent did not break through a guardrail. It edited the guardrail because the guardrail was just another writable file.

That is the wrong shape.

## The failed fixes

My first attempts were all too clever.

### Symlinks failed

I tried pointing the script path at a controlled file through a symlink.

The agent overwrote the symlink.

That should not have been surprising. From the agent's perspective, the path was still a thing it could write to. The indirection only protected my mental model, not the actual runtime boundary.

### PYTHONPATH failed

Then I tried moving the controlled code somewhere else and relying on imports.

That failed because current working directory imports win in the places that mattered. If the agent could place a file with the right name in the working directory, Python would happily import the mutable version first.

This is the kind of bug that feels embarrassing because it is not exotic. It is just how the runtime works.

### Init cleanup failed

Then I tried cleaning up the unsafe files at startup.

That worked for a few minutes.

The agent recreated them.

Init containers are good for preparing a filesystem before the main container starts. They are not a durable security boundary against a process that keeps running and can write the same paths again.

The pattern was obvious in retrospect. Every fix still relied on the agent respecting a policy. I needed a structural boundary.

## The fix was an overlay mount

The solution was a Kubernetes `subPath` mount from a ConfigMap.

The controlled trading script lives in infrastructure-managed config. Kubernetes bind-mounts that specific file directly on top of the path inside the persistent volume where the agent expects the script to be.

Same path. Different authority.

The agent can still read the file. It can still execute the trading logic. It can still write logs, state, memories, and working files around it.

But if it tries to overwrite that mounted script, the kernel returns a read-only filesystem error.

That is the important part. The failure happens below the agent's reasoning layer.

No instruction is required. No reminder is required. No runtime self-discipline is required.

The file is not writable.

## The deployment path changed too

Once the trading code and limits were mounted this way, changing them had to go through the deployment system.

The path became:

1. edit code or risk limits in source control
2. push the change
3. let ArgoCD sync the infrastructure state
4. restart the pod with the new mounted file

That is slower than letting an agent rewrite its own runtime script.

That is the point.

Some changes should be slow. Risk limits are one of them.

The agent can still adapt inside the box. It can change orders, update inventory, record observations, tune runtime decisions, and preserve memory. It just cannot rewrite the code that defines the box while it is standing inside it.

## Immutable does not mean frozen

The broader lesson is not that everything should be read-only.

Useful agents need mutable state. They need memory. They need scratch space. They need queues, logs, checkpoints, and working directories. If every file is immutable, the agent is a demo with nowhere to live.

The trick is deciding which things are allowed to change at runtime.

For this system, the split is simple:

- code is immutable
- risk limits are immutable
- infrastructure configuration is immutable
- state is mutable
- memory is mutable
- logs are mutable
- market observations are mutable

That separation matters more than any individual implementation detail.

The agent should be able to learn from the world. It should not be able to edit the rules that constrain its actions in the world.

## This is an infrastructure problem

A lot of agent safety discussion lives at the model layer.

That layer matters. Better models make better decisions. Better prompts can reduce mistakes. Better evals can catch more failures before deployment.

But once an agent has tools, money, credentials, or production access, the surrounding system has to carry some of the safety burden.

Filesystem permissions matter.

Mount semantics matter.

Import order matters.

Deployment paths matter.

The boring primitives are where the boundary becomes real.

If the only thing stopping an agent from changing a risk limit is an instruction in the prompt, the system is depending on the least durable part of the stack.

## The shape I trust now

The shape I trust is structural separation.

Immutable things are managed through infrastructure as code. They move through source control, review, sync, and restart.

Mutable things live on persistent volumes. They can change continuously because that is where the agent does its actual work.

The interface between those two worlds should be explicit. The agent can observe immutable files. It can depend on them. It can fail loudly if they block an action.

But it cannot quietly replace them.

That one distinction changed how I think about agent systems.

The question is not "can the agent be trusted?"

The question is "what does the system require trust for?"

If the answer includes editing its own safety limits at runtime, the infrastructure is not done yet.
