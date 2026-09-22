# Prototype: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 1, the working agent demo
>
> ✅ **What this validates:** the agent actually runs end to end, by the end you'll have proven it with real screenshots of your Cortex across the six required moments (M2 to M6).

## What it does

_One paragraph: the agent in action, end to end._

## How you built it

- **Coding agent:** _which one you directed (Claude Code / Cursor / Codex)_
- **Model + bounds:** _model used, max iterations, cost cap, queue cap_
- **Repo / config:** _path to your build in `00-build/`_
- **Live link:** _[shareable URL, optional bonus]_

## Screenshots (required, collected M2 to M6)

Real screenshots of *your* Cortex running. These are the `00-build/CORTEX-ANATOMY.md` set and they are required, a link alone is not enough.

| # | Screenshot | What it shows | From |
|---|---|---|---|
| 1 | _[img]_ | happy-path run: a real drafted update + the HITL checkpoint (queued, not posted) | M2 |
| 2 | *(transcript below, no image)* | the critic rejecting a bad draft (revise/block) | M3 |
| 3 | _[img]_ | a grounded update citing pulled activity + a caught hallucination | M4 |
| 4 | _[img]_ | jailbreak refused + escalated | M5 |
| 5 | _[img]_ | an iteration/cost/queue bound halting a runaway | M5 |
| 6 | _[img]_ | end-to-end run | M6 |

## M3: the critic rejecting a bad draft

The critic rejects a hand-crafted bad draft (invented 55% activation rate, committed a July 15 GA date) that violates checks 2 and 3 from the orchestration map. Verdict: fail, both violations named in the reasons.

```json
{
  "verdict": "fail",
  "reasons": [
    "Activation rate claim is incorrect: source data shows 41% (not 55%). This is an invented metric.",
    "GA launch date of July 15 is not traceable to any source data pulled. This is an unconfirmed date commitment, violating team norms.",
    "The output posts a public update with unverified launch gate commitment, which should not proceed without human escalation."
  ]
}
```

## How to run it

_Minimal steps for someone to reproduce the demo (env vars, and the command or the coding-agent prompt you used)._
