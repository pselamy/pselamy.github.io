---
title: "Highly Effective Agents on My Team"
date: 2026-05-27T18:30:00-04:00
slug: "highly-effective-agents"
description: "The agents that became useful were not general chatbots. They got names, jobs, permissions, memory, and real responsibility."
tags: ["AI agents", "automation", "software engineering", "personal systems"]
showToc: true
draft: false
---

I started with scripts.

Little automations. Cron jobs. Shell commands wrapped around tasks I was tired of repeating. Check this inbox. Run that test. Poll this endpoint. Save that result somewhere durable.

That is a fine place to start. Scripts are honest. They either run or they do not.

The weird part came later, when some of those scripts grew enough state, context, and tools that they stopped feeling like scripts. They started feeling like narrow teammates.

Not people. Not magic. Systems with jobs.

That distinction has become important. A chatbot waits for a prompt. A useful agent owns a lane. It has context, permissions, memory, and a way to report back when something changes.

The jump was not from manual work to full automation. The jump was from one-off assistance to delegated responsibility.

## the good ones are not generalists

The agents that work best in my setup are specialized.

Nolan ships software. Nash trades. Reeve manages the career pipeline. Reid watches finances. Forge, Axel, Sable, and a few others exist around the edges, but the core pattern is easiest to see in the agents that carry real responsibility.

I do not want one giant assistant with access to everything.

I want narrow systems that are good enough in their lanes that I can stop carrying all the state myself.

That means each agent gets a smaller world: a purpose, a tool set, durable notes, explicit permissions, and a clear point where autonomy stops.

Small world. Deep context. Hard boundary.

That is the pattern.

## Nolan ships software

Nolan is the strongest example.

The job is software delivery on a real product repo. Strict types. Strict CI. Branch protection. Real pull requests. Real failures. The repo does not care that a model wrote the patch. It either builds or it does not.

Nolan owns the product roadmap at the task level. It can turn requirements into branches, run autonomous bug-hunt loops, open PRs, and keep iterating until the checks pass or the task needs escalation.

On a good day, that is 10 or more PRs.

The number is fun, but the more important part is the operating model. Nolan is not sitting in a blank chat box generating code snippets. It works inside a delivery loop:

- pick up scoped work
- create a branch
- make the change
- run the checks
- inspect failures
- patch again
- open or update the PR
- leave an artifact I can review

That last part matters. The output is not a claim. It is a diff, a test result, and a PR thread.

I can inspect it. I can reject it. I can ask for another pass. The agent does not ask me to believe in autonomy. It gives me artifacts.

The messy parts are still there. CI flakes. Branches go stale. A bug hunt finds three small issues and one false positive. Sometimes the agent gets stuck on an error that a human would recognize in ten seconds.

But those failures are inside the system now. They become state. They become retries. They become better prompts, better checks, or smaller task boundaries.

That is what made Nolan useful: not perfect code generation, but continuous delivery with enough structure around it to survive mistakes.

## Nash trades real capital

Nash is a different kind of pressure test.

It trades on Kalshi with real money. Not a huge account. Enough to make the consequences real.

That changes the design immediately.

A bad code patch can be reverted. A bad trade can settle against you. The system needs hard limits, immutable risk guards, position tracking, reconciliation, and boring records of what happened.

Nash has placed more than a hundred fills. Some markets settled well. Some did not. The early P&L was not the interesting part. The interesting part was watching the loop become real:

- read markets
- decide whether there is an edge
- place bounded orders
- reconcile fills
- track positions
- stop at limits

The hardest lesson was about authority.

A trading agent should never be able to rewrite the rules that bound its own risk. The risk caps belong outside the writable workspace. The agent can read them, report on them, and stop when it hits them. It cannot casually edit them while doing unrelated work.

That is the kind of boundary that turns an experiment into a system.

Nash did not make me more confident because it was clever. It made me more confident when the infrastructure got boring: immutable caps, durable logs, clear stop conditions, and enough observability to know whether it was active, stuck, or done.

Real stakes force real engineering.

## Reeve keeps the career pipeline sane

Career work is a surprisingly good agent test because it is high-context and socially expensive.

A recruiter message is not just a message. It depends on the latest resume, previous replies, verified facts, existing referrals, scheduling constraints, and whether the right answer is a warm note, a direct answer, or silence.

Reeve owns that lane.

The useful part is not drafting a polite paragraph. Any model can do that. The useful part is maintaining the pipeline: who reached out, what they asked for, what has already been sent, which roles are active, what facts are safe to use, and what still needs approval.

The lane crosses multiple systems. Professional inboxes. Email. Job docs. Resume versions. Notes from calls. A thread can go stale because one detail is missing, or because I already replied somewhere else and forgot.

Reeve is quiet, but that is why it works.

It triages. It researches. It drafts. It flags what needs a decision. It updates the record so I am not reconstructing the whole story from memory every time someone follows up.

Outbound messages still need approval.

That is not a weakness. That is the trust boundary. Reeve can do the expensive prep work, but I still own the relationship.

## Reid watches the boring money stuff

Reid is even less glamorous.

The job is financial monitoring. Watch reports. Track obligations. Keep the LLC accounting picture from turning into a shoebox of delayed context. Notice when something changes and summarize it before it becomes urgent.

This is exactly the kind of work humans neglect.

Not because it is hard. Because it is repetitive, low-drama, and easy to postpone until the cost of forgetting gets high.

A good finance agent should not narrate every tiny movement. That becomes spam. It also should not wait until something is on fire.

So the problem is mostly threshold design.

What changed? Is it expected? Does it affect cash, credit, taxes, or obligations? Does it need action now, or should it just update the record?

Reid is reliable because the scope is boring. That is a compliment.

## the rest of the bench

There are other agents around the edges.

Forge handles build-shaped work. Axel handles ops-shaped work. Sable helps with infrastructure and support tasks. They matter, but they are not the center of the lesson yet.

The center is Nolan, Nash, Reeve, and Reid because their work has consequences.

Code merges. Trades settle. Career threads move or stall. Finance details compound quietly.

Once an agent touches work like that, the design stops being about clever prompts. It becomes permission design, state management, escalation, and auditability.

## autonomy stops at different places

Each lane has a different trust boundary.

Nolan can push branches and open PRs. That is safe because PRs are inspectable and gated by CI.

Nash can trade, but only inside immutable caps. The autonomy exists inside the risk box.

Reeve can prepare career replies and track the pipeline, but external messages need approval.

Reid can monitor and summarize, but should not move money.

That is the part I keep coming back to. Effective agents are not defined by how autonomous they are in the abstract. They are defined by exactly where autonomy stops.

A useful agent is not one that can do anything.

It is one that knows its lane well enough to act inside it and stop at the boundary.

## context is the next trust frontier

The next frontier is not more personality.

It is more situational awareness.

Calendar access is the obvious next step for Reeve. Read-only at first. That sounds small until you look at how much coordination depends on schedule context.

Finding open slots. Proposing times. Avoiding conflicts. Knowing whether a call already happened. Not drafting a booking reply after I already booked the meeting. Preparing notes before a screen instead of after the fact.

That is not about giving an agent control of my calendar.

It is about giving the agent enough context to stop making dumb suggestions.

Read-only context is a different trust level from write access. It lets an agent coordinate on my behalf without giving it power to commit me to anything.

That feels like the right progression:

1. more awareness
2. better suggestions
3. bounded actions
4. approval before anything socially or financially costly

Contacts and preferences fit the same pattern. An agent that knows my schedule, communication style, current obligations, and active projects can coordinate much better than one that only sees the last message.

Full situational awareness does not mean full authority.

It means fewer blind spots.

## delegation is different from automation

At first, I thought about agents as automation.

Take a task I do manually. Make the model do it. Save time.

That is useful, but it is not the interesting part anymore.

The better frame is delegation.

Delegation requires a role, context, expectations, feedback, and trust. It also requires knowing what not to delegate.

That maps cleanly onto specialized agents.

Nolan gets software delivery. Nash gets bounded trading. Reeve gets career pipeline work. Reid gets finance monitoring. Each one has a job, a memory, a tool set, and a boundary.

That is much more useful than a general assistant trying to be good at everything.

## where this is going

I do not think the end state is agents replacing all the work.

The useful version is more specific and more mundane.

Agents keep state warm. They watch for changes. They prepare decisions. They execute bounded actions. They leave trails. They ask for approval when the action crosses a trust boundary.

That is enough to change the shape of a day.

A software lane keeps moving while I am elsewhere. A trading lane follows rules without me staring at markets. A career lane remembers every thread. A finance lane notices what I would otherwise check too late.

None of that requires pretending agents are people.

It does require treating them like systems with jobs.
