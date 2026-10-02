# Report example

The report below (sign-up screen, 6 August 2026) is a user-approved worked example — **an example, not a required structure**. It supersedes the 23 July 2026 exemplar and folds in the 2026-08-06 rulings (section rename, embedded snapshots, bulleted findings, three-sentence method notes). **It is fictionalized: the customer name, optimization ID, and every number are altered; the structure, register, and density are as approved.** The user's explicit instruction: don't overfit to it; what must always hold is the principle behind it, **Minto's Pyramid Principle** — the governing thought answers first (what happened, what it's worth, what to do), every section opens with the claim its data supports, each level of detail answers the question the level above raises, and the groupings are MECE. The layout works *because* it renders the pyramid at this particular optimization's stage and story; a different stage (early run, no winner yet, a validity problem as the headline) should change the rendering, never the pyramid.

## Conventions worth borrowing (defaults, not requirements)

- **Title + subtitle.** `# <Surface> Optimization: Report for <Customer>`, then an italic one-liner: `*<date> · <optimization name> · <status>*`. The `·` separator recurs throughout the document for compact in-cell and in-line lists.
- **Summary.** One bold governing sentence (answer + worth + action), then four bullets whose bold labels match the section names: `**Progress:**`, `**Impact:**`, `**What wins and why:**` (renamed from "Variants and factors", user ruling 2026-08-06), `**Recommended action:**`.
- **Every section opens with a bold claim sentence**, then at most one or two supporting sentences, then data. E.g. `**The learning phase is over.**`, `**Sign-up conversion is measurably and significantly higher on the optimized screen.**`, `**The key insight: the refund-estimate message wins, on element strength.**`, `**A decision is available now: the winner is confirmed and can be adopted.**`
- **Multi-finding passages are bullets, not paragraphs (user ruling 2026-08-06):** the key-insight opener and "What the interactions show" render as a bold claim line followed by one-finding-per-bullet, each a single crisp sentence (two only when the second states the consequence).
- **Progress table is headerless** (`| | |`): label/value rows, values packed with `·` (e.g. `184,730 since launch · 158,940 in the measurement window (10% holdout)`).
- **Measured table** carries a final unlabeled column with a verbal verdict per row: `statistically significant`, `at threshold of significance`, `no detectable change`. Goal metric gets two rows when the windows differ: full measurement window and the converged-allocation window. Sample sizes inline as `(n=15,880)`. Load-bearing numbers bold.
- **Absolute translation** is bolded in prose (`**300 to 450 additional sign-ups per month**`) and its derivation is shown in one sentence (users/month × pp gain), with the CI-implied range stated honestly ("the confidence intervals allow roughly 130 to 780").
- **Modeled estimates** are a bold inline lead (`**Modeled estimates.**`), a small table (estimate / lift / interval) naming the dashboard cards, and — when the baseline-sanity gate fails — an *italic* caveat paragraph (mechanism, direction, "measured figures are authoritative", correction expected).
- **Variant table**: columns `# / Variant / Traffic / Exposures / Rate`; variant as the level tokens joined with `·`; winner row fully bold; original row italic with an `*original:*` prefix; contenders chosen by model estimate. One sentence after it on the baseline's thorough test and the traffic-column basis (share of optimized traffic).
- **Variant snapshots (user rulings 2026-08-06)**: after the variant table, embed exactly two platform screenshots — the **winner** and the **original/baseline** — **side by side in a two-column GFM table** (header row = italic captions with variant number + levels, body row = the images), **embedded as base64 `data:image/png` URIs** so the single .md shows them on its own: no sidecar files, nothing to click, no Levered login needed by recipients. Then one sentence linking to the optimization in Levered (`https://app.levered.dev/optimizations/<id>#results`). No contender images.
- **No all-variants appendix**: embedding every variant's snapshot in an appendix was tried and rejected (user ruling 2026-08-06, "too much"). The two body snapshots plus the optimization link are the report's entire visual footprint.
- **Utilities table** grouped by factor (factor cell left empty on continuation rows), levels sorted descending within factor, original level marked `*(original)*` at 0, the winner's levels bold.
- **Interactions**: bold inline lead, the LR stat quoted as χ² with df and p, then a *top-deviations* table (`Combination / vs. additive / n`, deviations as pp with z in parentheses, sub-2 z labeled `directional` inline), then the FULL masked deviation matrix as a compact markdown table (rows = one factor's levels, columns = the other's, cells = deviation in pp, masked cells as `·`). Close with the bulleted `**What the interactions show: <claim>.**` block.
- **Context effects** (only when the model has context factors; last block of *What wins and why*): bold inline lead with the claim, one table per context factor (`Level / Users / Holdout / Optimized / Lift / 95% CI / Winner / Winner's traffic`), one sentence on whether lift differs between levels, then the bulleted `**What context added: <claim>.**` block: the model's finding first (labeled *model estimate*), then the empirical cross-check with its coverage, then the consequence. Lift per level is measured; what context added is model-led, and a null result reads "no benefit detected so far". The Summary's *What wins and why* bullet states the verdict in one clause, and Recommended action settles the context factors for the next optimization. The exemplar below includes the block for a model with one context factor.
- **Charts — RETIRED (2026-08-03).** No SVG/image charts anywhere in the deliverable; evidence that would have been a chart is a compact markdown table or is dropped. The only images are the two variant snapshots.
- **Recommended action**: bold opener stating whether a decision is needed now, then a short numbered list (three here), each item starting with a bold imperative phrase and carrying its condition inline (measurement consequence of path a vs. b). A guardrail that moved appears inside the adoption item as the trade-off the customer accepts, stated in per-user units; guardrails are health metrics and never make an item conditional or add a review item of their own.
- **Method notes**: after a `---` break, ONE italic paragraph beginning `*Method notes: …*` — inline label, no headline, fine-print register. Essentials only, about three sentences (user ruling 2026-08-06): counting basis + windows, measurement start + why, table-comparability caveat; no methodology narration.

## Exemplar (fictionalized; the two data URIs are abbreviated here — real reports embed the full base64)

# Sign-up Screen Optimization: Report for Formora

*6 August 2026 · Sign-up Screen Value Proposition v2 · live*

## Summary

**The optimization has found its winner and the result is now statistically significant: sign-up conversion is 1.4 to 1.9% higher on the optimized screen, worth roughly 300 to 450 additional sign-ups per month at current traffic, and the winner is ready to adopt.**

- **Progress:** The model is fully converged at 100% progress-to-best and the winning variant has carried over 99% of optimized traffic since 22 July. 184,730 users are enrolled, and the lift direction has been consistent across all measurement windows.
- **Impact:** Measured sign-up lift is **+1.4%** on the full measurement window and **+1.9%** since allocation converged, both statistically significant versus the randomized holdout. That translates to roughly **300 to 450 additional sign-ups per month** at current traffic. Intro completion is up +1.2%, at the threshold of significance; booking shows no detectable change.
- **What wins and why:** The refund-estimate message is the strongest element in the test, and the winner pairs it with the progress bar and the *"Continue with"* button. The winner's advantage is element strength: it combines the best level of every factor. The same variant wins on both platforms, and no benefit from considering context has been detected.
- **Recommended action:** Adopt the winner by leaving the optimization running, which requires no engineering and keeps the holdout measuring. Reinvest attention in a next optimization built on the learnings.

## Progress

**The learning phase is over and the confirmation phase has completed.** After 83 days and 184,730 users, the model is fully converged on a single winner, allocation has been stable for two weeks, and the measured result has reached statistical significance.

| | |
|---|---|
| Running since | 15 May 2026 (83 days) |
| Users enrolled | 184,730 since launch · 158,940 in the measurement window (10% holdout) |
| Sign-ups tracked | 131,205 |
| Model convergence | 100% progress-to-best · winning variant carries 99.1% of optimized traffic |
| Stability | allocation stable since 22 July · lift direction consistent across all measurement windows |

## Impact

**Sign-up conversion is measurably and significantly higher on the optimized screen.** The optimized arm converts 1.4 to 1.9% better than the randomized holdout, which corresponds to roughly **300 to 450 additional sign-ups per month** at current traffic. Intro completion moves with it; booking shows no detectable change.

Measured against the randomized holdout, per user (window: since 31 May):

| Metric | Holdout | Optimized | Lift | 95% CI | |
|---|---|---|---|---|---|
| **Sign-up** (goal), since 31 May | 67.94% (n=15,880) | 68.89% (n=143,060) | **+1.40%** | [+0.52%, +2.28%] | statistically significant |
| **Sign-up** (goal), since 22 July | 70.61% (n=5,530) | 71.98% (n=50,870) | **+1.94%** | [+0.55%, +3.33%] | significant, converged allocation |
| Intro completed (guardrail) | 60.13% (n=15,880) | 60.82% | +1.15% | [+0.09%, +2.20%] | positive, at threshold of significance |
| Booking (guardrail) | 19.72% (n=15,880) | 19.73% | +0.05% | [−2.75%, +2.85%] | no detectable change |

The window since 22 July is the better guide to what the converged system delivers today. The monthly figure derives from roughly 33,000 optimized users per month at August traffic multiplied by the measured gain of 1.0 to 1.4 percentage points; the confidence intervals allow roughly 130 to 780. Traffic is seasonal: July volumes ahead of the filing deadline were about five times higher, and the same lift is worth proportionally more whenever traffic returns to those levels.

**Modeled estimates.** These are the model's forward-looking view and correspond to the *Lift (now)* and *Lift (best variant)* cards on the dashboard's Model tab:

| Estimate | Lift | 95% interval |
|---|---|---|
| Current policy vs. original screen | +5.9% | [+5.2%, +6.6%] |
| Best variant (ceiling) vs. original screen | +5.9% | [+5.2%, +6.6%] |

*Caveat: these estimates are currently overstated. The model's baseline reference still reflects the earlier, lower base rate, while sign-up rates have risen seasonally, which temporarily inflates the modeled lift. The measured figures above are authoritative. A model update correcting this is in progress, and these estimates are expected to come down toward the measured range when it deploys.*

## What wins and why

**The key insight: the refund-estimate message wins, on element strength.**

- Telling users their estimated refund is the strongest element in the test: +1.6pp vs. the original copy, ahead of every alternative framing (trust, loss aversion, task descriptions).
- The winner combines the best level of every factor and converts within 0.6pp of what the element effects predict (68,420 exposures).
- Pairings matter only at the margins, and their direction is message-specific (see interaction effects below).

**Winning variant and contenders** (cumulative over the full run):

| # | Variant | Traffic | Exposures | Rate |
|---|---|---|---|---|
| **67** | **continue_with · refund_stat_estimate · progress_bar** | **99.1%** | 68,420 | **71.6%** |
| 68 | continue_with · refund_stat_estimate · star_badge | 0.0% | 2,110 | 68.3% |
| 42 | continue_with · task_signup_with_trust · progress_bar | 0.0% | 2,085 | 68.9% |
| 52 | continue_with · progress_sunk_cost · progress_bar | 0.0% | 1,430 | 67.9% |
| 1 | *original: sign_up_with · task_signup · none* | 0.0% | 28,650 | 67.1% |

The original screen received a thorough test: more exposures than any variant except the winner, and its probability of being the best design is 0%. Traffic is the current share of optimized traffic; the holdout separately continues to see the original screen.

**Variant snapshots** (as served in the app):

| *Winner — variant 67: "Continue with" · refund estimate message · progress bar* | *Original — variant 1: "Sign up with" · task description · no visual* |
|---|---|
| ![Variant 67 — winner](data:image/png;base64,…) | ![Variant 1 — original](data:image/png;base64,…) |

Snapshots of [all 70 variants are available on the dashboard](https://app.levered.dev/optimizations/<optimization-id>#results).

**Factor-level utilities** (average effect on sign-up rate vs. the original level; model estimates):

| Factor | Level | Utility |
|---|---|---|
| Button label | continue_with | **+1.05pp** |
| | sign_up_with *(original)* | 0 |
| Message | refund_stat_estimate | **+1.62pp** |
| | task_signup_with_trust | +1.10pp |
| | loss_aversion | +1.06pp |
| | refund_forward | +1.03pp |
| | progress_sunk_cost | +0.76pp |
| | trust_security | +0.12pp |
| | task_signup *(original)* | 0 |
| Visual | progress_bar | **+0.58pp** |
| | none *(original)* | 0 |
| | star_badge | −0.79pp |
| | refund_illustration | −0.87pp |
| | shield_illustration | −1.08pp |

**Interaction effects.** Levels interact: a combination's value can differ from the sum of its parts (likelihood ratio test on raw per-user data, message × visual with week and button label controlled: χ² = 58.9, df = 24, p < 0.0001). The largest deviations among well-served message and visual pairings, aggregated over button label:

| Combination | vs. additive | n |
|---|---|---|
| refund_forward + no visual | **+4.0pp** (z = +5.8) | 3,210 |
| loss_aversion + no visual | +2.6pp (z = +3.0) | 2,150 |
| trust_security + shield illustration | +2.4pp (z = +5.7) | 8,970 |
| refund_stat_estimate + no visual | **−1.9pp** (z = −2.4) | 2,480 |
| task_signup_with_trust + shield illustration | +1.7pp (z = +3.0) | 4,820 |
| loss_aversion + progress bar | −0.9pp (z = −2.4) | 11,040 |

The full deviation matrix (observed minus additive prediction, pp; cells with fewer than 2,000 users masked as ·):

| Message \ Visual | none | progress_bar | refund_illust. | shield_illust. | star_badge |
|---|---|---|---|---|---|
| loss_aversion | +2.6 | −0.9 | · | · | · |
| progress_sunk_cost | +1.3 | −1.2 | · | · | · |
| refund_forward | +4.0 | −0.1 | +0.6 | · | +1.3 |
| refund_stat_estimate | −1.9 | −0.6 | +0.7 | −1.1 | −0.1 |
| task_signup | · | · | · | · | · |
| task_signup_with_trust | · | +0.1 | · | +1.7 | · |
| trust_security | · | · | · | +2.4 | · |

**What the interactions show: pairing effects are message-specific, and no uniform matching rule holds.**

- Standalone value messages do best with no visual: refund_forward +4.0pp and loss_aversion +2.6pp above their additive prediction.
- The winning refund-estimate message is the exception: it under-delivers alone (−1.9pp) and needs its progress-bar cue. Reuse message and cue as one unit.
- The positive trust × shield cells are floor effects, two weak elements hurting less than predicted while still trailing the leaders. No design recommendation follows.
- A new pairing therefore deserves validation on its own traffic.

**Context effects.** The optimization considered one context factor, platform, and the result holds on both platforms. Measured against the randomized holdout within each level, per user (window: since 31 May):

| Platform | Users | Holdout | Optimized | Lift | 95% CI | Winner | Winner's traffic |
|---|---|---|---|---|---|---|---|
| ios | 64% | 69.80% (n=10,160) | 70.85% (n=91,560) | +1.50% | [+0.41%, +2.59%] | variant 67 | 99.3% |
| android | 36% | 64.63% (n=5,720) | 65.40% (n=51,500) | +1.19% | [−0.29%, +2.67%] | variant 67 | 98.7% |

Sign-up rates are higher on iOS in both arms, and the lift shows no detectable difference between the platforms (heterogeneity test: Q = 0.11, df = 1, p = 0.74).

**What context added: no personalization benefit has been detected.**

- The model finds no platform effect on which variant wins (context importance 0.00, *model estimate*), and it serves variant 67 to 99% of traffic on both platforms.
- The observed data agree: among the four variants with enough users on both platforms, the same one leads on each, and there is no evidence that any variant performs differently by platform (day-controlled test: F(3, 139,870) = 0.62, p = 0.60). This comparison is a cross-check and is not randomized.
- An optimization without the platform factor would therefore most likely have reached the same design.
- Considering a context factor slows learning, because the model has to learn each level separately. Platform can be left out of the next optimization.

## Recommended action

**A decision is available now: the winner is confirmed and can be adopted.** The measured lift is statistically significant, the guardrails show no trade-off, and the system has already routed essentially all optimized traffic to the winner.

1. **Adopt the winner by leaving the optimization running.** Path (a) keeps serving through the platform: the winner already receives 99.1% of optimized traffic, no engineering is required, and the 10% holdout continues to measure the lift. Path (b) hard-codes the variant in the app and ends the optimization, which also ends measurement. Path (a) is preferable until the next optimization is ready to use this traffic. Adopting carries no measured trade-off: intro completion is positive and booking shows no detectable change.
2. **Keep the configuration unchanged while the optimization runs.** The measurement window restarts whenever the configuration changes, and the current window is what carries the statistical confirmation.
3. **Reinvest the traffic in a next optimization built on the learnings:** lead with the refund estimate, keep it paired with its progress cue as one unit, prefer no visual when the message carries the value on its own, and skip decorative illustrations, which cost 0.8 to 1.1pp wherever they appeared. Leave platform out as a context factor, since no benefit was detected here and the next optimization learns faster without it.

---

*Method notes: all lift figures are per user versus the randomized 10% holdout, which always sees the original screen; sign-up is counted within 24 hours of first exposure, guardrails unbounded. The measurement window starts 31 May, when the holdout reached its final 10% configuration; enrollment and sign-up totals cover the full run since 15 May. Variant rates in the contender table are cumulative over the full run and therefore not directly comparable to the windowed lift figures.*
