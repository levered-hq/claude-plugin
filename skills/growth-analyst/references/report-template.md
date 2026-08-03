# Report example

The report below (Taxfix sign-up, 23 July 2026) is a user-approved worked example — **an example, not a required structure**. The user's explicit instruction: don't overfit to it; what must always hold is the principle behind it, **Minto's Pyramid Principle** — the governing thought answers first (what happened, what it's worth, what to do), every section opens with the claim its data supports, each level of detail answers the question the level above raises, and the groupings are MECE. The layout works *because* it renders the pyramid at this particular optimization's stage and story; a different stage (early run, no winner yet, a validity problem as the headline) should change the rendering, never the pyramid.

## Conventions worth borrowing (defaults, not requirements)

- **Title + subtitle.** `# <Surface> Optimization: Report for <Customer>`, then an italic one-liner: `*<date> · <optimization name> · <status>*`. The `·` separator recurs throughout the document for compact in-cell and in-line lists.
- **Summary.** One bold governing sentence (answer + worth + action), then four bullets whose bold labels match the section names: `**Progress:**`, `**Impact:**`, `**Variants and factors:**`, `**Recommended action:**`.
- **Every section opens with a bold claim sentence**, then at most one or two supporting sentences, then data. E.g. `**The learning phase is over.**`, `**Sign-up conversion is measurably higher on the optimized screen.**`, `**The key insight: the refund-estimate message wins.**`, `**No decision is required this week.**`
- **Progress table is headerless** (`| | |`): label/value rows, values packed with `·` (e.g. `171,292 since launch · 138,188 in the measurement window (10% holdout)`).
- **Measured table** carries a final unlabeled column with a verbal verdict per row: `at threshold of significance`, `no detectable change`, `flat to positive`. Goal metric gets two rows when the windows differ: full measurement window and last four weeks. Sample sizes inline as `(n=13,998)`. Load-bearing numbers bold.
- **Absolute translation** is bolded in prose (`**500 to 700 additional sign-ups per month**`) and its derivation is shown in one sentence (users/month × pp gain), with the CI-implied range stated honestly ("anywhere from roughly zero to 1,400").
- **Modeled estimates** are a bold inline lead (`**Modeled estimates.**`), a small table (estimate / lift / interval) naming the dashboard cards, and — when the baseline-sanity gate fails — an *italic* caveat paragraph (mechanism, direction, "measured figures are authoritative", correction expected).
- **Variant table**: columns `# / Variant / Traffic / Exposures / Rate`; variant as the level tokens joined with `·`; winner row fully bold; original row italic with an `*original:*` prefix; contenders chosen by traffic share. One sentence after it on the baseline's thorough test.
- **Utilities table** grouped by factor (factor cell left empty on continuation rows), levels sorted descending within factor, original level marked `*(original)*` at 0, the winner's levels bold.
- **Interactions**: bold inline lead, the LR stat quoted as χ² with df and p, then a *top-deviations* table (`Combination / vs. additive / n`, deviations as pp with z in parentheses, sub-2 z labeled `directional` inline) — the FULL matrix follows as a compact markdown table (see the Charts bullet below). Close with a `**What the interactions show.**` paragraph.
- **Charts — RETIRED (2026-08-03).** The exemplar below still contains its heatmap image line, but the user has since retired all SVG/image charts from the deliverable: the document is ONE markdown file, and the full masked deviation matrix travels as a compact markdown table (rows = one factor's levels, columns = the other's, cells = deviation in pp, masked cells as `·`) placed after the top-deviations table. Do not generate chart files.
- **Recommended action**: bold opener stating whether a decision is needed now, then a short numbered list (three here), each item starting with a bold imperative phrase and carrying its condition inline (guardrail check, measurement consequence of path a vs. b).
- **Method notes**: after a `---` break, ONE italic paragraph beginning `*Method notes: …*` — inline label, no headline, fine-print register.

## Exemplar (verbatim)

# Sign-up Screen Optimization: Report for Taxfix

*23 July 2026 · Sign-up Screen Value Proposition v2 · live*

## Summary

**The optimization has found its winner. It is worth roughly 500 to 700 additional sign-ups per month, and two more weeks without configuration changes are needed to confirm the result statistically.**

- **Progress:** The model is fully converged at 99.9% progress-to-best. 171,292 users are enrolled, allocation has been stable for four weeks, and results have been directionally consistent since measurement began.
- **Impact:** Measured sign-up lift is +1.0% overall and +1.3% over the last four weeks versus the randomized holdout, which translates to roughly **500 to 700 additional sign-ups per month** at current traffic. The result sits at the threshold of statistical significance and is tightening. The guardrails (booking, intro completion) show no detectable change.
- **Variants and factors:** The refund-estimate message is the strongest element in the test, and the winner pairs it with the progress bar and the *"Continue with"* button. The visual does not need to match the message: a must-match rule would have excluded the winner.
- **Recommended action:** Continue unchanged for about two weeks so the result can reach statistical significance. Then adopt the winner and redirect the traffic to a next optimization built on the learnings.

## Progress

**The learning phase is over.** After 69 days and 171,292 users, the model has fully converged on a single winner and allocation has been stable for four weeks. What remains is confirming the size of the effect, not finding it.

| | |
|---|---|
| Running since | 15 May 2026 (69 days) |
| Users enrolled | 171,292 since launch · 138,188 in the measurement window (10% holdout) |
| Sign-ups tracked | 126,097 |
| Model convergence | 99.9% progress-to-best · winning variant carries 99.4% of optimized traffic |
| Stability | allocation stable and monotone since late June · lift direction consistent across all measurement windows |

## Impact

**Sign-up conversion is measurably higher on the optimized screen.** The optimized arm converts 1.0 to 1.3% better than the randomized holdout, which corresponds to roughly **500 to 700 additional sign-ups per month** at current traffic. Booking and intro completion show no detectable change.

Measured against the randomized holdout, per user (window: since 31 May):

| Metric | Holdout | Optimized | Lift | 95% CI | |
|---|---|---|---|---|---|
| **Sign-up** (goal), since 31 May | 73.14% (n=13,998) | 73.88% (n=124,190) | **+1.01%** | [−0.04%, +2.07%] | at threshold of significance |
| **Sign-up** (goal), last 4 weeks | 74.05% (n=8,375) | 75.05% (n=74,192) | **+1.34%** | [+0.00%, +2.68%] | at threshold, tightening |
| Booking (guardrail) | 19.29% (n=14,029) | 19.15% | −0.73% | [−4.30%, +2.84%] | no detectable change |
| Intro completed (guardrail) | 63.71% (n=14,029) | 64.31% | +0.94% | [−0.38%, +2.25%] | flat to positive |

The recent window is the better guide to what the converged system delivers today, and the trend is upward as the optimization concentrated traffic on its winner. The monthly figure derives from roughly 69,000 optimized users per month multiplied by the measured gain of 0.7 to 1.0 percentage points. The confidence intervals allow anywhere from roughly zero to 1,400.

**Modeled estimates.** These are the model's forward-looking view and correspond to the *Lift (now)* and *Lift (best variant)* cards on the dashboard's Model tab:

| Estimate | Lift | 95% interval |
|---|---|---|
| Current policy vs. original screen | +5.8% | [+4.8%, +6.8%] |
| Best variant (ceiling) vs. original screen | +5.8% | [+4.8%, +6.8%] |

*Caveat: these estimates are currently overstated. The model's baseline reference still reflects the earlier, lower base rate, while sign-up rates have risen seasonally, which temporarily inflates the modeled lift. The measured figures above are authoritative. A model update correcting this is in progress, and these estimates are expected to come down toward the measured range when it deploys.*

## Variants and factors

**The key insight: the refund-estimate message wins.** Telling users their estimated refund is the strongest single element in the test, worth +1.8pp against the original copy and ahead of every alternative framing (trust, loss aversion, task descriptions). The winner pairs it with the progress bar and the "Continue with" button and converts exactly as the utilities predict, measured on 36,913 exposures. A second finding: the visual does not need to match the message, and restricting designs to matched pairs would have excluded the winner at a cost of roughly 0.9pp.

**Winning variant and contenders** (cumulative, event-level):

| # | Variant | Traffic | Exposures | Rate |
|---|---|---|---|---|
| **67** | **continue_with · refund_stat_estimate · progress_bar** | **99.4%** | 26,799 | **76.6%** |
| 42 | continue_with · task_signup_with_trust · progress_bar | 0.3% | 2,605 | 75.1% |
| 68 | continue_with · refund_stat_estimate · star_badge | 0.1% | 2,674 | 74.6% |
| 52 | continue_with · progress_sunk_cost · progress_bar | 0.1% | 1,809 | 74.2% |
| 1 | *original: sign_up_with · task_signup · none* | 0.0% | 29,981 | 72.3% |

The original screen received a thorough test: more exposures than any variant except the winner, and its probability of being the best design is 0%.

**Factor-level utilities** (average effect on sign-up rate vs. the original level; model estimates):

| Factor | Level | Utility |
|---|---|---|
| Button label | continue_with | **+1.26pp** |
| | sign_up_with *(original)* | 0 |
| Message | refund_stat_estimate | **+1.80pp** |
| | task_signup_with_trust | +1.34pp |
| | loss_aversion | +1.33pp |
| | refund_forward | +1.21pp |
| | progress_sunk_cost | +0.96pp |
| | trust_security | +0.22pp |
| | task_signup *(original)* | 0 |
| Visual | progress_bar | **+0.72pp** |
| | none *(original)* | 0 |
| | star_badge | −0.55pp |
| | refund_illustration | −0.84pp |
| | shield_illustration | −1.07pp |

**Interaction effects.** Levels interact: a combination's value can differ from the sum of its parts (likelihood ratio test on raw per-user data: χ² = 100.7, df = 34, p < 0.0001). The largest deviations among well-served message and visual pairings, aggregated over button label:

| Combination | vs. additive | n |
|---|---|---|
| refund_forward + shield illustration | **−2.4pp** (z = −2.6) | 2,228 |
| refund_forward + no visual | +1.8pp (z = +2.6) | 4,287 |
| refund_stat_estimate + no visual | −1.3pp (z = −2.0, directional) | 4,205 |
| refund_stat_estimate + star badge | +1.1pp (z = +1.8, directional) | 5,248 |

![Message by visual interaction matrix](taxfix-interaction-heatmap.svg)

**What the interactions show.** Thematic matching contributes at most a small bonus: a matched-pair term fitted across all combinations is +0.3 to +1.2pp depending on the construction, and every well-served matched pairing sits at or slightly above its additive prediction. Individual pairings still vary: the refund-forward message performs best with no visual and worst next to the shield illustration, so a new combination deserves validation on its own traffic. The winning pairing converts as its utilities predict, and its advantage is element strength.

## Recommended action

**No decision is required this week.** The plan is to let the system run two more weeks so the result can reach significance, then adopt the winner and apply the learnings to the next optimization.

1. **Continue unchanged for about two weeks.** The system is converged, and every additional day of data narrows the confidence interval around a lift figure currently at the threshold of significance. A configuration change now would end the current comparison and start the measurement period over.
2. **Then adopt the winner.** Measured guardrails show no detectable change, and the dashboard guardrail view should be confirmed green as the final check. There are two paths. Path (a) leaves the optimization running: the winner already receives 99.4% of traffic automatically, no engineering is required, and the holdout continues to measure the lift. Path (b) hard-codes the variant in the app and ends the optimization, which also ends measurement. Path (a) is preferable until the next optimization is ready to use this traffic.
3. **Reinvest the traffic in a next optimization built on the learnings:** drop decorative illustrations entirely, keep the message and progress-cue pairing, and apply the every-element-adds-new-information rule to the next surface in the funnel.

---

*Method notes: all lift figures are per user versus the randomized 10% holdout, which always sees the original screen. Sign-up is counted within 24 hours of first exposure. Booking and intro completion are counted unbounded from first exposure, and recent cohorts' bookings are still maturing, which affects both arms equally. Guardrails are reported on the full measurement window only, because booking converts rarely and matures slowly, so a four-week cut would be uninformatively noisy. The measurement window starts 31 May, when the holdout moved to its final 10% configuration, and earlier data is excluded from lift figures by design. Enrollment and sign-up totals cover the full run since 15 May.*
