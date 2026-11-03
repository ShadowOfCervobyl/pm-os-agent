# Agent gates: contracts

Decided with the owner on 2026-11-02. Three checks that code enforces, outside the model, on top of the critic.

## CONTRACTS

### T-1

| Part | Contract |
|---|---|
| Critic reply | `critic.review()` returns `verdict`, `reasons` and `injection_in_task`. `injection_in_task` is a boolean. It is true when the task brief contains instructions aimed at Cortex, such as an override, a claimed permission or a request to post. The critic decides it from the brief it is given. Cortex's draft does not change it. |
| Critic request | Every critic call carries `temperature` set to 0. |
| Escalation output | An output is an escalation when, after removing leading whitespace and any of the characters `*`, `#`, `-`, `_` and `>`, it starts with `ESCALATE`. Any other output is a draft. |
| Required source | A draft is rejected when no `get_activity` call has returned a result without an `error` key. An escalation output is never rejected for this reason. |
| Injection ending | A draft is rejected when the critic reply has `injection_in_task` true. An escalation output is never rejected for this reason. |
| Rejection | A rejected output counts as a failed critic verdict: its reasons go back to Cortex, it uses one of the `MAX_REVISIONS` rounds, and at the cap the run is held and escalated. The critic still runs on every output, escalations included. |

### T-2

| Part | Contract |
|---|---|
| Embargoed project | A project is embargoed when its record in `projects.json` has status `embargoed` or the flag `confidential`. Its short name is the first word of its `name`. |
| Past updates | `search_past_updates()` returns no entry from `past-updates.json` or `decision-log.json` that names an embargoed project. An entry names it when the short name appears in the entry's `project`, `summary` or `theme`, ignoring case. This holds for the fallback entries too. Every other entry is still returned. |
| Sprint | A draft is rejected when it contains `Sprint <number>`, ignoring case, and that text is absent from the source log. An escalation output is never rejected for this reason. |
| Rejection | The same as in T-1. The reason goes back to Cortex, the rejection uses one of the `MAX_REVISIONS` rounds, and at the cap the run is held. |

### T-3

| Part | Contract |
|---|---|
| Project list | `get_project()` for an unknown ID returns `known_projects` with the IDs of projects that are not embargoed. An embargoed project is defined as in T-2. Its ID does not appear anywhere in the reply. |
