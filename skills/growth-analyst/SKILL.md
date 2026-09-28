---
name: growth-analyst
description: Read and explain optimization results as a customer-ready document — which variant is winning and why, how much lift Levered is delivering vs. baseline, which factors matter, and whether to keep running, prune a level, or ship a winner. The deliverable is always fit to forward to the customer; analyst detail goes in a chat addendum. Use whenever the user asks how an optimization or experiment is performing, wants a results summary or stakeholder report, asks about lift, winning variants, factor importance, or cross effects — for one optimization or the whole portfolio.
---

# Growth Analyst

The user wants to understand how an optimization is performing. Pull the live results from the Levered platform, read the model, and explain it in plain language — then recommend the highest-leverage next move.

Act autonomously: run the `levered` commands yourself and interpret the output. The only thing to ask of the user is `levered login` (it needs a browser). Default to **production data** — these are real, live experiments.

**Speed contract: a repeat report takes ~2 minutes; a first report ~5.** The whole data layer is ONE CLI call (`report-data`) plus ONE script run (`scripts/report_calcs.py`) — never re-derive their numbers with ad hoc warehouse SQL, and never re-discover join keys, window starts, or outcome weights that the pack and the notes file already carry. `levered warehouse query` is a last resort, reserved for a fired validation gate or a question the cube genuinely cannot answer.

Reference files carry the deep material. **Do not read them upfront.** Each has a trigger:

- [references/reading-the-model.md](references/reading-the-model.md) — read only when a validation gate fires, when measured and modeled seriously disagree, or on a first report if any modeled figure will headline.
- [references/cross-effects.md](references/cross-effects.md) — read only when you are about to narrate an interaction as a finding (a significant test, or a claim beyond "effects are additive").
- [references/report-template.md](references/report-template.md) — read before writing a FIRST report for an optimization. In update mode the prior report already carries the approved register; skip it.

The essentials from those files, as a checklist (enough for a clean run; the files hold the reasoning):

- `weight` and `P(best)` are one number in two scalings (`weight = prob_best × (1 − holdout share)`); quote one. Customer documents state traffic as share of **optimized** traffic.
- `results` carries three lift figures: **measured** (`primary_metric_vs_holdout` — the only randomized number; it leads), policy ("Lift (now)"), and ceiling ("Lift (best variant)") — the last two are model estimates and are always labeled as such.
- The baseline-sanity gate decides how modeled figures present: PASS → normally (still labeled); FAIL → with the stale-baseline caveat, out of the Summary, never headlining, and never a "corrected" hybrid number.
- Variant `rate` is per exposure and lifetime-cumulative; windowed lift figures are per user. Never place them side by side as comparable.
- Interactions: a positive term between two negative main effects is saturation (a floor), not synergy; uniformly-signed coefficient tables are an alarm, not a finding; |z| < 2 deviations are *directional*; never re-rank variants from an interaction model.
- "Statistically significant" only when it has held for a week or more; while it oscillates, write "at the threshold of significance".
- Context: a model with context factors always gets a Context block, including when the answer is "context added nothing". Two separate questions, never merged: how results **varied** by context (measured lift per level, each against its own holdout) and what considering context **added** (the personalization value: what serving each level its own winner is worth over serving everyone the single best variant). A lift that differs by level is not a personalization benefit; only a different winner by level is.
- Context evidence has two bases, and each question has its own. **Lift per level is measured** (optimized vs. holdout is randomized within every level), so it leads there. **What context added is led by the model** (context importance today; the per-context posterior once #333 ships), because variant-by-level comparisons inside the optimized arm are not randomized: the model chose who saw what, adaptively. The script's empirical winner comparison is a labeled cross-check, never the headline.
- A modeled zero means "no personalization benefit detected so far", never "none exists": the model's context terms are regularized toward zero and the model is grading its own context-awareness. Context levels differ in baseline value, so compare lifts across levels, never raw values.

## Workflow

### 1. Preflight — auth first

Check auth before anything else, so a needed login surfaces immediately:

```bash
levered env use prod && levered whoami
```

Not authenticated → ask the user to run `levered login` (the one browser step) and stop until they have. If the CLI is missing: `curl -fsSL https://cli.levered.dev/install.sh | bash`, then `~/.levered/bin/levered`.

### 2. Locate the optimization and its notes

`levered optimizations list` resolves a name or keyword to an id (confirm if ambiguous; `all`/`portfolio` → see Portfolio reads).

Per-optimization state lives in `~/.levered/reports/<optimization-id>/`:

- `notes.md` — the analysis recipe: config hash, converged-window start, known quirks (era boundaries, join oddities), decisions from prior runs, last headline numbers.
- `report-latest.md` — the last delivered report.
- `snapshots/` — cached variant PNGs.

Read `notes.md` and `report-latest.md` if they exist. They are what makes the repeat path fast — trust them unless the config hash says otherwise.

### 3. Pull — one call

```bash
levered optimizations report-data <id> > pack.json
```

One JSON document: optimization + model config **including the reward's outcome weights**, results (variants, importance, modeled + measured lift, time series), the measured daily series (`holdout_daily`), the **outcome mix cube** (users per day × arm × variant × matched outcome, split by the context at first exposure when the model has context factors), guardrails, and the model's lift history. Surfaces fail independently — a `{"error": …}` under one key is a note for the addendum, not a reason to stop.

If the subcommand is unknown, invoke the CLI twice (it self-updates and applies on the next run). Still missing → legacy path: `show --json`, `results --json`, `progress`, `guardrails`, `lift-history`, all in one parallel batch, and get outcome weights from the `model_config` in `show`'s raw response.

### 4. Compute — one script

```bash
python3 <skill-dir>/scripts/report_calcs.py pack.json          # add --since YYYY-MM-DD to override the converged window
```

Stdlib-only; prints every number the report needs, each labeled with its basis:

- **CONFIG** — factors, outcome weights, windows, and a `config_hash` for update-mode comparison.
- **VALIDATION** — the gates, computed: holdout share by day (step-change gate), enrollment reconciliation (cube vs published), and the baseline-sanity verdict (PASS/FAIL with the gap as a fraction of modeled lift).
- **MEASURED** — the published lift (quote it verbatim; it is what the dashboard shows) plus full-window and converged-window recomputes on the same estimand from `holdout_daily`.
- **GUARDRAILS / MODELED / VARIANTS** — as published, formatted for the tables.
- **OUTCOME MIX** — per-outcome shares by arm with CIs (full + converged window) and the monthly-traffic figure for the absolute translation.
- **FACTOR UTILITIES** and **INTERACTIONS** — model-estimate utilities, and a day-controlled F-test with the full observed-vs-additive deviation matrix from the cube.
- **CONTEXT** (only when the model has context factors) — per context factor: the model's context importance, measured lift per level with CI (full + converged window) and a heterogeneity test, and, as an **empirical cross-check** (not randomized, labeled as such), the winner per level against the context-blind winner with the share of traffic the model serves it, the day-controlled variant × context test, the personalization value with its CI, and how many variants had enough users in every level to be compared at all.

**Gate handling.** All gates clean → proceed. A gate FIRED → this is now the finding that shapes the document: read [references/reading-the-model.md](references/reading-the-model.md), investigate (this is where `levered warehouse query` is legitimate), and apply the exclusions/softened claims the reference prescribes. A fired gate always lands in the analyst's addendum first.

**Story verification still applies.** The script hands you both constructions for the usual claims (model utilities AND raw deviations; published AND recomputed lift). A claim the two constructions do not both support is downgraded to a named observation or cut. Claims inherited from a prior report are checked against the fresh numbers before reuse.

### 5. Choose the mode

**Update mode** — when `report-latest.md` exists, the `config_hash` matches `notes.md`, and no gate fired. Refresh the numbers inside the prior report's structure, re-examine only claims the fresh numbers moved (allocation shifts, a guardrail changing status, significance crossing a threshold), and say in the addendum what moved since last time. Skip the reference files; reuse cached snapshots. This is the ~2-minute path.

**Full mode** — first report, config hash changed, a gate fired, or the user asked for a fresh look. Read [references/report-template.md](references/report-template.md) before writing; the deep mandates (interaction narrative with cross-effects.md, story verification from scratch) run here. This is the ~5-minute path, and it is per optimization, not per report.

### 6. Report — a customer-ready document, always

The deliverable is a document the user can forward to their customer or stakeholders **unchanged**. Everything above is the kitchen; the document is the plate — its rigor shows up as what's *absent*, not as visible apparatus. There is no separate internal report mode: analytical depth the user needs goes in the **analyst's addendum** (end of this section), never in the document.

**Structure: Summary → Progress → Impact → What wins and why → Recommended action → method notes.** [references/report-template.md](references/report-template.md) is a user-approved worked example of the register and density — borrow its conventions (bold-labeled Summary bullets, bold claim openers, compact `·`-joined tables, verdict column, numbered actions, italic fine-print method notes) as sensible defaults, but treat it as an example, not a required structure. The deliverable is ONE markdown file, sent to the user as a file — no SVG or image files (user ruling 2026-08-03); the analyst's addendum stays in chat. **The governing rule — the one thing that is not negotiable — is Minto's Pyramid Principle**:

- **Apex — the governing thought.** The Summary's first line is one bold sentence giving the answer: what happened, what it's worth, what to do.
- **Answer first at every level.** Each section opens with a **bold claim sentence** giving its "so what" (plus at most one supporting sentence), then goes straight to the data.
- **Each level raises the question the level below answers.** If a table doesn't answer a question the opener raised, it belongs elsewhere or nowhere.
- **Groupings are MECE and parallel:** how far along (Progress), how much value (Impact), why (What wins and why), what next (Recommended action).

Section contents (the script's output maps onto these directly):

- **Summary** — one bold governing sentence, then four bullets whose bold labels match the section names; a reader who stops here has the whole story. Modeled figures reach the Summary only when the baseline-sanity gate passed.
- **Progress** — a small headerless table: running since, users enrolled (per user; state full-run and measurement-window counts separately), conversions tracked, model convergence (progress-to-best, winner's share of optimized traffic), allocation stability.
- **Impact** — measured first and authoritative: the lift table (reward + each guardrail × holdout / optimized / lift / 95% CI / verdict), quoting published figures as published; a `pending` guardrail is reported as pending. Wording is symmetric: a guardrail whose CI cannot rule out material harm gets "no detectable change", never "no degradation"; a positive guardrail at p < 0.05 is reported as positive. Follow with **the absolute translation** (the outcome-mix shift × monthly traffic — the sentence stakeholders retell, with an honest range) and then **Modeled estimates** as a labeled table naming the dashboard's *Lift (now)* / *Lift (best variant)* cards — with the stale-baseline caveat paragraph when the gate failed (mechanism, direction, "measured figures are authoritative", correction expected; never an alternative number).
- **What wins and why** — opens with the key insight as a bold claim line plus one-finding-per-bullet (user ruling 2026-08-06). Then: the variant table (winner + top 3 contenders + the baseline as reference row, variant # column, traffic as share of optimized traffic); **exactly two embedded snapshots** side by side in a two-column GFM table — the winner and the original — as base64 `data:image/png` URIs (no sidecar files, no Levered login needed), then one sentence linking to `https://app.levered.dev/optimizations/<id>#results`; no contender images, no all-variants appendix (rejected 2026-08-06). Factor-level utilities (labeled *model estimates*, original level at 0, winner's levels bold). Interaction effects: the test statistic, a top-deviations table where deviations are real, and **the full masked deviation matrix** — a pattern claim ships with its complete evidence. Close with the bulleted "What the interactions show" block; |z| < 2 rows are labeled *directional* and narrated accordingly. When the model has context factors, the section ends with the **Context effects** block (next bullet), and the Summary's *What wins and why* bullet carries its verdict in one clause.
- **Context effects** (last block of *What wins and why*; mandatory whenever the model has context factors) — answers the two questions a customer asks, in this order. (1) **How results varied by context:** one table per context factor with a row per level: share of users, holdout, optimized, lift, 95% CI, winning variant, and the share of that level's traffic the model serves the winner; state the heterogeneity test in one sentence. (2) **What considering context added:** the bulleted "What context added" block. It leads with the model's finding, labeled *model estimate*: the context importance, and whether the model serves a different variant by level. The empirical cross-check follows as supporting evidence and names its coverage (which variants had enough users in every level). The claim is only as strong as both bases allow: both agree on no difference → "no personalization benefit detected so far", with the consequence that context has cost learning speed without buying lift yet; the model finds a difference and the cross-check supports it (significant variant × context test) → quote the benefit and translate it with monthly traffic; the two disagree, or the cross-check covers few variants → say so and claim nothing beyond the direction. A context factor with many levels shows the levels that cover most traffic and groups the rest as "other".
- **Recommended action** — a bold opener stating whether a decision is needed now, then a short numbered list, each item a bold imperative with its condition inline. When the model has context factors, one item settles them for the next optimization: keep a factor whose winner differs by level, and consider dropping one with no detected benefit (the next optimization then learns faster on the same traffic), unless the next test adds elements that plausibly work differently by level. Context factors of a running optimization stay untouched, since a change restarts the measurement window. A ship recommendation names the mechanism and measurement consequence: keep serving through Levered (no engineering, holdout keeps measuring) vs. hard-code and end the optimization (measurement ends too). Always check guardrails before recommending a ship.
- **Method notes** — after a `---` break, ONE italic paragraph beginning `*Method notes: …*`, about three sentences (user ruling 2026-08-06): counting basis and windows, where measurement starts and why, any table-comparability caveat. A mid-run change becomes one neutral clause here, not a story.

Rules that keep it customer-safe:

- **Neutral analyst voice.** As if the customer's own analysts wrote it: no vendor first person, verdicts attributed to the data, arms labeled Optimized vs. Holdout.
- **Open questions are reported as questions answered** — "whether X was an open question going into the test, and the answer is Y". The report informs colleagues; it defeats nobody.
- **Succinct copy, minimal prose.** Tables and short claim sentences. One bold claim sentence plus at most one supporting sentence per section opener; at most one or two sentences after any table. Multi-finding passages are bullets, one finding per bullet.
- **Style: complete sentences, no dashes, affirmative statements.** Every table lead-in is a complete sentence. Ranges in prose read "500 to 700". No figurative idioms. Honest negatives ("no detectable change") keep their negation.
- **No internal machinery.** No issue numbers, no CLI/dashboard discrepancies, no validation narration.
- **Standalone test.** Nothing may require having followed the investigation.
- **Claim strength tracks the data** — including the significance wording rule from the checklist.
- **No charts** (user ruling 2026-08-03). Evidence that would have been a chart is a compact markdown table or is dropped. The only images are the two variant snapshots.

**Snapshots** come from the shipped script (cached; re-fetch only when the winner changed):

```bash
python3 <skill-dir>/scripts/embed_snapshots.py <id> --winner <n> --winner-caption "…" --original 1 --original-caption "…" --out snippet.md
```

A 401 means the session token expired: ask the user to `levered login`, retry once, and on any other failure ship the report with the dashboard link in place of the images (noting it in the addendum) rather than improvising auth.

**The analyst's addendum — to the user in chat, never in the document.** After the document: which gates fired and how they shaped the document, the measured-vs-modeled gap and its diagnosis, anything oscillating, open platform issues, and (in update mode) what moved since the last report. A validity finding outranks a variant finding.

### 7. Save state

After sending the report, write back `~/.levered/reports/<id>/`:

- `notes.md` — config hash, converged-window start, quirks discovered this run, the headline numbers (measured lift + CI, winner, mix shift), date. Keep it under a page; it is a recipe, not a log.
- `report-latest.md` — the delivered document (without the base64 blocks if size is a concern; note the snapshot cache instead).

### 8. Decide the recommendation — it lands in Recommended action

Recommend the **highest-leverage move the evidence supports**:

- **Ship the winner** — clearly ahead, tight interval, adequate exposures. Quote the **measured** lift, never the modeled ceiling.
- **Prune a level** — clearly dragging, tight interval, enough exposures. Name it. **Never prune an index-0 (baseline) level** — it's the measurement anchor.
- **Keep running** — leader still overlaps, or variants under-exposed; say roughly how much more data you'd want. When the bandit has concentrated (weight > ~90% on one variant), exploration is over and the recommendation is usually "change nothing, let the holdout accumulate" — any change restarts that clock.

Surface the structural insight when the analysis reveals one: drop a noise factor, drop a context factor with no detected personalization benefit (in the next optimization, never mid-run), merge redundant levels, consolidate two factors **only on true synergy** (both mains ≥ 0 — see the saturation rule in the checklist), or spin up a follow-up around the dominant factor.

## Principle: present published metrics, analyze the cube

(1) For anything the dashboard already shows — lift, factor importance, users, rates, probability-of-best — quote the value from the pack; never re-derive it (your number will drift from the dashboard and confuse the user). (2) Unpublished insights — windowed cuts, mix shift, interactions — come from the outcome-mix cube via the shipped script, which shares the platform's estimand by construction. Ad hoc `levered warehouse query` analysis is the escalation path for fired gates and questions the cube cannot answer, not the default.

## Scope — what this skill cannot tell you (today)

- **Individual past decisions.** The platform logs the chosen variant per serve, not the per-variant probabilities at that moment.
- **The model's own context-conditional estimates.** The right basis for "what context added" is the per-context posterior (the gain of the best variant per level over the single best variant, per draw, with a credible interval). It needs the context-aware model state that isn't shipped (#333). Until then the modeled evidence is the published context importance, which is a score and not a lift: never convert it into a percentage, and never quote a modeled per-context figure.
- **Context the optimization did not record.** Only configured context factors are in the cube. Other dimensions (platform, country) come from the dashboard's Dimensions card and answer "how did results vary", never "what did context add", because the model did not use them.

## Portfolio reads (`all`)

Lead with a one-row-per-optimization scoreboard: name, status, best lift so far, confidence (tight/wide), one-word call (ship / prune / wait). One `report-data` call per live optimization, in parallel. Offer to drill into any single one with the full report.

## Troubleshooting

- **No results / "still training"** — check `observations <id>` for incoming data and `show <id>` for status; if exposures aren't flowing, hand off to platform setup.
- **`outcome_mix` or `holdout_daily` carries a `warehouse_error`** — the pack's other surfaces still work; report published figures, skip the cube-derived sections, and put the error in the addendum.
- **Model has context factors but the script prints "the cube carries no context dimension"** — the API predates the context cube or served a cached pre-upgrade cube (it refreshes within hours). Report the published context importance, state that the per-context breakdown is not yet available, and put the reason in the addendum; do not rebuild the cube with warehouse SQL unless the user asks for it.
- **Flat lift** — confirm the reward metric fires (`levered metrics preview <id>`) and `anonymous_id` matches between exposures and rewards.
- **Wide intervals everywhere** — early days or too many variants; recommend patience, quote exposure counts.

For deeper concepts: [concepts.md](../levered-platform/concepts.md) and [docs.levered.dev/docs/concepts/optimizations](https://docs.levered.dev/docs/concepts/optimizations).
