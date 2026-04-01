---
title: "The Dispatch Pattern"
date: 2026-04-01T10:00:00-04:00
slug: "the-dispatch-pattern"
description: "A pattern for delegating self-contained units of work to autonomous AI coding agents — and the infrastructure that makes it reliable."
tags: ["ai", "automation", "architecture", "agents"]
showToc: true
draft: false
---

Most people using AI coding assistants work interactively. You type a prompt, read the output, adjust, repeat. It works, but it doesn't scale. You're still the bottleneck — every task waits for your attention.

The dispatch pattern changes this. Instead of conversing with an agent, you *dispatch* work to it: hand off a well-defined task, let the agent run autonomously, and collect the result as a pull request. You become a reviewer instead of a typist.

This post covers the pattern, the infrastructure it requires, and the failure modes I've run into while building it out.

## What the dispatch pattern looks like

The core idea is simple. You define a task as a structured specification — a JSON file, a ticket, a PRD — and hand it to an autonomous agent loop. The agent reads the spec, does the work, opens a PR, and stops. You review and merge.

A minimal dispatch has three components:

1. **A task spec** that defines what needs to be done and how to verify it
2. **An agent loop** that reads the spec, executes, and iterates until acceptance criteria are met
3. **A PR boundary** that captures the result and feeds it into your normal review workflow

The agent loop is the interesting part. Unlike a single-shot prompt, the loop lets the agent run quality checks, fix its own mistakes, and iterate toward a passing state. It's closer to how a developer actually works: write code, run tests, fix what's broken, repeat.

```text
┌─────────────┐     ┌──────────────────────────────────┐     ┌────────────┐
│  Task Spec  │────▶│  Agent Loop                      │────▶│  Pull      │
│  (PRD/JSON) │     │  read spec → implement → verify  │     │  Request   │
│             │     │       ▲            │              │     │            │
└─────────────┘     │       └────────────┘              │     └────────────┘
                    │       (iterate until pass)        │
                    └──────────────────────────────────┘
```

## Why dispatch over interactive use

Interactive AI coding is useful. I still use it for exploration, debugging, and one-off tasks. But dispatch is better for a specific class of work:

**Parallelism.** You can dispatch multiple tasks at once. While one agent writes a blog post, another refactors a module, and a third adds test coverage. Your throughput multiplies without multiplying your effort.

**Consistency.** A task spec with explicit acceptance criteria produces more predictable results than a freehand conversation. The spec becomes documentation of what you wanted and the PR shows what you got.

**Asynchronous workflow.** You don't need to babysit the agent. Dispatch a task, do something else, come back to a PR ready for review. This is especially valuable for tasks that are well-defined but tedious — the kind of work that drains your energy but doesn't actually need your judgment until the review stage.

**Auditability.** Every dispatched task has a spec, a branch, and a PR. You can trace what was requested, what was produced, and what was reviewed. That trail matters when you're moving fast.

## The task spec

The quality of your dispatch depends almost entirely on the quality of your task spec. A vague spec produces vague work. A precise spec with testable acceptance criteria produces code you can merge with confidence.

A good task spec includes:

- **What to build**, described concretely enough that there's no ambiguity about when it's done
- **Acceptance criteria** that the agent can verify programmatically — tests that pass, linters that clear, builds that succeed
- **Boundaries** on what the agent should and shouldn't touch

Here's a simplified example:

```json
{
  "description": "Add input validation to the signup endpoint",
  "acceptanceCriteria": [
    "Email field rejects invalid formats and returns 422",
    "Password field enforces minimum 8 characters",
    "All new validation paths have unit tests",
    "Existing tests still pass"
  ],
  "constraints": [
    "Only modify files in src/api/signup/",
    "Do not change the database schema"
  ]
}
```

The acceptance criteria are the key. They give the agent loop its termination condition: keep iterating until all criteria pass. Without them, the agent either stops too early or wanders.

## The agent loop

The loop reads the spec, plans an approach, implements it, and then runs verification. If verification fails, it reads the errors, adjusts, and tries again. Each iteration is a chance to self-correct.

The loop structure looks roughly like this:

```text
1. Read task spec
2. Check current state (git log, existing code)
3. Implement changes for the highest-priority incomplete criterion
4. Run quality checks (tests, linters, build)
5. If checks fail → read errors, fix, go to 4
6. If checks pass → mark criterion complete, go to 3
7. When all criteria pass → open PR, stop
```

A few design decisions matter here:

**One criterion at a time.** Having the agent tackle criteria sequentially reduces the blast radius of mistakes. If it breaks something, the error is localized to the current criterion.

**Checkpointing.** The agent should commit after completing each criterion. This gives you a clean git history and lets the agent resume if it gets interrupted. Context windows are finite — if the agent restarts, it can read git log and a progress file to understand what's already done.

**Bounded iterations.** Set a maximum iteration count. An agent stuck in an infinite fix loop is worse than one that stops and says "I got stuck here." The progress file should capture what went wrong so the next attempt starts with more context.

## Infrastructure requirements

The dispatch pattern needs more infrastructure than interactive use. Here's what I've found necessary:

### Branch isolation

Every dispatch gets its own branch. I use git worktrees so the agent operates on an isolated copy of the repo while the main checkout stays clean. This lets multiple dispatches run concurrently without stepping on each other.

```bash
git worktree add .worktrees/feature-name -b feature-branch main
```

### Quality gates

Automated quality gates are essential. The agent needs fast, deterministic signals about whether its work is correct. That means:

- Tests that cover the acceptance criteria
- Linters configured with clear rules
- A build step that catches compilation or rendering errors
- CI that runs on every push to the branch

Without these gates, you're relying on the agent's self-assessment, which is unreliable. The agent needs external verification.

### PR as the integration point

The pull request is where dispatch meets your existing workflow. The agent creates the PR, CI runs the quality gate, and you review the diff. This keeps humans in the loop at the right moment — after the tedious work is done but before anything merges to main.

Auto-merge with required CI checks works well here. If CI passes and the PR looks good, you approve once and it merges on green. No babysitting.

## Failure modes

I've watched enough dispatched tasks fail to have a taxonomy:

**Underspecified tasks.** If the spec is vague, the agent will produce something that technically satisfies the words but misses the intent. "Add a blog post about X" without guidance on tone, length, audience, or structure produces a generic post. The fix is always the same: make the spec more explicit.

**Missing quality gates.** If the agent can't verify its work programmatically, it'll declare victory too early. I've seen agents produce code that looks correct in the diff but fails at runtime because there were no tests to catch the error. Add tests before dispatching, not after.

**Context window exhaustion.** Long tasks can exhaust the agent's context window. Without checkpointing, the agent loses track of what it's done and starts repeating or contradicting itself. Progress files and git commits as checkpoints mitigate this — the agent reads its own trail to recover state.

**Scope creep.** Agents, like developers, will sometimes "improve" things you didn't ask them to touch. Explicit constraints in the spec help, but you still need to review the diff carefully. A dispatch is not a license to skip review.

**Cascading failures.** If the agent's first implementation attempt creates a mess, subsequent iterations may compound the mess instead of fixing it. Bounded iteration counts and clean checkpoints help — sometimes the best move is to reset and try a fresh approach.

## When to dispatch vs. when to stay interactive

Not every task benefits from dispatch. Here's my rough heuristic:

**Dispatch when:**

- The task is well-defined with clear completion criteria
- You can verify the result with automated checks
- The work is tedious but not ambiguous
- You have multiple such tasks and want parallelism

**Stay interactive when:**

- You're exploring a problem space and don't know what you want yet
- The task requires frequent judgment calls that depend on taste
- You need to iterate on the approach itself, not just the implementation
- The cost of a wrong result is high and hard to detect in review

The dispatch pattern works best when you've already made the hard decisions — what to build, how to structure it, what quality bar to hit — and you're delegating the execution.

## What I'm building toward

The dispatch pattern is a step toward a broader system where I can describe work at a higher level and have it decomposed, dispatched, and assembled automatically. The pieces are:

- A **planner** that breaks large tasks into dispatchable units
- A **dispatcher** that assigns each unit to an agent loop with the right context
- A **shepherd** that monitors running dispatches, handles failures, and merges results
- A **quality gate** that verifies the integrated result, not just individual pieces

I'm not there yet. Right now, I'm writing task specs by hand and dispatching one at a time. But each piece of infrastructure I add — worktree isolation, structured specs, automated quality gates — brings the full system closer.

The most important thing I've learned is that the pattern only works when the infrastructure is honest. Flaky tests, missing linters, vague specs — these all degrade dispatch reliability. The agent is only as good as the signals you give it.

If you're using AI coding tools interactively and hitting a ceiling on throughput, try dispatching a single well-defined task. Write a clear spec, set up a quality gate, and let the agent run. Review the PR. You'll quickly learn where your infrastructure gaps are — and closing those gaps makes everything else better too.
