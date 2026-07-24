# Cross effects: detecting and interpreting factor interactions

The platform doesn't publish interaction metrics, so deriving them is the analyst's own work — and the part of the report most likely to go confidently wrong. Two methods (screen, then test) and two interpretation traps that have each produced a plausible-but-false narrative in real reports.

This is **design×design** only. Context×design ("wins on mobile, loses on desktop") needs the context-aware model state that isn't shipped yet (#333) — say so rather than guessing.

## Method 1 — screen from the posterior means

From `results` (or `models state`), using per-variant point estimates:

```
interaction(A=a, B=b) = mean(variants with A=a,B=b) − mean(A=a) − mean(B=b) + grand_mean
```

This is double-centered, cheap, and has **no honest uncertainty estimate** — `models state` exposes interval summaries, not draw-aligned samples. Treat it strictly as a *screen*: flag terms that are large relative to the factors' main-effect spreads, and say explicitly they're point estimates. Note also that late in a run these means are the model's shrunken estimates, heavily informed by whatever the bandit still serves — thin cells are model extrapolation, not data.

## Method 2 — test on raw data

When the warehouse is queryable, upgrade the screen to a real test. Pull per-user exposures and conversions with `levered warehouse query` (first exposure per user, the optimization's conversion window), then fit main-effects vs. main-effects-plus-pairwise logistic models and compare by likelihood ratio — **with a time control** (week fixed effects at minimum), because adaptive allocation confounds variant with calendar period. A significant LR statistic says interactions exist; the *sign pattern* of the significant terms is usually the insight.

Even with a significant test, **never re-rank variants from an interaction model**: cells the bandit stopped serving are too thin to predict, and the model extrapolates nonsense into exactly the cells a re-ranking would promote.

## Trap 1 — coding conventions

Interaction coefficients depend on the parameterization. A reference-coded model (terms relative to the baseline levels) and the double-centered screen above (terms relative to the grand mean) express the **same structure with different sign patterns**. "21 of 22 terms negative" in one coding and "mixed signs" in the other is not a contradiction — and comparing individual term signs across the two is meaningless.

The interpretable view that works in any coding: **observed vs. additive-prediction at the variant level.** For a flagged cell, compare its observed rate against what the main effects alone predict. That deviation has a sign, a magnitude in points, and a z-score, and it means the same thing regardless of how the model was parameterized.

## Trap 2 — synergy vs. saturation

A positive interaction term has **two different causes**, and only one supports a "combine these" recommendation:

- **Synergy** — both levels have positive (or at worst neutral) main effects, and the combination beats the sum. This is the only pattern that justifies consolidating two factors into one lever.
- **Saturation** — both levels have *negative* main effects, and the combination is merely *less bad than doubling the damage*. The additive model predicts the harm stacks; in reality the screen can only fail one way at a time, so the term comes out positive. This is a floor effect. It is not evidence the pair works — the combined cell still underperforms.

**Rule: before narrating any positive interaction, look at the two main effects.** Both ≥ 0 → possible synergy, worth surfacing. Both < 0 → saturation; the correct sentence is "the damage doesn't stack," never "these reinforce each other."

Worked example (real): a security-message × shield-illustration cell showed +1.0pp over its additive prediction — but both levels were among the worst in their factors, and the cell still trailed the leaders by ~2.5pp. Calling that "coherence pays" would have been exactly wrong. (The same dataset later falsified an equally attractive story in the opposite direction — see Trap 3.)

Main effects usually dominate; interaction lessons are pairing-specific. A defensible finding names concrete pairings ("message X performs best with no visual and worst next to visual Y"). A sweeping design law ("elements must never repeat each other", "elements must each add new information") needs the FULL masked deviation matrix to survive, and usually doesn't — check every cell the law predicts, not just the cells that inspired it.

## Trap 3 — thin reference cross

Reference-coded interaction coefficients measure every cell against the reference row and column. Under adaptive allocation the reference levels are often exactly the ones the bandit abandoned, so those cells are thin AND era-confounded — and their noise propagates into *every* interaction term. A single anomalous reference-cross cell (e.g. `original_message × illustration` overperforming on 1,200 early-era users) inflates a main effect and pushes the whole column of interaction terms negative. **The symptom is a uniformly-signed z-table** ("21 of 22 terms negative"): real interaction structure is rarely that tidy; contamination is.

Defenses: trust the LR existence tests (coding-invariant); read *pattern* only from observed-vs-additive deviations aggregated over the factor not under study, with thin cells masked (n threshold in the thousands, not hundreds); and treat any story built on reference-coded z-rankings as unverified until the masked matrix reproduces it. Real case: a −5.0z "redundant illustration destroys the message" term dissolved to +0.1pp in the masked aggregate, and the story died with it — caught because the full matrix was visualized instead of the top-4 rows.

Related: never present a single three-factor cell as a two-factor finding. A deviation that appears in one button-label cell and reverses in the other is a three-way effect; quoting the striking cell alone misattributes it to the pair.

## Lead with the story

Classifying the terms is the analysis; it is not the deliverable. The deliverable is **one positive design claim, stated first, with the terms as supporting evidence** — a reader should get the lesson from the opening sentence and be able to stop there. Concretely:

- Open the cross-effects read with the claim ("the refund-forward message performs best on its own and worst next to the shield illustration"), not with a coefficient or a χ².
- Phrase the claim as what to *build*, not what to avoid — "pair the value message with a cue that adds new information" teaches; "never restate the message" only warns.
- Coefficients, z-scores, and the LR statistic go after the claim, sized as evidence. If a term needs classifying as saturation, do it in a parenthetical, not a bullet of its own — the exception must not read at the same weight as the finding.

The failure mode this prevents is real: a term-by-term taxonomy, each bullet anchored on a magnitude, is technically correct and communicates nothing — the reader is left to assemble the story, and mostly won't.

## What to recommend from each pattern

| Pattern | Recommendation |
|---|---|
| A crisp, cell-supported negative pairing | Avoid that specific pairing next iteration; name it, and generalize only if the full masked matrix supports the generalization |
| True synergy (both mains ≥ 0, combo beats sum) | Consider consolidating the two factors into one coherent lever |
| Saturation (both mains < 0, positive term) | Nothing — it's a floor effect; at most note the damage doesn't stack |
| Significant LR but no interpretable pattern | Report that interactions exist and per-level effects don't simply add; don't force a story |
