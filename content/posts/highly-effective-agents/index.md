---
title: "Highly Effective Agents"
date: 2026-05-27T12:20:00-04:00
slug: "highly-effective-agents"
description: "The useful version of personal agent systems is not one general assistant. It is a team of specialized agents with isolated identities, bounded authority, and real responsibilities."
tags: ["AI agents", "Hermes", "automation", "personal infrastructure"]
showToc: true
draft: false
---

The first useful version was not a general assistant.

It was a specialist.

Then another specialist. Then another. Then enough of them that the shape stopped looking like automation scripts and started looking like a small operating team.

That distinction matters.

A generic agent can be impressive in a demo. It can summarize, draft, search, write code, call tools, and answer questions in the same voice.

But real work does not stay generic for very long.

Real work has context. It has stakes. It has recurring tasks, private preferences, calendars, credentials, repos, alerts, failure modes, and relationships. It needs memory in one place and hard boundaries in another.

The version that started working for me was a team of specialized agents, each with its own role, identity, domain, and authority.

## The software engineer

Nolan is the most competent one.

Nolan is a software engineer. Not in the cute demo sense where an agent writes a toy function and opens a pull request against a sandbox repo.

Nolan ships real changes.

On a good day, Nolan can ship 10 or more pull requests. The agent owns a product roadmap, takes scoped tasks, runs implementation loops, opens PRs, watches CI, reads failures, fixes bugs, and keeps going.

The important part is not the PR count. The important part is that the work survives contact with real CI.

That means the agent is dealing with the same annoying reality every engineer deals with:

- stale branches
- flaky tests
- missing environment setup
- broken assumptions
- review feedback
- half-fixed bugs that need another pass

The best Nolan loops are not one-shot code generation. They are autonomous bug hunts.

Start with a product surface. Let the agent explore it. Capture failures. Turn those failures into issues. Patch the code. Run the tests. Open the PR. Repeat.

That is the point where the system stops feeling like a chatbot and starts feeling like labor.

## The trading agent

Nash is different.

Nash runs a live trading strategy on Kalshi with real capital. Around $715 right now. Not life-changing money, but enough to make fake guardrails feel irresponsible.

That changes the design immediately.

A coding agent can create a bad PR. Annoying, but reversible.

A trading agent can lose money.

So Nash has to operate inside harder boundaries. It can make markets, track inventory, read market state, and adapt within its box. But the risk controls and trading code are enforced by immutable infrastructure.

That is not a prompt rule. It is a filesystem rule.

The agent gets mutable state where it needs mutable state. It gets read-only code and risk limits where mutation would be dangerous.

That separation is the only reason I am comfortable letting it run with real capital.

## The career steward

Reeve handles career operations.

The work is less flashy than code or trading, but it is exactly the kind of high-context coordination that benefits from a persistent specialist.

Recruiter messages need triage. Outreach needs drafts. Job leads need state. Follow-ups need timing. A pipeline needs to remember what happened last week, not ask me to reconstruct it every time.

The agent can read professional messages through APIs, maintain a job pipeline, draft responses, and prepare context before calls.

The boundary is simple: it can prepare and track, but it does not send external messages without approval.

That boundary makes the agent useful instead of risky.

The value is not that it can write a reply. The value is that it knows the thread, the resume, the target companies, the current stage, and the last thing I said I cared about.

## The financial agent

Reid handles personal finance operations.

This is another domain where the boring work compounds.

Credit reports need monitoring. LLC accounting needs attention. Recurring checks should happen whether I remember them or not.

Reid runs on a weekly schedule, checks the things it is supposed to check, and sends Telegram alerts when something needs attention.

That is not glamorous.

It is useful because it is persistent.

Most personal automation fails because it depends on the exact moment you remember to run the script. A financial agent should be the opposite. It should remember the rhythm of the work and interrupt only when there is something worth interrupting for.

## Specialization beats generalization

The lesson from all of this is that specialization beats generalization.

Not because a general model cannot do many tasks. It can.

Specialization wins because each domain needs different defaults.

A software agent should be aggressive about making changes in a repo and conservative about merging.

A trading agent should be adaptive about market behavior and conservative about risk boundaries.

A career agent should be proactive about preparation and conservative about outbound communication.

A financial agent should be quiet most of the time and loud when something crosses a threshold.

Those are not just different prompts. They are different operating contracts.

## Identity isolation is structural

The agents also need separate identities.

That sounds cosmetic until the system touches real tools.

Each agent has its own email, source-control identity, chat surface, API keys, credentials, memory, and schedule. The separation is not for branding. It is for blast radius.

If a software agent is working in source control, it should not also have the keys for financial monitoring.

If a career agent can read professional messages, it should not be able to place trades.

If a trading agent has market access, it should not be able to publish a blog post.

The identity boundary makes the permission boundary understandable.

It also makes debugging easier. When something happens, I can ask which agent did it, which credentials it had, and which domain boundary allowed the action.

That is much cleaner than one universal assistant with every key in the house.

## The platform is the commodity

The platform underneath this is Hermes.

That matters, but maybe not in the way people expect.

The platform provides the common substrate: memory, tools, schedules, message delivery, profiles, credentials, and long-running workflows.

But the value is not "an agent platform."

The value is the specialized operational layer on top of it.

Nolan is valuable because it knows how to ship software in my environment.

Nash is valuable because it understands the trading loop and lives inside real risk boundaries.

Reeve is valuable because it knows my career pipeline and communication rules.

Reid is valuable because it knows the cadence of financial monitoring.

The substrate should become boring. The specialization is where the leverage is.

## Real work changes the bar

Demos optimize for surprise.

Real work optimizes for trust.

That is a different bar.

A demo can be stateless. A working agent needs memory.

A demo can use one identity. A working agent needs scoped credentials.

A demo can fail silently. A working agent needs alerts and recovery paths.

A demo can take broad instructions. A working agent needs domain-specific rules and a way to know when to stop.

Once agents have real responsibilities, the question changes from "can it do the task?" to "can it keep doing the task without making me afraid of it?"

That is where most of the engineering lives.

## The next trust milestone

The next frontier is situational awareness.

I am adding read-only calendar access for Reeve.

That sounds small. It is not.

A calendar is one of the highest-signal context sources in a person's life. It tells an agent what is coming, what just happened, who is involved, when preparation matters, and when interruption is expensive.

Read-only access is the right first step.

The agent does not need to schedule meetings on its own to be useful. It can prepare briefs before calls, notice when a recruiter screen is coming up, connect a conversation to a pipeline entry, and remind me when a follow-up is timely.

That is a trust milestone.

Not because the tool is hard. Because the context is intimate.

An agent with calendar context is closer to coordinating on my behalf than one that only responds when summoned.

## The arc

The arc looks like this:

1. automation scripts
2. specialized agents
3. real responsibilities with real stakes
4. broader situational awareness

The first stage saves clicks.

The second stage saves context switching.

The third stage creates leverage.

The fourth stage starts to feel like delegation.

I do not think the future is one omniscient assistant doing everything through one chat box.

The version I trust is more like a small team. Specialized roles. Separate identities. Narrow authority. Persistent memory. Real tools. Clear boundaries.

Less magic.

More responsibility.

That is where the useful work starts.
