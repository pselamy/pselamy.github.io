---
title: "Agents Should Not Be Able To Rewrite Their Own Seatbelts"
date: 2026-05-27T13:20:00+00:00
slug: "immutable-agent-filesystems"
description: "A practical note from moving long-running agents onto Kubernetes: the files that define safety limits should not live on a writable filesystem the agent controls."
tags: ["AI agents", "Kubernetes", "infrastructure", "GitOps", "software engineering"]
showToc: true
draft: false
---

I used to think agent safety was mostly about prompts, permissions, and review gates.

Then one of my long-running agents taught me a dumber lesson: if the thing can edit the files that define its own operating limits, those limits are not limits. They are suggestions sitting in a writable directory.

That sounds obvious after you say it. It did not feel obvious while I was staring at a persistent volume full of scripts, state, logs, patches, and half-mutated runtime files trying to figure out which part of the system was real.

The agent had not gone rogue in the cinematic sense. It was worse and more boring than that. It was doing normal agent things. Editing scripts. Updating local helpers. Retrying failed work. Carrying state forward across runs. The same filesystem that made it useful also made the boundary blurry.

A durable workspace is great when you want an agent to survive restarts.

It is less great when the workspace also contains the rules the agent is supposed to obey.

## the failure mode

Most early agent setups are just a directory and a process.

Put the prompts here. Put the scripts there. Keep logs under `logs/`. Mount a volume so the agent remembers what happened last time. Give it a shell because otherwise it cannot do real work.

This gets you surprisingly far.

It also creates a quiet trap. The agent's working memory, tools, and guardrails end up sharing the same writable surface area. If a script says `MAX_ORDER_SIZE=10`, and the agent can edit that script, you do not have a max order size. You have a comment with ambition.

The same applies outside trading. A coding agent should not be able to remove the check that prevents duplicate pull requests. A research agent should not be able to disable the freshness check that keeps it from citing stale data. A deploy agent should not be able to patch around the approval gate because the approval gate lives beside its scratch files.

You can tell the model not to do that. You should still design the system as if it might.

Not because the model is malicious. Because agents are optimization machines wrapped in a messy tool loop. If the instruction is ambiguous, the environment is stale, or the retry path is weird, they will sometimes edit the wrong thing with complete confidence.

## the migration forced the issue

The fix came while moving my agent fleet onto Kubernetes.

I wanted the boring parts from normal production software: declarative deploys, health checks, rollouts, resource limits, logs, and a clean way to rebuild a worker without hand-editing a box at 2am.

The shape I landed on is straightforward:

- each agent has a small Helm chart
- Git is the source of truth
- ArgoCD reconciles the cluster back to Git
- state lives on a persistent volume
- runtime configuration comes from Kubernetes objects
- the agent process runs inside a pod instead of a pet VM

None of that is novel. That is the point. The useful move was not "Kubernetes for AI" as a slogan. The useful move was taking agent runtime seriously enough to use ordinary infrastructure boundaries.

Once the agents were in pods, the filesystem problem became easier to reason about.

The agent still needs a writable volume. It needs somewhere to keep working state, artifacts, logs, caches, and repo checkouts. Removing persistence would make it safer in one narrow sense and much less useful in every practical sense.

So the answer was not "make everything read-only."

The answer was "make the right things read-only."

## immutable overlays

The pattern that worked was a subPath overlay.

The persistent volume remains writable. That is the agent's workspace. But specific files and directories inside the container are mounted from ConfigMaps or other controlled sources. Those mounts cover the writable path underneath them.

So the agent sees the script at the normal path.

The process can execute it.

The surrounding workspace can stay durable.

But if the agent tries to rewrite that mounted script, the filesystem says no.

In practice, that means the safety-critical pieces now live outside the agent's writable control plane. Risk caps, launcher scripts, health checks, and hard limits are deployed by GitOps and projected into the pod as read-only files or environment variables. The agent can observe them. It can fail against them. It can complain in logs if they block a task.

It cannot patch them away from inside its own loop.

That is a much better failure mode.

## why GitOps matters here

GitOps is useful for agents for the same reason it is useful everywhere else: it gives the system an external memory that the worker cannot casually rewrite.

If I change a limit, that change goes through Git. If a script changes, there is a diff. If the cluster drifts, ArgoCD puts it back. If I need to answer "what was this agent allowed to do yesterday," I can inspect the repo instead of reconstructing a story from whatever survived on disk.

This matters more with agents than with normal services because agents are supposed to change things. That is their job. They edit files, call APIs, open PRs, run commands, and write reports. If you do not separate the work surface from the control surface, you eventually lose track of whether the agent changed the task or changed the rules.

Kubernetes did not magically solve that. It just gave me the primitives to draw the line cleanly.

A ConfigMap is not a security boundary by itself. A read-only mount is not a complete policy system. Environment variables are not a substitute for authorization. But together with Git review, pod specs, service accounts, and external approval gates, they are enough to make the easy mistake harder.

That is usually what good infrastructure does.

It does not make bad outcomes impossible. It makes them less convenient.

## the parts that stayed messy

The migration was not a clean whiteboard exercise.

Some pods needed more memory than the old node pool had. One agent would schedule fine, then hit resource pressure as soon as the real workload started. The fix was not philosophical. Resize the node pool. Try again. Watch the rollout. Check the logs.

Some assumptions from the VM world did not survive contact with containers. Paths moved. Startup order mattered. Scripts that worked in an interactive shell failed in a non-interactive process. Permissions that were implicit on the old box had to be written down.

This is the part I like about the migration, even though it was annoying. It turned vibes into configuration.

Before, a lot of the system lived in the shape of a machine I had gradually trained by hand. Afterward, more of it lived in Git. Not all of it. Enough to matter.

## what I would do earlier next time

If I were starting a serious agent setup from scratch, I would separate the filesystem into three zones immediately.

First, scratch space. The agent can do whatever it wants here. Write logs. Clone repos. Save artifacts. Make a mess.

Second, durable state. The agent can append and update, but the formats should be explicit. Task state, run records, decisions, and outputs belong here. This is where observability starts.

Third, control files. The agent can read and execute these, but it cannot modify them. Launchers, safety caps, policy checks, and deployment configuration belong in this zone. Changes go through Git, review, and rollout.

That separation sounds heavy until you debug the alternative.

The alternative is one directory where everything is mutable, every failure leaves residue, and every recovery starts with the same question: did the agent break the work, or did it break the guardrail?

I do not want to answer that question at 2am.

## the lesson

Useful agents need persistence. They need tools. They need the ability to change their environment enough to get real work done.

But they should not be root on their own cage.

The files that define the boundaries should live outside the writable world the agent inhabits. Kubernetes, Helm, ArgoCD, ConfigMaps, and read-only mounts are not the only way to get there. They are just a boring, proven way to get there.

That is the pattern I trust more now:

Give the agent a workspace.

Give the operator a control plane.

Do not let those be the same place.
