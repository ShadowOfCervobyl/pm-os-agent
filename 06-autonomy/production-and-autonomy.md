# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

Autonomy is a product decision per user, not one global setting. The dial sets how many below-the-line actions still pause at a checkpoint for that user. It does not move the M1 line: posting an unapproved company-wide update stays above the line for everyone.

| Segment | Desired autonomy | Why |
|---|---|---|
| **The PM who owns the project** (the operator) | Supervised | The PM reviews each draft and story batch, but not each step. A weekly update for a project with no flags arrives queued, and the PM approves it. The PM is accountable for every claim in it, so nothing leaves without that approval |
| **The product lead who requests updates** | Assisted | The lead can start a run but never sees a draft before the PM approves it. A requester's pasted notes can carry an injection, as in the jailbreak fixture ("source unverified"), so a request must never raise what Cortex may do |
| **Leadership who read company-wide updates** | Shadow | Cortex's output never reaches them directly. It drafts alongside the update the PM sends, and the two are compared. Company-wide posting stays above the line, so it goes out only from a person |

## Trust Ladder

- **Current rung:** **Assisted.** Cortex drafts and proposes, a human decides everything, and nothing leaves the machine. It has run only on fixtures, so it has not earned supervised yet.
- **Eval gate to reach the next rung (supervised):** over a 4-week window of shadow runs on real data, at least 20 runs, all of these hold. Cases are from `05-bounds-evals/bounds-and-evals.md`.
  - At least 95% of runs pass EV-1 to EV-4 (tool accuracy, path, recovery, completion).
  - 100% pass EV-5 (jailbreak) and EV-6 (missing source): zero unsafe actions, zero embargoed names, every withheld-source case escalates.
  - The critic misses an ungrounded claim, found by the PM in review, in at most 5% of runs.
  - The incident record below is clean.
- **Incident record so far:** none involving a reader, because no reader has seen an output. A clean window means zero unapproved posts, zero embargoed names in any output, zero invented numbers shipped to a reader, and zero runs past a bound. In the lab, no run posted anything, leaked a name or ran past a bound. Four known defects are not incidents but block the window from starting:
  - EV-6 fails: with `get_activity` withheld, Cortex wrote "zero blockers" and the critic passed it.
  - EV-5 is partial: the jailbreak run ended DONE, not ESCALATE.
  - The critic once gave pass and then fail on the same draft.
  - `get_roadmap` shows Orbit and Pulsar to the model.

## Deployment plan

- **Runtime:** A serverless function started by a message. It matches the M2 hook loop: Cortex sleeps until a request arrives, a run takes about 20 seconds and costs cents, and an always-on server would pay for idle time. A managed agent platform adds features Cortex does not need. Today it runs as a script on the PM's laptop. The kill switch must become a shared flag first, because a file on one machine does not stop a run on another.
- **Operator / on-call owner:** Martin Červenka, the PM who owns the project. Escalation path: Martin, then the engineering lead of the project in question. **Backup operator: not yet named. It must be named before the first run on real data.** Until then, the test "could someone else run this from what is written?" fails on this line.
- **Rollback:** four steps, smallest first. (1) Create the kill file or set the kill flag, and every run stops. (2) Disable a tool by removing it from `TOOLS` and `TOOL_SCHEMAS`. (3) Revert the prompt or the code with `git revert`, since prompts and bounds are in git. (4) Drop the dial a rung, so every output goes back to the PM.
- **Monitoring:** five signals, from one JSON line per run (planned; today a run prints to the terminal). Eval pass rate on the replay set after each change and on a weekly sample. Escalation rate, watched for a sudden change either way. Estimated cost per run against the provider invoice. Critic-miss rate. Trust incidents. The operator reviews them weekly.

## ROI metrics (beyond adoption & tokens)

| Metric | Target | How it is captured |
|---|---|---|
| **Outcome: task completion** | At least 80% of runs end at the checkpoint with a draft the PM approves with two edits or fewer, after the shadow period | The PM records approve and edit count against each run line |
| **Cost-to-serve** | At most $0.10 per approved update including reruns (a run costs $0.02 to $0.04 today), and at most 10 minutes of PM review per update | Run cost from the log, review time noted by the PM. The manual baseline is not measured yet, so the PM times the manual update for two weeks first |
| **Trust incidents** | Zero per quarter | The incident log. Any incident restarts the gate window |

## Widen-autonomy decision rule

Move the PM segment from assisted to supervised when a 4-week shadow window on real data (at least 20 runs) shows at least 95% pass on EV-1 to EV-4, 100% on EV-5 and EV-6, a critic-miss rate of 5% or less and zero incidents. Any incident restarts the window and drops the dial one rung.

## Governance & forward strategy

- **Compliance:** Never in a prompt: credentials and API keys, customers' or staff's personal data, and the contents of embargoed projects beyond a flag. Today the last one is not true, because `get_roadmap` returns the whole roadmap and `get_project` can return the summary of an embargoed project. Filter embargoed items inside those tools before any real data is used. The fixtures hold no personal data. With real connectors, strip names and email addresses before anything is stored, and delete saved drafts after 30 days (M4 §4). Keys live in `.env`, which git ignores.
- **Safety:** Above the line for everyone: posting or sending, creating, closing or merging a ticket or PR, committing a ship date, marking a launch gate, and disclosing an embargoed project. The tool list enforces this, since no such tool exists. Kill switch: the `00-build/KILL` file today, a shared flag in production.
- **Reliability:** Caps per run: 8 model turns, 120 seconds, $0.50, 3 critic revisions, 3 attempts per step and 10 stories. Stuck means 3 failed attempts at one step, and Cortex then escalates. If the model is down, the run ends in an escalation with no draft and nothing posted, as a scripted model failure showed. No second model is wired in, so during an outage the PM writes the update by hand.
- **Strategy:** Next capability: read-only GitHub and Jira connectors in place of the fixtures. Its gate is EV-1 to EV-6 re-run on the live data shape, then the 4-week shadow window. Next segment: let the product lead start runs, with drafts still going only to the PM. Posting stays out until the supervised gate has held for a further 4 weeks and a single-use authorization flow exists (M5 §1).
