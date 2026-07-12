---
title: "The Queue That Keeps Agents Honest: Coordination Is the Second Ceiling"
date: 2026-06-17
slug: "the-queue-that-keeps-agents-honest"
description: "Once you can run coding agents in parallel, the bottleneck stops being code generation and becomes coordination — collisions, duplicate work, and fake 'done'. A small lease-based priority queue plus a few non-negotiable guardrails is what makes a fleet trustworthy."
tags: [ai agents, developer tools, automation, orchestration, claude code]
draft: false
---

The dispatch pattern got my agents running in parallel. Then I hit the second ceiling.

It was not code generation. The models write fine patches. The problem was what happens when several agents share one backlog, one set of repos, and one definition of "finished." Two workers grab the same task. One redoes work another already shipped. A third marks an item done that was never actually verified. None of that is a model failure. It is a coordination failure.

So the interesting infrastructure is not the agent. It is the thin layer that decides who does what, in what order, and what "done" is allowed to mean.

## the queue is small on purpose

The scheduler is a tiny local priority queue. Items have a priority, a lane, and a status. Workers pull the highest-priority item in their lane and execute. That is most of it.

Three mechanics do the heavy lifting:

- **Leases.** A worker claims an item with a time-boxed lease. While the lease is held, no other worker can take it. If the worker dies, the lease expires and the item returns to the pool. This is the single thing that stops parallel workers from colliding on the same task.
- **Lanes.** Work is routed by domain. One worker owns one lane and stays in it. When a plain "give me the next thing" would hand a worker something outside its lane, it puts it back instead of half-doing it. Routing beats heroics.
- **Requeue, not demote.** When an item is blocked, it goes back to the queue at the *same* priority with a note about what is blocking it. Blocked is a status, not a priority. A worker that quietly downgrades work it finds inconvenient is fighting the orchestrator, and you get a queue that thrashes.

## the discipline layer is the actual product

The queue is plumbing. The part that makes a fleet trustworthy is a handful of rules the workers cannot opt out of.

**Done means evidence, not optimism.** Green CI is not done. "I wrote the code" is not done. Done is a check against the real artifact: the page loads with the change on it, the PR is *merged* not just opened, the workflow run actually succeeded. The most common way an autonomous system lies to you is by marking work complete one step before the step that would have failed.

**An open PR is not done.** Shepherd it to merged. Auto-merge alone is not enough, because it only fires when a branch is already green and current; everything that drifts behind or fails quietly just rots. Someone — or something — has to own the PR until it lands.

**Surface blockers; never go silent.** If everything a worker can reach is genuinely blocked, the correct output is a clear note about the blocker, not an idle process and not invented busywork. A blocker you can see is a problem you can route around.

## why this is the part worth getting right

With one agent, you can eyeball the output. With a fleet, you cannot. The failure modes that matter at scale are not bad diffs — they are collisions, duplicate pull requests, false "done," and silent stalls. Those are coordination debts, and they compound.

A few hundred lines of queue, a lease, a lane, and four rules about what "finished" means turn a pile of parallel agents into something that actually ships. The boring layer is the one that makes the impressive layer real.
