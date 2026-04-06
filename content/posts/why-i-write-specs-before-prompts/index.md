---
title: "Why I Write Specs Before Prompts"
date: 2026-04-06T01:19:00Z
slug: "why-i-write-specs-before-prompts"
description: "Prompts are requests. Specs are coordination systems. If you want reliable output from AI agents, start with the spec."
tags:
  - ai-agents
  - specs
  - software-engineering
  - claude-code
  - developer-tools
draft: false
---

If you want reliable work from AI systems, the spec matters more than the prompt.

A prompt is a request. A spec is shared reality.

That distinction changed how I build.

Most AI coding advice obsesses over prompts. Wording. context size. model quirks. That matters a little. It matters less than having a clear unit of work.

The bottleneck is usually not model intelligence. It is ambiguity.

A weak prompt can still work on a small task with a strong reviewer. But once work spans multiple files, tools, sessions, or handoffs, prompts get lossy fast. The agent improvises. The human re-explains. Review slows down. Rework stacks up.

I do not start serious work with prompts anymore. I start with specs.

## Prompts are too lossy

A prompt is good at saying "do this next."

It is bad at preserving intent over time.

That becomes obvious the moment work leaves the first session. The original reasoning is gone. Constraints get half remembered. Edge cases disappear. The next person, or the next agent, has to reconstruct the task.

This is fine for toy work. It is expensive for real systems.

A lot of what people blame on agents is really spec debt. The model is not failing because it cannot write code. It is failing because the work was never shaped well enough to execute cleanly.

## Specs survive handoffs

A useful spec does a few simple things:

- defines the problem
- names the desired outcome
- lists constraints
- points to interfaces and dependencies
- states how success will be checked
- calls out failure modes or rollback conditions

That is not bureaucracy. It is compression.

A good spec lets a human and an agent see the same task the same way. It reduces short-term memory load and narrows the space for bad interpretation.

It also makes review faster. I do not want to infer the goal from the diff. I want the goal to be explicit before the diff exists. Then review becomes a cleaner question: did the implementation satisfy the spec, or not?

## What changed in practice

In my own workflow, the spec is now the dispatchable artifact.

The prompt still exists, but it sits downstream of the spec.

A typical path looks like this:

1. Write the problem and scope.
2. Add constraints, affected systems, and acceptance checks.
3. Break that into a task that can be assigned cleanly.
4. Let the agent execute.
5. Review against the original spec, not against vibes.

That one change cuts a lot of thrash.

Agents move faster because they have clearer boundaries. Review moves faster because intent is visible. Parallel work gets easier because each task has a stable definition.

It also makes failure less mysterious. If an agent misses, I can usually see whether the issue was execution quality or task definition. Without a spec, those two failures blur together.

## Benchmarks measure capability, production needs coordination

This is part of why benchmark results and production reality often feel misaligned.

A strong model can do well on scoped software tasks and still struggle inside a messy operating environment. The missing layer is often not raw capability. It is coordination.

OpenAI's SWE-Lancer is a good example of why this distinction matters. It evaluates models on real freelance-style software work rather than synthetic toy problems, which is directionally useful. But even when model capability rises, production systems still need routing, memory, constraints, verification, and rollback paths.

Source: <https://openai.com/index/swe-lancer/>

That is why I think "prompt engineering" is the wrong abstraction for serious build systems. The deeper problem is work definition.

## A simple spec template

If you want a lightweight starting point, this is enough:

```md
# Task
One paragraph on the problem to solve.

# Goal
What should be true when this is done?

# Constraints
What must not happen? What boundaries matter?

# Interfaces
Files, services, APIs, owners, dependencies.

# Acceptance
What checks prove this worked?

# Failure plan
What should happen if rollout fails?
```

You can make this richer later. You do not need to start richer.

The point is to create a durable contract before execution begins.

If you have already read [The Dispatch Pattern](/posts/the-dispatch-pattern/), this is the layer that sits upstream of it. Dispatch helps me route execution. Specs make the work legible before execution starts.

## The prompt is downstream

I still use prompts constantly.

I just do not confuse them for the system.

The prompt is how I talk to the agent in the moment. The spec is how I make the work legible across time, tools, and reviewers.

That difference matters more as soon as the work gets real. If the [Dispatch Pattern](/posts/the-dispatch-pattern/) is about execution at scale, this is about defining work well enough that execution can succeed.

Teams that treat specs as first-class coordination objects will get better results from both humans and agents.

The prompt is a request. The spec is the system.
