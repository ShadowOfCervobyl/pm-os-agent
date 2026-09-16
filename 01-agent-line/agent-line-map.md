# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner, by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| Pull project state + activity | H | L | H | Below | none |
| Decide relevant context | H | L | M | Below | spot-check |
| Draft the update | H | L | H | Below | none |
| Decide tone/commitment level | H | M | M | Below | spot-check |
| Flag at-risk/escalation | H | L | H | Below | none |
| Choose what to escalate | M | H | L | Above | required |
| Propose a story batch (capped) | H | L | H | Below | none |
| Post an update / approve a company-wide one | L | H | M | Above | required |

## Agent anatomy (sketch)

- **Model:** Claude Sonnet 5 by default; escalate to a frontier model for complex tasks or when the task needs a larger context window.
- **Tools:** project + activity lookup (read) · story proposal (capped) — nothing further needed today.
- **Memory:** everything persists across runs.
- **Loop:** _placeholder, defined in M2 loop-spec.md_
- **Bounds:** _placeholder, defined in M5 bounds-and-evals.md_
- **Evals:** _placeholder, defined in M5 bounds-and-evals.md_

## The golden rule, applied

1. **Pull project state + activity** — below: easy to reverse, low blast radius, easy to verify. Deciding factor: blast radius — pure read, nothing changes.
2. **Decide relevant context** — below: easy to reverse, low blast radius, medium to verify. Deciding factor: blast radius — nothing leaves the system yet.
3. **Draft the update** — below: easy to reverse, low blast radius, easy to verify. Deciding factor: reversibility — it's a draft, not a send.
4. **Decide tone/commitment level** — below: easy to reverse, medium blast radius, medium to verify. Deciding factor: reversibility — proposing tone, not committing to it.
5. **Flag at-risk/escalation** — below: easy to reverse, low blast radius, easy to verify. Deciding factor: blast radius — a flag costs a glance, nothing more.
6. **Choose what to escalate** — above: medium to reverse, high blast radius, hard to verify. Deciding factor: blast radius — miss a real risk or over-escalate, and it costs credibility either way.
7. **Propose a story batch (capped)** — below: easy to reverse, low blast radius, easy to verify. Deciding factor: reversibility — a proposal, not a committed story.
8. **Post an update / approve a company-wide one** — above: hard to reverse, high blast radius, medium to verify. Deciding factor: reversibility — once it's posted, it's out.

## Hardest call

Proposing story/roadmap batches to Cortex (#7). Past experience outsourcing roadmap-level decisions to AI without a cap taught me that blast radius is the deciding axis — capped, it's a safe below-the-line proposal; uncapped, it isn't.
