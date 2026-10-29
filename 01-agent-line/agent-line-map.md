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

- **Model:** Claude Sonnet 5 by default; escalate to a frontier model for complex tasks or when the task needs a larger context window. The lab build runs `claude-haiku-4-5` (set in `00-build/.env`) to keep a run to a few cents.
- **Tools:** read-only lookups for the project record, activity, past updates, roadmap and team norms, plus story proposal (capped, queued for approval). No tool posts, creates, closes or merges anything.
- **Memory:** persists across runs, with lifetimes set in M4 (`04-memory-context/memory-and-context.md` §4). A run's working state is dropped at its end. Approved updates and decisions are kept 12 months, saved drafts 30 days, and norms and roadmap facts until a human changes them.
- **Loop:** a hook starts a run. It ends in success, stuck or escalate, each with a rule you can check (`02-loop-design/loop-spec.md`).
- **Bounds:** the full set comes in M5 (`05-bounds-evals/bounds-and-evals.md`). The build enforces these today: 8 iterations, 3 critic revisions, 3 attempts per step, $0.50 per run, 10 stories per batch.
- **Evals:** written in M5. Today's checks are the critic's six rules and three test runs: happy path, missing data, jailbreak.

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
