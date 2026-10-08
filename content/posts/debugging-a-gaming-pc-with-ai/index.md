---
title: "The Lights Were On. The Screen Was Black."
date: 2026-10-07T19:00:00-04:00
slug: "debugging-a-gaming-pc-with-ai"
description: "Debugging my son's gaming PC with Codex: reproduce the failure, collect evidence, test a mitigation, and report what we actually know."
tags: ["AI", "debugging", "observability", "hardware"]
draft: false
showToc: false
---

My son and I built his gaming PC in 2024. After roughly two years of working across different games, it started losing video. The fans kept spinning. The RGB lights kept pulsing. The monitor said **no signal**.

I had been an A+ certified technician. I wasn't afraid to open the case, but I wanted evidence before replacing an expensive graphics card.

We investigated with Codex. It helped inspect Windows events, record GPU telemetry, build graphs and run controlled tests. I checked the physical display, challenged assumptions and decided what to try next.

## Minecraft got the blame

Most recent failures happened during Minecraft. But that was also what my son had mostly been playing.

Safe Mode stayed visible for at least 15 minutes. Disabling the NVIDIA overlay didn't prevent another failure. Neither did a clean NVIDIA driver update. Windows recorded Java crashes in NVIDIA's OpenGL driver; NVIDIA's diagnostic utility reported the GPU was lost.

That identified a failure path, not its cause.

I asked why we needed my son to keep playing to generate load. We switched to an OCCT graphics stress test. About five minutes later, the display failed again.

**We had reproduced the symptom outside Minecraft.**

## Measure, change, retest

The failing stress test's recorded GPU core temperature peaked at 62°C. That weakened the simple overheating explanation, although core temperature alone couldn't rule out a hotspot, memory or power-connection problem.

We examined the wider software inventory and updated the AMD chipset package. We left the motherboard BIOS and newly installed NVIDIA driver unchanged.

Then we tested again:

| Test | Result |
|---|---|
| 15-minute OCCT run, display on integrated graphics | Passed; discrete GPU core peaked at 65°C |
| 15-minute OCCT run, display directly on GeForce | Passed; 67°C; physical picture stayed visible |
| 40-minute Minecraft observation | No captured GPU loss or relevant Windows error; 60°C peak |

My son tried vanilla and modded versions. The logs showed multiple Java restarts. He explained that he had deliberately switched versions: those weren't crashes.

A process log could tell us what stopped. It couldn't tell us why he stopped it.

## The assistant needed supervision

Remote access took work. My laptop's changed IP address broke a connection rule. The receipt search also stopped too early; searching the additional mailbox I identified finally recovered the graphics card, PSU, case, cooler and SSD purchases.

Codex did substantial work. My questions improved that work: had we checked enough, did the evidence support the conclusion, and could we design a better test?

## Report the evidence, preserve the uncertainty

We [submitted a report to NVIDIA](nvidia-report.txt), followed by a [hardware-identification addendum](hardware-addendum.txt). These are public copies of our submissions, **not a vendor-confirmed bug or public NVIDIA ticket**. Raw memory dumps and personal account details aren't included.

The chipset update was followed by successful tests. We haven't proved it caused the improvement. Reboots and display reconnections are confounders, and we haven't rolled back the update or substituted hardware to isolate the cause.

As of October 7, NVIDIA hasn't confirmed a diagnosis. Longer-term stability remains to be established.

My son got back to playing. We got a reproducible failure, measurements, a promising mitigation and a useful vendor report—without buying another graphics card.
