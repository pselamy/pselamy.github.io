---
title: "Reading Code You Didn't Write"
date: 2026-04-08T12:00:00-04:00
slug: "reading-code-you-didnt-write"
description: "How to use Claude Code as a codebase navigator."
tags: ["claude-code", "developer-tools", "ai-assisted-development", "tutorial"]
showToc: true
draft: false
---

You've been handed a codebase. Maybe it's your first week at a new job. Maybe you inherited a service from a team that no longer exists. Maybe you're contributing to an open source project for the first time. Either way, you're staring at thousands of files written by people who aren't around to explain them.

Reading unfamiliar code is one of the most common activities in software engineering, and one of the least taught. Most developers develop their own coping strategies — grep around, find `main()`, start clicking through imports. It works eventually, but it's slow and you miss things.

Claude Code changes the economics of this problem. Instead of navigating alone, you have a tool that can read, search, and reason about the entire codebase alongside you. This post walks through how I use it to get oriented in unfamiliar code.

## The problem with reading code alone

When you read code by yourself, you're trying to answer two very different kinds of questions at the same time.

**Structural questions** are about the shape of the codebase. Where are the entry points? What calls what? How are modules organized? These questions have concrete, mechanical answers that live in the file tree, import graphs, and function signatures.

**Meaning questions** are about intent. Why is this function structured this way? What invariant does this check protect? Why does this module exist separately from that one? These answers often live outside the code — in commit messages, design docs, or the heads of people who have left.

The problem with reading code alone is that you're constantly switching between these two modes. You open a file to understand what it does, but you can't make sense of it without knowing where it sits in the larger structure. You zoom out to understand the structure, but you lose track of the specific question you were trying to answer.

Claude Code helps because you can offload the structural questions entirely. Ask it to find every caller of a function, trace a data flow, or explain a module's public API, and you free yourself to focus on the meaning questions that actually require human judgment.

## Start with a map

Before diving into any specific file, ask for a structural overview. This is the single highest-value prompt you can run on an unfamiliar codebase.

```text
Give me a structural overview of this codebase. What are the main
modules, where are the entry points, and what are the most central
files (files that the most other files depend on)?
```

Claude Code will read through the directory structure, scan imports, and give you a map. It won't be perfect, but it gives you something critical: **orientation**. You know where to start looking and what the major boundaries are.

The "centrality" part matters. In most codebases, a small number of files are imported by everything else — shared types, utility modules, core domain models. These central files are the best starting point because changes to them ripple everywhere. Understanding them first gives you leverage.

Once you have the map, save it. Write it down in a doc, or better yet, start a `CLAUDE.md` file. You'll build on it as you explore.

## Trace a path, not a file

Reading files in isolation is like reading a dictionary to learn a language. You need to follow a path — a complete flow through the system — to understand how pieces connect.

Pick a concrete user-visible behavior and trace it end to end. For example:

```text
Trace what happens when a user submits the login form. Start from
the form component and follow the flow through to where the session
cookie gets set. Show me each file and function along the way.
```

This gives you a thread to pull. Instead of reading modules in whatever order they appear in the file tree, you see them in the order they actually execute. You understand not just what each piece does, but why it exists — because you can see it in the context of a real flow.

Good paths to trace first:

- The main user-facing action (login, submit, purchase)
- The critical data path (how data enters the system and where it ends up)
- The error path (what happens when something fails)

Each path you trace fills in more of your mental model. After three or four paths, you'll have a working understanding of most of the codebase.

## Use Plan Mode for exploration

Claude Code has a Plan Mode (activated with Shift+Tab) that's specifically designed for exploration. In Plan Mode, Claude reads and reasons about code but doesn't make any changes. No files get edited, no commands get run. It's pure exploration with no side effects.

This is exactly what you want when you're still getting oriented. You can ask ambitious questions without worrying about accidentally modifying something:

```text
[Plan Mode] How does the authentication middleware work? What are
the different auth strategies supported and where are they configured?
```

Plan Mode is also useful for validating your understanding. Once you think you know how something works, describe your mental model and ask Claude to check it:

```text
[Plan Mode] I think the event system works like this: producers
write to a Kafka topic, the consumer service polls and dispatches
to handlers based on event type, and handlers are registered in
handlers/registry.ts. Is that right? What am I missing?
```

This kind of back-and-forth would take hours with just grep and file reading. With Plan Mode, you can iterate on your understanding in minutes.

## Git history is documentation

The commit log is one of the most underused sources of information in any codebase. It tells you not just what the code does now, but how it got there — what was added, what was removed, what was refactored and why.

Claude Code can read git history and make sense of it:

```text
Show me the git history for PaymentProcessor.ts. Summarize the
major changes and what motivated them based on the commit messages.
```

This is especially valuable for code that looks strange. If a function has an odd structure or an unexpected edge case, the commit that introduced it often explains why. Instead of guessing at intent, you can see the actual decision trail.

You can also use git history to understand team dynamics — who owns what, how frequently different parts of the codebase change, and where the active development is happening:

```text
Which files in the src/api/ directory have changed the most in
the last 3 months? Who are the main contributors?
```

This tells you where to focus your attention and who to ask questions when you do need a human explanation.

## Build a CLAUDE.md while you explore

As you learn about the codebase, encode what you learn into a `CLAUDE.md` file in the repo root. This file serves as context for Claude Code — it reads it at the start of every conversation — so anything you put there makes future sessions more productive.

A good exploration-phase `CLAUDE.md` includes:

- **Entry points**: Where the application starts, what kicks off processing
- **Key paths**: The important flows you've traced (authentication, data pipeline, request handling)
- **Conventions**: Patterns you've noticed (how errors are handled, where config lives, naming conventions)
- **Architecture boundaries**: What the major modules are and how they relate to each other
- **Gotchas**: Surprising things you've discovered (implicit dependencies, non-obvious environment requirements)

You don't need to write this all at once. Add to it as you explore. Each session, you'll understand more, and the `CLAUDE.md` grows to reflect that understanding.

The key insight is that exploration isn't wasted work if you capture what you learn. The `CLAUDE.md` becomes a persistent artifact that makes every future session — yours or anyone else's — start from a higher baseline.

## What you can do now

After working through a codebase with these techniques, you should be able to:

- **Navigate confidently**: Know where to look for any given behavior without searching randomly
- **Trace any flow**: Follow a user action from entry point to side effect, understanding each step
- **Read with context**: Understand why code is structured the way it is, not just what it does
- **Onboard others**: Share your `CLAUDE.md` and traced paths so the next person starts further ahead
- **Contribute safely**: Make changes with an understanding of what depends on what, reducing the risk of unintended breakage

The underlying principle is simple: don't try to read a codebase. Explore it with a tool that can handle the structural questions while you focus on building understanding. Claude Code won't replace the need to think carefully about unfamiliar code, but it removes the mechanical bottleneck that makes reading code so slow.

For more techniques on working effectively with Claude Code, see Anthropic's [Best Practices for Claude Code](https://anthropic.com/engineering/claude-code-best-practices).
