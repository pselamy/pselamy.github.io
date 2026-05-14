---
title: "Agents Need Boring Infrastructure"
date: 2026-05-13T21:20:00-04:00
slug: "agents-need-boring-infrastructure"
description: "The hard part of agent systems is not getting a model to take an action. It is making that action safe, repeatable, inspectable, and useful over time."
tags: ["AI agents", "infrastructure", "software engineering", "automation"]
showToc: true
draft: false
---

Most agent demos start in the wrong place.

They show the model doing something impressive. It reads a ticket. It writes code. It opens a pull request. It passes a test. For a few minutes, it feels like the future arrived early.

Then you try to use the same idea in a real system.

The task gets interrupted. The model loses context. The test suite flakes. The branch goes stale. A token expires. A tool returns partial data. A dependency changes. The agent keeps retrying the wrong thing. Nobody knows whether it is stuck, still working, or about to break something expensive.

That is where the interesting work begins.

The hard part of agent systems is not getting a model to take an action. The hard part is making that action safe, repeatable, inspectable, and useful over time.

In practice, useful agents need boring infrastructure.

## They need queues

A real agent system needs a place for work to live. Tasks should have IDs, owners, states, timestamps, retries, and outcomes. Without that, every task is just a chat transcript with ambition.

Queues also create pressure control. Some work can run now. Some work should wait. Some work should never run twice. Some work should stop the moment a human changes the plan.

## They need state

An agent that cannot remember what it already tried is not autonomous. It is just expensive recursion.

State does not have to be fancy. It can be a database row, a file, a durable log, or a ticket comment. The important part is that the system can answer basic questions.

What did we ask it to do?
What did it try?
What changed?
What failed?
What is the next safe step?

If those answers only exist inside a model context window, the system is fragile.

## They need permissions

The safest agent is not the one that refuses to do anything. The safest agent is the one with a clear job, limited tools, and explicit boundaries.

A code agent should not have every credential. A research agent should not be able to deploy production. A writing agent should not be able to send external messages without review.

Good permission design makes agents more useful, not less. It lets them move fast inside a known box.

## They need observability

You cannot manage what you cannot see.

Agent systems need logs, heartbeats, progress markers, and failure reasons. Not because logs are exciting, but because silence is expensive.

If an agent is working on a pull request for twenty minutes, I want to know whether it is running tests, editing files, waiting on a tool, or stuck in a loop. If it fails, I want the failure to become input for the next attempt.

The goal is not perfect automation. The goal is low-noise automation that tells you when it needs help.

## They need approval gates

This is the part that gets skipped in demos.

Many actions should not be fully autonomous. Sending an email, publishing a post, changing production infrastructure, accepting a calendar invite, and applying to a job all need human judgment.

That does not make the agent less valuable. It makes the agent trustworthy.

A good agent can do the expensive prep work. It can gather context, draft the response, check the facts, run the tests, and present a clean decision. The human still owns the call.

## They need failure handling

Agents fail in weird ways.

Sometimes the model is wrong. Sometimes the tool is wrong. Sometimes the task is underspecified. Sometimes the environment changed. Sometimes the agent did exactly what it was told, and the instruction was bad.

The system has to treat failure as normal. That means retries with limits, circuit breakers, fallbacks, and clear escalation paths.

If the only recovery plan is "ask the model again," the system is not ready.

## They need boring product judgment

The best agent systems are not the ones that do the most. They are the ones that remove a real bottleneck.

Can it save a developer from context switching?
Can it keep a pull request moving?
Can it turn a messy thread into a clear action item?
Can it monitor something quietly and interrupt only when it matters?

Those are product questions before they are model questions.

The model matters, of course. Better models make more things possible. But the model is only one part of the system.

The rest looks like normal software engineering.

Queues. State. Permissions. Logs. Tests. Reviews. Rollbacks. Ownership. Documentation. Alerts. Interfaces that make the next step obvious.

That is the unglamorous foundation that makes agents useful.

I think this is why the next wave of AI engineering will look less like prompt hacking and more like systems work.

The winners will not just be the teams with the best demos. They will be the teams that can take messy, high-context work and make it reliable enough to trust.

That requires models.

It also requires boring infrastructure.
