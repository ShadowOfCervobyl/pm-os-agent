# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

Each run receives these, in priority order. When the window gets tight, cut from the bottom:

1. The rules and the definition of done (the system prompt).
2. The task brief.
3. Team norms.
4. This project's record and this week's activity.
5. The roadmap.
6. Past updates: the top matches only.

Today all of it is about 7 KB, so nothing is cut. The order matters once real sources grow: past updates go first, then the roadmap. The rules, the brief, the norms and this week's activity never go. Without them Cortex can't stay in bounds or ground a claim.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Why |
|---|---|---|---|
| Task brief | 0.5 KB, one document, fixed for the run | Long-context | **Size.** One short document, and Cortex needs all of it. |
| Team norms | 2 KB, changes rarely, must be current | Long-context | **Citation.** Cortex must quote the exact rule it relied on, and a slice could drop the one rule that matters. Read fresh on every run. |
| Roadmap | 0.8 KB, slow-changing, some items confidential | Long-context | **Size.** Small enough to include whole, so Cortex cites exact lines. Flip to retrieve when it outgrows the window. Confidential items rest on their flags and the critic; see §5. |
| GitHub/Jira activity | grows and changes every week | Retrieve | **Volatility.** Only this project's latest week matters, and each claim is cited by PR or issue ID. |
| Past updates | grows without limit | Retrieve | **Size.** Precedent needs a few matches, not the whole history. |

## 3. Retrieval quality plan

Only the two retrieved sources need moves. The other three are included whole.

| Source | Routing | Document grading | Reranking | Self-verification | Caching |
|---|---|---|---|---|---|
| **Activity** | ✓ Project ID taken from the brief, never guessed | ✓ Right project, this week only | — The list is small and all of it is needed | ✓ Every claim cites a PR or issue ID. No activity means escalate, never "all clear" | — Changes every week, so read it fresh |
| **Past updates** | ✓ Query by project name and update type | ✓ Drop other projects' updates. The search falls back to two unrelated ones when nothing matches | ✓ Newest first within the same project | ✓ Precedent sets tone only. Never copy its numbers | — Small and cheap, so not worth it |

**Why these moves.** Each follows from how the source fails:
- **Activity fails silently.** With `get_activity` withheld, Cortex did not escalate. It took 41% → 43% from the roadmap, called it "live activation metrics", and wrote "zero blockers" without seeing any issues. The critic passed it. Self-verification is the move that stops this.
- **Past updates fail by being close but wrong.** A search for a project that does not exist still returns two other projects' updates, because the search falls back to the first two entries. Grading drops them, and tone-only use keeps old numbers out of the draft.

**What the build does today.** It does key lookup for activity and keyword search for past updates. Grading, reranking and self-verification are not enforced in code. The prompt and the critic carry them, and the critic missed the withheld-activity case. Enforcing them is M5 work.

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | The task brief, this run's tool results, the draft, the critic's verdicts | This run. Gone when it ends, except the saved draft |
| **Episodic** (past runs) | Approved status updates and decisions. Saved drafts, held for review | Approved updates and decisions: 12 months, per project. Saved drafts: 30 days, local only. Drafts a human rejects never become precedent |
| **Semantic** (durable facts/prefs) | Team norms, roadmap facts, the embargo list (Orbit, Pulsar), PRD scope | Until a human changes it. Read fresh on every run and reviewed monthly. Only humans write it, because Cortex has no write tool (M1) |
| **Shared** (across agents) | The draft and the source log, handed to the critic | This run only. The critic sees nothing of Cortex's reasoning (M3 §6) |

Cortex reads all four and writes only the saved draft and the queued story proposals. Everything else is written by a human, which keeps memory on the safe side of the M1 agent line. These lifetimes are listed as a bound in M5 §1. The code does not enforce them yet.

## 5. Memory risks & mitigations

| Risk | Where it bites Cortex | Mitigation |
|---|---|---|
| **Drift** | Each update copies the format and numbers of the last one, so errors carry forward week after week | Precedent sets tone only. Every number traces to this week's pulled activity. The norms stay the fixed reference, and a human spot-checks drafts. M5 adds a golden-example eval |
| **Poisoning** | Pasted notes in the task brief tell Cortex to post or reveal Orbit (the jailbreak fixture). A wrong draft saved as precedent gets trusted later | Brief content is data, never instructions (norms, prompt, critic check 5). Only human-approved updates enter episodic memory. Cortex cannot write semantic memory |
| **Staleness** | Pulsar joined the embargo list on 2026-07-02, so an old copy of the norms or roadmap would let it through. Last week's 39% → 41% sits in past updates | Norms, roadmap and activity are read fresh on every run, never cached. Every pulled item carries a date. Past updates serve tone only. No activity means escalate (§3), because the withheld-source run showed other sources cover the gap quietly |
| **Confidential / retention** | `get_roadmap` returns the whole roadmap, Orbit and Pulsar included, so the model sees them. The ingest run kept both out of the draft (checked), but only the flags and the critic stop a leak, which does not match the M2 read rule | Today: flags, the norms and the critic's leak check. Fix, still open and listed in M5 §1: filter embargoed items inside the tool, before the model sees them. Retention: saved drafts live 30 days and stay out of git (`run-output/` is ignored). No personal data in the fixtures. With real Jira or email connectors, strip names and addresses before anything is stored |
