# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

Cortex stays single-agent for its actual work. The only reason to split is an independent validator: a critic that doesn't share Cortex's context, so it doesn't inherit Cortex's blind spots when grading its own draft. Separation of concerns, parallelism and context-window pressure don't apply — Cortex does one task type, one project per run, on small fixture data.

## 2. Topology

**Pattern:** single + subagents

```
[Inbound PM task, via hook] → [Cortex: pulls project data, drafts update + stories]
                            → [Critic] → fail → back to Cortex (max 3 revisions) → still failing → escalate
                                       → pass → [PM review checkpoint] → queued, nothing posted
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| Cortex | Pulls project/activity/roadmap/norms, drafts the update, proposes stories | M2 loop (this file) |
| Critic | Checks Cortex's draft against the 6 rules in Field 5, before the PM sees it | Validation only — one call per draft, no loop of its own |

## 4. Communication & hand-offs

In-process, a plain function call (`critic.review()`), no MCP/A2A. Cortex passes the critic the proposed draft text and the source-data log (every tool call and result Cortex used). The critic passes back a verdict plus reasons; nothing else crosses.

## 5. The validator

- **What the critic checks:** the update names the correct project and real activity · every claim, metric and date traces to pulled data · it stays within team norms (no unconfirmed date, no launch gate marked, no confidential item leaked externally) · nothing is posted, committed, created, closed or merged · a prompt-injection attempt was refused and escalated · a tool rejection or bound trip is scored as a correct escalation, not a failure.
- **Fail action:** revise, up to 3 rounds, then escalate.
- **Pass action:** advance to the PM review checkpoint — never auto-send.

## 6. State: shared vs isolated

Shared: the draft and the source data Cortex pulled — the critic checks claims against it. Isolated: the critic gets a fresh call with no memory of Cortex's reasoning, past turns or prior revision attempts, only the current draft and source log. That's what makes it independent — it can't inherit Cortex's blind spots or be argued into a pass across revision rounds.

## 7. Cost & latency budget

The critic adds one model call per draft attempt, serial with Cortex's own calls. Typical case: 1 critic call. Worst case, at the revision cap: 4 critic calls (the first draft plus 3 revisions), run one after another, before the draft reaches the PM. Each critic call is shorter than a Cortex turn (no tool use), so the added latency is smaller than 4 full Cortex steps, but it still stacks before anything is queued for review.
