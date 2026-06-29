## Visual Plan / Recap (Lavish)

Two skills render interactive HTML review surfaces in the local Lavish Editor (`lavish-axi`). Use them proactively, not only when asked; skip them for trivial one-step work.

- **`/visual-plan`** — before non-trivial, multi-step, or decision-heavy work, turn the task into an interactive visual plan (options, tradeoffs, comparisons, timelines, diagrams, plus wireframes when there is a UI) and get it approved before building. The locked plan is the build spec.
- **`/visual-recap`** — after a substantial unit of work, summarize what changed as a visual recap: a file map plus annotated diffs for code, or narrative, comparisons, and decisions for everything else.

Both render via a subagent to stay cheap and keep the markup out of the main context. They need `lavish-axi` (Node >= 22; `npm i -g lavish-axi`, or they fall back to `npx -y lavish-axi`).
