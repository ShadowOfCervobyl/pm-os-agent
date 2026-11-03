# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

1. **Every vague word had to become a number.** "Retry a few times" meant nothing to the loop until it was 3. "A few seconds" was not a timeout until it was 120. Each number forced a call I had been putting off.
2. **The documents and the build drifted apart.** Each module was right when I wrote it and wrong one module later. M1 said Sonnet 5, but the build ran Haiku. M1 said everything persists, then M4 gave memory lifetimes. M2 said a run reads only roadmap items safe to share, but the tool returned all of them. After every change I reread the earlier files.
3. **I trusted the critic too much.** It gave pass and then fail on the same bad draft. It passed a draft that had filled a missing source from another one.
4. **Two bounds were only in the table.** The template listed a timeout and a kill switch, and the code had neither. A bound in a document is a wish, so I built both.
5. **Every check I added changed how the model behaved.** The sprint check rejected 11 drafts in 10 runs until I told Cortex the rule up front and made the rejection say exactly what to do. After that, 0 of 10 named an invented sprint.

## Learning

1. **A bound is a number that code enforces, outside the model.** "High", "TBD" and "a few" are not bounds. My test is whether the model could talk its way past it. A counter, a budget, a file check and a missing tool cannot be argued with. A line in a prompt can.
2. **A second model is a second opinion, not a guarantee.** The critic has the same kind of blind spots as the drafter. I trust it only after I feed it cases that should fail, and I write down the ones where it does not fail. Then code enforces what it missed: a status update needs activity data, and a run with an injected brief must end in an escalation.
3. **What the model can read is a permission decision.** Flags and instructions did not keep Orbit and Pulsar away from the model, because the tools handed over everything. I moved the filter into the tools and wrote tests for it. The names still come through the norms, which cite them as examples. For now I accept that, and I check it again with real data.

## Aha moment

A missing source does not make the agent fail. It makes the agent fill the gap from the nearest source, in the same confident tone. With the activity feed withheld, Cortex took the activation figure from the roadmap, called it live activity and wrote "zero blockers" about issues it never saw. The dangerous failure is the quiet one. So "I can't verify that" has to be the default, and a check has to enforce it. (Fixed now: code rejects a draft with no activity data. In 10 withheld-source runs, none ended as an accepted draft.)

## What you'd do differently

1. **Write the evals before the prompts.** The missing-source case and the jailbreak ending would have failed on day one, not in module 5.
2. **Filter sensitive data inside the tools from the start.**
3. **Keep one table of numbers** (turns, seconds, dollars, rounds, attempts) and check every document against it.
4. **Name the backup operator and build the kill switch before the first run.** I named Sandra at the end.
5. **Use real, scrubbed data earlier.** The fixtures were so tidy that the gaps showed only when I removed a source on purpose.
