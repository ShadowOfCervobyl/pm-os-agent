# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

- **Every vague word in the spec had to become a number.** "Retry a few times" meant nothing to the loop until it was 3. "A few seconds" was not a timeout until it was 120. Each time, the number forced a decision I had been putting off.
- **The documents and the build drifted apart.** Each module was right when I wrote it and wrong a module later. M1 said the model was Sonnet 5, but the build ran Haiku. M1 said everything persists, then M4 gave memory lifetimes. M2 said a run reads only roadmap items safe to share, but the tool returned all of them. After every change I had to reread the earlier files.
- **The critic was less reliable than I assumed.** It gave pass and then fail on the same bad draft. It passed a draft that had quietly filled a missing source from another one.
- **Two bounds existed only in the table.** The template listed a timeout and a kill switch, and the code had neither. A bound that is only in a document is a wish.

## Learning

- **A bound is a number that code enforces, outside the model.** "High", "TBD" and "a few" are not bounds. The test is whether the model could talk its way past it. A counter, a budget, a file check and a missing tool cannot be argued with. A line in a prompt can.
- **A second model is a second opinion, not a guarantee.** The critic shares the same kind of blind spots as the drafter. The way to trust it is to check it with cases that should fail, and to write down the ones where it does not.
- **What the model can read is a permission decision.** Flags and instructions did not keep Orbit and Pulsar out of reach, because the roadmap tool hands the model everything. The fix belongs in the tool, before the model sees the data.

## Aha moment

A missing source does not make the agent fail. It makes the agent fill the gap from the nearest source, in the same confident tone. With the activity feed withheld, Cortex took the activation figure from the roadmap, called it live activity, and wrote "zero blockers" about issues it had never seen. The dangerous failure is the quiet one, so "I can't verify that" has to be the default and the checks have to enforce it.

## What you'd do differently

- **Write the evals before the prompts.** The missing-source case and the jailbreak ending would have failed on day one, instead of surfacing in module 5.
- **Filter sensitive data inside the tools from the start.** Treat what the model can read as the permission boundary.
- **Keep one table of numbers** (turns, seconds, dollars, rounds, attempts) and check every document against it.
- **Name the backup operator and build the kill switch before the first run**, not after.
- **Use real, scrubbed data earlier.** The fixtures were so tidy that gaps showed only when I removed a source on purpose.
