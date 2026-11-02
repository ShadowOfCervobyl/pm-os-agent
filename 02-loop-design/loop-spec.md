# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** hook. Something wakes Cortex with a request: another agent, a system, a user or an operator. The request carries the instructions and, sometimes, its own definition of done.

**Why not the others:**
- **Cron:** it runs on a schedule and nobody asks for it. I do not want that much autonomy in the first runs.
- **Heartbeat:** it watches my to-do list, the repo and email, and starts by itself when something changes. Cortex would start work nobody asked for.
- **Goal:** it keeps going until the output matches the task exactly. Without a check and a limit it never ends. The critic already does this check inside a run, but it does not start a run.

**Dedupe:** I check the request ID first, then project and week, because not every caller sends an ID and weekly tasks can collide. On a match, or a possible match, Cortex looks at it and asks the operator before it runs. It never runs silently. That costs the operator some work, and I accept it until we find the edge cases. Not built yet: the build has no live hook and no request IDs, so it does not enforce this. It waits for a real hook.

## 2. Goal / definition of done

A run is done when all three layers pass:
- **Global, every run:** the draft is saved for review · proposed stories are queued for approval and within the cap · the critic returns a pass · nothing is posted, committed or created · every claim cites its source.
- **Task type:** each task type has its own DoD. Prioritization differs from story drafting, for example.
- **Operator:** whatever the operator specifies for that task.

If Cortex can't finish, it escalates to the operator instead.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | All three DoD layers pass | Stop. Queued for review, nothing posted |
| **Stuck / give up** | The same step fails 3 times (one attempt = one failed call, one failed completion of the task, or one failed read or write), the critic still fails the draft after 3 correction rounds, or the run hits a bound (8 model turns, 120 seconds, $0.50, or the kill switch) | Stop. Escalate to the operator with what failed |
| **Escalate to human** | Firm ship date asked for (M1 #4) · post asked for (M1 #8) · confidential or embargoed project · story batch over cap (M1 #7) · project or data doesn't exist · request ID or project-and-week match | Stop at the HITL checkpoint. Hand to the operator |

## 4. State

Memory stays between runs. The lifetimes are in `04-memory-context/memory-and-context.md` §4. A run should read only its own project's history, plus the team norms and the roadmap that are safe to share. If every run could read every project, one project's confidential material would sit next to all the others. The jailbreak test shows why: the injected notes told Cortex to publish the embargoed Orbit roadmap in a Northstar update.

What is enforced now: the roadmap tool removes embargoed sections, and the project tool returns a stub for an embargoed project. Both have tests in `00-build/test_cortex.py`. What is not: the names Orbit and Pulsar still reach the model through the team norms, the past updates and the decision log, which cite them as examples (M5 §1).

## 5. The five things a loop can lean on

`state` and the critic are in use. Work tree, skills and connectors are not needed yet.

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet. One run at a time, and Cortex only writes a draft file. Add it when runs go parallel. |
| **Skills** (reusable capabilities) | Not needed yet. There is one task type today. Add them when prioritization and story drafting get their own DoD and format. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | None wired. The tools read fixture data today. Plan: read-only GitHub and Jira connectors later. |
| **Subagents** (independent check when the loop can't grade itself) | One independent critic and no other subagents. See `03-orchestration/orchestration-map.md`. |
| **State tracking** | As in §4: per-project history plus shared norms, everything kept. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

The agent lives in `00-build/`: `agent.py` (the loop and its bounds), `prompts.py` (Cortex's rules and the critic's six checks), `critic.py` (the independent validator) and `tools.py` (the read-only tools). Run it with `cd 00-build && python agent.py`. Add `missing-data` or `jailbreak` to run the other two test cases. The checks for the bounds and the embargo filter are in `00-build/test_cortex.py`. They use a scripted model, so they cost nothing.
