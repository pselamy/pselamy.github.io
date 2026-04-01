---
title: "The Dispatch Pattern: How I Shipped 25 PRs in One Night Without Touching the Code"
date: 2026-04-01
slug: "the-dispatch-pattern"
description: "A practical pattern for running parallel coding agents across isolated environments, with isolated workspaces, failure detection, and guardrails that make multi-project execution usable."
tags: [ai agents, developer tools, automation, claude code, git]
draft: false
---

I kept hitting the same ceiling.

One repo was manageable. Two was annoying. Three or four active codebases meant my time disappeared into context switching. Open a branch. restate the task. wait for CI. switch repos. lose the thread. repeat.

So I stopped trying to code faster and built a dispatch layer instead.

The core idea is simple: one orchestrator assigns work, isolated coding agents execute it in parallel, and the system treats failures as normal operating conditions.

That pattern let me ship roughly 25 PRs in a single evening session across multiple projects. I did not write the implementation code by hand. I wrote prompts, set constraints, watched the failure modes, and fixed the system until it became usable.

This post is the pattern that emerged.

## the problem was not code generation

Most agent demos break on the wrong bottleneck.

The hard part is not getting a model to write a patch. The hard part is running many patches, across many repos, without credential leaks, branch collisions, duplicate PRs, or silent crashes.

If an agent can run shell commands, then orchestration becomes a systems problem:

- identity isolation

- repo isolation

- concurrency control

- crash detection

- deduplication

- clean handoff between planner and executor

That is the dispatch pattern.

## the architecture

I ended up with five pieces.

### 1. one linux user per trust boundary

Each project boundary gets its own Linux user.

That user has its own Git config, tokens, SSH setup, and local checkout. The orchestrator does not hold project credentials directly. It dispatches work into the target user context.

This matters for the same reason role separation matters anywhere else: if one task goes weird, the blast radius stays local.

I also use SSH restrictions aggressively. OpenSSH supports forced commands and source restrictions in , which is exactly the kind of primitive you want when an agent is allowed to operate through a proxy. The official docs are worth reading if you are building anything similar: <https://man.openbsd.org/sshd#AUTHORIZED_KEYS_FILE_FORMAT>

### 2. one workspace per task

Parallel agents cannot safely share a working directory.

Every dispatched task gets its own isolated workspace. That gives each run an isolated filesystem view with a dedicated branch, while still sharing the underlying repository objects.

This is one of the highest leverage parts of the system. Without it, parallel execution turns into branch contention and dirty-workspace cleanup.

Git workspaces are built for this use case and are much better than trying to fake isolation with repeated clone-and-delete loops: <https://git-scm.com/docs/git->

### 3. prompt to file, not prompt through five shells

At first I tried to pass prompts through nested shells.

SSH into a host. start tmux. invoke a shell. pass a multi-line prompt. include YAML or JSON. pray.

That path is a quoting trap.

The fix was boring and effective: write the prompt to a file, then launch the agent against that file.

That removed a whole class of breakage:

- shell escaping bugs

- broken heredocs

- prompts mangled by guardrails

- impossible debugging when a single quote disappears somewhere in the stack

If your agent runner is more than one shell hop away from the caller, prompt-to-file should probably be your default.

### 4. a loop that assumes tasks will fail

Headless agent execution is the primitive. Anthropic documents the non-interactive Claude Code flow directly: <https://docs.anthropic.com/en/docs/claude-code/cli-usage>

But one call is not enough.

Real work stalls. tools crash. CI flakes. a task gets 80 percent done and needs another pass with better context.

So each task runs inside a simple loop:

1. create isolated task context

2. run the coding agent

3. inspect output and repo state

4. stop early if the success markers are there

5. otherwise feed back the new state and iterate

That loop matters more than the model choice. Good orchestration beats one-shot prompting.

### 5. a scheduler that fills open slots

Parallelism should be controlled, not accidental.

I use a slot-based model. Each user has a maximum concurrency setting. The dispatcher looks for open slots and fills them. If a task crashes, the slot becomes available again.

The important part is not the exact scheduler. The important part is making concurrency explicit.

If you do not do that, you do not have a system. You have a pile of background processes.

## what actually made it work

The first version was fragile. The useful version came from fixing a few recurring failures.

### duplicate PRs

A looped agent will happily create a second PR if you ask it to continue a task without telling it a PR already exists.

So I added a guard: before PR creation, check task state for an existing PR artifact and block duplicates.

This sounds small. It is not. Duplicate PRs destroy trust in the whole setup.

### silent crashes

Some tasks looked alive in state files but the underlying session had already died.

The fix was to cross-check process reality against recorded status. If the session is gone but the task claims it is still running, mark it crashed and free the slot.

Any long-running agent system needs this. State files lie. Processes tell the truth.

### missing setup

A dispatch is worthless if the target environment is missing the repo, branch setup, or login context.

So I added pre-flight checks before scheduling work:

- repo exists

- workspace can be created

- login is valid

- required tools are available

This prevented a lot of fake starts.

### shell environment drift

Non-interactive shells do not always load the same environment as an interactive login.

That broke auth in subtle ways.

The fix was to standardize command execution so the environment is loaded consistently before the agent starts.

Again, boring fix. High leverage.

## results worth caring about

The dispatch pattern became interesting once it stopped being a toy.

The strongest numbers I have from the logged sessions:

- roughly 25 PRs merged in one evening session across three active project lanes

- more than 50 PRs merged across the tracked autonomous sessions

- up to 11 parallel agent sessions running at once

Those numbers are not a claim of full autonomy.

I still had to orchestrate the work, inspect failures, and improve the system between runs. That is the point. Useful agent systems are not magic. They are operational.

## what this changed for me

The biggest shift was mental.

I stopped thinking of coding agents as pair programmers and started treating them like workers in a constrained execution system.

That changes how you build around them.

You care less about perfect prompts and more about:

- what trust boundary this task should run inside

- how to isolate filesystem state

- how to detect failure early

- how to retry without duplication

- how to make every run inspectable after the fact

That framing has held up better than any model-specific trick.

## what I would build first if I were starting over

If you want to try this pattern, start here:

1. isolate credentials by environment or user

2. use isolated workspaces for parallel repo tasks

3. write prompts to files

4. make task state explicit and inspectable

5. add duplicate-action guards before you add more autonomy

6. detect crashed sessions before you optimize throughput

Do those six things and you have the beginnings of a real system.

Skip them and you are mostly running demos with shell access.

## closing

The interesting part of agent engineering is shifting away from chat and toward operations.

Once an agent can use a shell, your problems start to look like scheduler design, environment isolation, and failure recovery.

That is why I think the dispatch pattern matters.

Not because it makes coding disappear. It does not.

Because it turns agent work into something you can route, constrain, parallelize, inspect, and improve.
