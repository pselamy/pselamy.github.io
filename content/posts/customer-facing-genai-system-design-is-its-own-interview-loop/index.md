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

Most system design preparation is built around classic backend prompts: design a feed, a chat system, a rate limiter, a file store, or a ticketing service.

Those exercises are still useful. They do not fully prepare you for the customer-facing GenAI loop, where the real question is closer to this:

> A customer wants an AI assistant over internal documents. How do you start, what do you ask, what do you build, and how do you know it is safe enough to trust?

That interview is not just architecture. It is discovery, requirements, RAG, retrieval quality, tool calling, IAM, PII, tenant isolation, evaluation, observability, cost, troubleshooting, and product judgment.

I could not find a preparation path that treated that loop as its own thing, so I built one.

## Open the course

Start with the public course spine:

- [Public Google Doc course table of contents](https://docs.google.com/document/d/1akqNIetG4R5kpv9AdobaAZv9qqBShTmHpVG3B8IJcds/edit?tab=t.0)
- [NotebookLM master index](https://notebooklm.google.com/notebook/9fbca41e-c836-4484-9bda-34bec0bdfaba)

The Google Doc is the clean public homepage. It gives the study paths, episode summaries, artifact notes, and final review checklist.

The NotebookLM master index is the hub for jumping into the notebooks directly.

## Direct NotebookLM episode links

Each episode has a focused NotebookLM notebook. Use the notebook for the generated learning experience, then use the Google Doc as the navigation layer back to the whole course.

| Episode | Notebook | What it trains |
| --- | --- | --- |
| 0 | [Orientation: How to Use the Course](https://notebooklm.google.com/notebook/29e38a85-3121-479c-b2fd-b8698854c91a) | How to move through the course without getting lost in the materials. |
| 1 | [Interview Answer Spine](https://notebooklm.google.com/notebook/858dd9db-aa45-4acc-a034-e0820923d997) | A repeatable structure for discovery, architecture, tradeoffs, reliability, security, and recommendation. |
| 2 | [Customer Discovery and Requirements](https://notebooklm.google.com/notebook/375f041e-e51d-4e2c-b317-880fc2e80af5) | The questions to ask before proposing any GenAI architecture. |
| 3 | [Enterprise RAG Architecture](https://notebooklm.google.com/notebook/144c060b-b944-4fcc-9ae6-cbb5bc03b3d2) | Ingestion, indexing, retrieval, grounding, citations, and production RAG boundaries. |
| 4 | [Vector Search, Retrieval, and Data Modeling](https://notebooklm.google.com/notebook/7e83ff4e-9575-49d0-893f-8c5700d23de9) | Chunking, embeddings, hybrid search, metadata filters, reranking, freshness, and recall. |
| 5 | [Agents, Tool Calling, Workflows, and State](https://notebooklm.google.com/notebook/b999660a-d6a7-4f1a-8924-591e17bcb645) | When to use agents, when not to, and how to design tool calls safely. |
| 6 | [Security, IAM, PII, Tenant Isolation, and Audit](https://notebooklm.google.com/notebook/9e5847c5-d982-4d0b-8691-33e2703d5304) | Identity propagation, least privilege, PII handling, audit logs, and isolation boundaries. |
| 7 | [Evaluation, Groundedness, and Hallucination Controls](https://notebooklm.google.com/notebook/71319ced-35b7-4c20-a207-d6214507bc15) | Golden sets, groundedness checks, refusal quality, regression tests, and human review. |
| 8 | [Observability, Latency, Cost, and Reliability](https://notebooklm.google.com/notebook/dabdc0b8-81f8-4b1f-9562-b867b6a6ca8e) | What to monitor once the assistant is live: tokens, latency, retrieval, tools, failures, and spend. |
| 9 | [Troubleshooting Slow, Inaccurate, or Expensive Systems](https://notebooklm.google.com/notebook/4602a98d-9f67-4294-b6cf-98045c01722c) | How to debug bad GenAI systems without guessing. |
| 10 | [Cloud AI Product Mapping and Field Feedback](https://notebooklm.google.com/notebook/57b21047-5a80-4638-8611-94a58cba2bb5) | How to connect customer pain to platform capabilities and product feedback. |
| 11 | [Full Customer Case Studies](https://notebooklm.google.com/notebook/7abc2abd-3a84-4b0a-824b-b8eb7200be24) | End-to-end scenarios that force discovery, architecture, tradeoffs, and recommendation. |
| 12 | [Timed Mocks and Final Review](https://notebooklm.google.com/notebook/34a6cacf-c42b-4b57-a268-b1fc376a85c0) | Cram drills, timed answers, final review, and interview readiness checks. |

## How I would use it

For a 90-minute emergency pass:

1. Open the [public course table of contents](https://docs.google.com/document/d/1akqNIetG4R5kpv9AdobaAZv9qqBShTmHpVG3B8IJcds/edit?tab=t.0).
2. Skim [Episode 1: Interview Answer Spine](https://notebooklm.google.com/notebook/858dd9db-aa45-4acc-a034-e0820923d997).
3. Review [Episode 3: Enterprise RAG Architecture](https://notebooklm.google.com/notebook/144c060b-b944-4fcc-9ae6-cbb5bc03b3d2).
4. Hit [Episode 6: Security, IAM, PII, Tenant Isolation, and Audit](https://notebooklm.google.com/notebook/9e5847c5-d982-4d0b-8691-33e2703d5304).
5. Finish with [Episode 12: Timed Mocks and Final Review](https://notebooklm.google.com/notebook/34a6cacf-c42b-4b57-a268-b1fc376a85c0).

For the 8-12 hour version, work through the notebooks in order and use NotebookLM's study guide, quiz, flashcards, mind map, and audio or video overview features where available.

For multi-day immersion, treat Episodes 2, 3, 5, 6, 7, 8, 9, and 11 as the core. Those are the episodes that most directly train the customer-facing loop: understand the customer, design the architecture, secure it, evaluate it, operate it, debug it, and recommend a path forward.

## What this course is trying to train

The course is organized around a simple answer spine:

1. Clarify the customer situation.
2. Name requirements and non-requirements.
3. Choose the simplest useful AI pattern.
4. Design retrieval, orchestration, tools, and state.
5. Protect the data and identity boundaries.
6. Evaluate groundedness and answer quality.
7. Operate for latency, reliability, and cost.
8. Troubleshoot failures with evidence.
9. Turn field pain into product feedback.
10. Make a recommendation the customer can actually adopt.

That spine matters because the right answer is rarely "use RAG" or "add an agent." Sometimes the right answer is RAG. Sometimes it is a guarded tool workflow. Sometimes it is fine-tuning, human review, a deterministic automation, a better search product, or a smaller first release.

The interview is testing whether you can tell the difference.

## Why this needed to exist

There is a gap between how GenAI systems are demoed and how they are operated.

There is also a gap between classic system design prep and the work expected in customer-facing GenAI roles. The real loop includes messy enterprise data, permissioned knowledge, ambiguous requirements, changing customer constraints, model behavior, security boundaries, hallucination risk, observability, and cost.

That deserves prep material that is more than a prompt list.

This course is public-safe by design. It does not include raw private source material, company-specific diagnostics, personal communications, internal system names, customer names, local paths, or operational secrets. The lesson was extracted, generalized, and rebuilt as courseware.

## Series roadmap

This is the wrapper post and course directory. The rest of the series should go deeper into the individual modules:

- discovery before architecture
- RAG as a production system, not a buzzword
- retrieval quality and vector data modeling
- agents, tool calls, workflow state, and approval gates
- security, privacy, IAM, and auditability
- evaluation and hallucination controls
- observability, cost, latency, and reliability
- troubleshooting slow, inaccurate, or expensive systems
- turning customer pain into product feedback
- full case studies and timed mocks

Open the [public course table of contents](https://docs.google.com/document/d/1akqNIetG4R5kpv9AdobaAZv9qqBShTmHpVG3B8IJcds/edit?tab=t.0), then jump into the [NotebookLM master index](https://notebooklm.google.com/notebook/9fbca41e-c836-4484-9bda-34bec0bdfaba).
