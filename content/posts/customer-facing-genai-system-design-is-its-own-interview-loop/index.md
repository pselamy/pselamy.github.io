---
title: "Customer-Facing GenAI System Design Is Its Own Interview Loop"
date: 2026-06-29T12:00:00-04:00
slug: "customer-facing-genai-system-design-interview-loop"
description: "A public course for preparing for customer-facing GenAI system design interviews: discovery, RAG, agents, evaluation, security, observability, troubleshooting, and field judgment."
tags:
  - genai
  - system-design
  - ai-agents
  - rag
  - field-engineering
series:
  - Customer-Facing GenAI Systems
showToc: true
draft: false
---

Most system design preparation is built around a familiar loop: design a feed, a chat system, a rate limiter, a file store, or a ticketing service. Those exercises are useful, but they do not fully prepare you for a newer kind of interview that is showing up around GenAI field engineering, customer engineering, solutions architecture, and applied AI product roles.

The shape is different.

The interviewer is not only asking whether you can decompose a backend system. They are asking whether you can walk into an ambiguous customer situation, discover what actually matters, choose the right AI pattern, explain the tradeoffs, protect the customer's data, evaluate answer quality, operate the system in production, and translate what you learn back into product feedback.

That is its own interview loop.

I built a public preparation course for it because the available prep material still feels thin. There is plenty of content about classic distributed systems. There is plenty of content about prompting. There is much less material about the middle layer where real GenAI systems live: enterprise knowledge, retrieval quality, tool calling, identity boundaries, observability, hallucination risk, customer trust, and cost.

The course is here:

- [Public course table of contents](https://docs.google.com/document/d/1akqNIetG4R5kpv9AdobaAZv9qqBShTmHpVG3B8IJcds/edit?tab=t.0)
- [NotebookLM master index](https://notebooklm.google.com/notebook/9fbca41e-c836-4484-9bda-34bec0bdfaba)

## The loop starts before architecture

The easy mistake is to jump straight to an architecture diagram.

"We need an AI assistant over internal docs" sounds like a RAG problem. It might be. But in a customer-facing interview, the first move should not be "vector database plus LLM." The first move should be discovery.

What kind of documents? Who owns them? How fresh are they? What access controls apply? Are answers expected to be factual summaries, recommendations, workflow actions, or draft responses? What happens if the assistant is wrong? Is the customer optimizing for accuracy, speed, cost, coverage, compliance, employee productivity, or some mixture of all six?

Those questions are not throat clearing. They determine the system.

If the customer's documents are highly permissioned, identity propagation and tenant isolation may dominate the architecture. If the documents are messy and duplicated, ingestion and retrieval quality may matter more than the model choice. If the system acts through tools, approval gates and audit trails may be more important than conversational polish. If wrong answers create legal or operational risk, the design needs evaluation, abstention, citations, and human review paths from the beginning.

A strong answer has an architecture, but it is not architecture-first. It is customer-first.

## The answer spine

The course is organized around a repeatable answer spine:

1. Clarify the customer situation.
2. Name requirements and non-requirements.
3. Choose the simplest useful AI pattern.
4. Design the data and retrieval path.
5. Add model orchestration, tools, and state only where they earn their complexity.
6. Protect data with IAM, PII handling, tenant boundaries, and auditability.
7. Evaluate answer quality before and after launch.
8. Operate for latency, cost, reliability, and safety.
9. Troubleshoot by separating retrieval failures, reasoning failures, tool failures, and product-fit failures.
10. Turn field pain into product feedback.

This spine matters because customer-facing GenAI interviews are usually not looking for one memorized diagram. They are looking for judgment. The interviewer wants to see how you move from ambiguity to a recommendation that an actual customer could trust.

## Why RAG is not enough

Retrieval-augmented generation is the default starting point for many enterprise assistants, but "RAG" is not a complete design.

You still have to decide:

- how documents are ingested, chunked, enriched, indexed, and refreshed
- whether retrieval should be lexical, semantic, hybrid, graph-based, or routed across multiple stores
- how metadata and access-control filters are applied
- how the system handles stale, conflicting, low-confidence, or missing evidence
- how citations are selected and rendered
- how conversation history affects retrieval without leaking context across users
- how the system measures groundedness instead of trusting plausible prose
- what the product does when it should not answer

This is where many interview answers get shallow. They name a vector database, an embedding model, and a chat model, then stop. In a real customer conversation, that is barely the opening move.

The hard work is making retrieval observable and correct enough that the model has something reliable to say.

## Agents raise the stakes

Tool calling and agents make the conversation more interesting and more dangerous.

An assistant that only answers questions can still harm trust when it hallucinates. An assistant that calls tools can mutate business state. It can create a ticket, send a message, update a record, schedule an event, trigger a workflow, or retrieve information the user should not see.

That changes the design.

The system needs tool schemas, authorization checks, policy-aware routing, confirmations for irreversible actions, idempotency keys, sandboxing where possible, and logs that explain what happened. It needs state management that can survive retries without double-executing actions. It needs a distinction between drafting, recommending, and committing.

In an interview, the question is not "Would you use agents?" The better question is "What part of this workflow truly needs agency, and what should remain deterministic automation?"

Sometimes the right answer is an agentic workflow. Sometimes it is RAG plus a small set of guarded tools. Sometimes it is a form, a rules engine, a search improvement, a queue, or a human review step. Senior judgment includes knowing when not to use the more exciting pattern.

## Evaluation is a product surface

Evaluation cannot be a footnote.

For a customer-facing GenAI system, answer quality is not a single score. You need to measure retrieval recall, citation relevance, factual groundedness, refusal quality, policy compliance, tool-call correctness, latency, cost, and user satisfaction. You need golden datasets, adversarial tests, regression suites, online monitoring, and a way for users to report bad answers.

You also need to know what failure looks like.

A hallucinated answer is one failure. A grounded answer over stale data is another. A correct answer shown to the wrong user is worse. A tool call that succeeds twice because retry behavior was not designed carefully is a different class of incident. A system that is accurate but too slow to use will still fail.

The best interview answers make these distinctions explicit. They do not flatten "quality" into vibes.

## Security is part of the core design

Enterprise AI systems inherit the security expectations of the systems they touch.

That means the design should account for:

- least-privilege access
- identity propagation from the user to retrieval and tools
- tenant isolation
- PII detection and handling
- encryption in transit and at rest
- audit logs for retrieval, prompts, model responses, and tool calls
- data retention policies
- admin controls and incident response
- clear boundaries between customer data, telemetry, and model improvement

These concerns do not sit after the architecture. They shape the architecture.

If the assistant is answering over internal documents, the retrieval layer has to respect the same access boundaries the source systems do. If the assistant can call business tools, authorization cannot be delegated to the model. If logs contain prompts and responses, the logging design itself becomes part of the data protection story.

## Production questions reveal maturity

The interview often gets most revealing when the system is "working" but the customer is unhappy.

The assistant is slow. Where do you look first? Retrieval fanout? embedding latency? model choice? context size? reranking? tool calls? network hops? frontend streaming?

The assistant is inaccurate. Is the problem ingestion, chunking, recall, ranking, prompt assembly, model reasoning, stale data, missing permissions, or unclear product expectations?

The assistant is too expensive. Is cost driven by embedding refresh, high-token prompts, long context, model tier, retries, tool fanout, low cache hit rate, or usage patterns that should be redesigned?

The assistant is not trusted. Is the answer uncited, overconfident, inconsistent, hard to correct, missing source transparency, or operating outside the user's mental model?

This is why the course spends time on troubleshooting. Production GenAI work is not just "design the happy path." It is knowing how to localize failure when the customer says the system is slow, inaccurate, expensive, or risky.

## What the course contains

The course is built as a multi-episode NotebookLM series with local fallback artifacts. Each episode is intended to support passive review and active recall: study guides, quizzes, flashcards, mind maps, prompts for audio and video overviews, mock drills, rubrics, and case studies.

The episode sequence:

1. Orientation: How to Use the Course
2. Interview Answer Spine
3. Customer Discovery and Requirements
4. Enterprise RAG Architecture
5. Vector Search, Retrieval, and Data Modeling
6. Agents, Tool Calling, Workflows, and State
7. Security, IAM, PII, Tenant Isolation, and Audit
8. Evaluation, Groundedness, and Hallucination Controls
9. Observability, Latency, Cost, and Reliability
10. Troubleshooting Slow, Inaccurate, or Expensive Systems
11. Cloud AI Product Mapping and Field Feedback
12. Full Customer Case Studies
13. Timed Mocks and Final Review

The public table of contents is meant to be the front door. Start there if you want the structured path. Use the NotebookLM master index if you want to jump directly into the notebooks.

## What I deliberately left out

The public version is intentionally generalized.

It does not include raw private source material, company-specific diagnostics, personal communications, internal system names, customer names, local paths, or operational secrets. The point is to extract the reusable lesson and rebuild it as public courseware.

That constraint made the material better. It forced the course to focus on durable patterns rather than one person's preparation process.

The resulting material is still specific. It just stays specific at the level that is useful to other engineers: architecture choices, tradeoffs, failure modes, evaluation methods, security constraints, production signals, and interview practice.

## The broader lesson

There is a gap between how GenAI systems are demoed and how they are operated.

There is a similar gap between how system design interviews are usually taught and how customer-facing GenAI roles are actually evaluated.

The work is not only "Can you design a RAG system?" It is:

- Can you discover the real customer problem?
- Can you choose the least complex pattern that works?
- Can you explain why not every workflow should become an agent?
- Can you protect data while still making the system useful?
- Can you measure groundedness and quality?
- Can you debug failures without guessing?
- Can you recommend a product path the customer can actually adopt?

That is the loop.

And it deserves prep material that treats it seriously.

This first post is the wrapper. The rest of the series will walk through the individual pieces: discovery, RAG, retrieval, agents, security, evaluation, observability, troubleshooting, product feedback, case studies, and timed mocks.
