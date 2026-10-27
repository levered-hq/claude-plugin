# Factor design

The deeper design rules: the knowledge base, the reward, coherent factors, the user's own hypotheses, and a new optimization next to a running one. Phase 1 has what a first design needs; read this when a design gets complicated.

## The knowledge base — best effort

The org may have connected analytics (PostHog, Mixpanel), synced Notion pages or uploaded documents, each with a short summary. Check it before drafting factors, silently, and never let it block you: if the user isn't signed in, it fails — skip it and say nothing.

```bash
levered knowledge list --json
levered knowledge view <document-id>
```

Use only documents with `use_as_knowledge: true`; a `null` summary means it isn't summarized yet, not that it's empty. Read the summaries, then the full text of the two or three that bear on this optimization (uploaded PDFs by ID). **Analytics** (`posthog`, `mixpanel`) say what to optimize: the real funnels and where visitors drop off — prefer a surface with a measured leak. **Research, brand and pricing docs** (`notion`, `upload`) say what's true: prices, guarantees, customer language. Knowledge informs the proposal; the user still approves it.

## The reward first

The goal decides which changes make sense, so settle it before any factor. In a first design it's the goal the user chose in phase 1. Later, or when that goal can't be measured, **propose a best guess** rather than an empty question: the deepest conversion the code already records that still has the volume to learn ([sizing.md](sizing.md)), in one line with its reason. When conversions pull in opposite directions, recommend one, with the trade-off. Settle it from its meaning, never by matching names in `levered metrics list`; which Levered metric implements it is phase 3's job.

## Factors

Choose the changes as phase 1 §4 says. Then:

**Every combination must be coherent.** A visitor must never be served a variant whose levels contradict each other, so cut the factors to make that impossible by construction:

- **Independent levers** — any combination makes sense: keep them as **separate factors**. The model mixes them, learns each cheaply and *discovers* which pairings work.
- **Coupled dimensions** — only some pairs tell one story: fold them into **one composite factor** whose levels are the pre-paired options (`<factor>: "<angle A, part 1 + part 2>" / "<angle B, part 1 + part 2>"`). This also cuts the version count.

**The test:** mentally expand the full grid and read each cell as a real screen. If any cell is incoherent, recompose. Within that, keep factors as independent as you can: over-factoring only learns a bit slower and is visible; wrongly merging hides the pairing that would have won. Compose exactly enough for coherence, no more.

Excluding combinations is a last resort for clashes no factor cut avoids: `--excluded-combinations '[{"<factor>":"<level>","<other factor>":"<level>"}]'` on `levered optimizations create`. The baseline can't be excluded, and at least two variants must remain.

**Every level presents only what is true.** Each claim, number, price, guarantee, feature, quote, rating and description of what the product does must exist in the code, on the live site, or in an opted-in knowledge document — and a document that contradicts a claim rules it out. Reframing, reordering, showing or hiding real content is the space to work in. If you don't know whether something is real, ask the user, and leave out what you can't confirm. When a level rests on a knowledge document, name the document in the proposal.

Present a later design the way phase 1 §5 presents the first: the problems it answers, then the changes, the bet in plain words, the evidence in a clause, each step with its card.

## The user's own hypotheses

They know things you can't see, so work their hypothesis with them:

1. **Sharpen it** into a belief about the visitor: who is stopped or moved, by what, and how we'd know.
2. **Look for evidence** for and against it in the code, the page, the knowledge base and the research; say what you found, once.
3. **Check every claim it relies on is true**; if it needs an untrue one, propose the closest true version.
4. **If you still disagree,** don't argue twice: offer it as a competing level and let live traffic settle it.
5. **Record it as theirs:** `source: user` on the level, in the design and in `changes/<n>.md`.

Ideas they add to `brief.md`'s Ideas section get the same treatment.

## Add to a running optimization, or start a new one?

If an idea changes **the same decision, for the same visitors, judged by the same reward**, it belongs in that optimization — a **level** if it's another option for something already varied, a **factor** if it's a new dimension that works with every existing level. Otherwise it's a **new optimization**.

- A live optimization can't take new levels or factors yet (a draft can: `levered optimizations update <id> --design-factors`).
- A **shipped** optimization still serves its winner; resume it (`--status live`) rather than starting a second one. A **completed** one frees its surface.
- Two optimizations on the same visitors at the same step interfere: don't overlap a running one.
- Another option on a change costs data; another change costs little data but multiplies the versions to review ([sizing.md](sizing.md)). Prefer the fewest additions the traffic can settle.

Say which you chose and why in the design.
