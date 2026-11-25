# Reading the model

Levered's bandit is a **Bayesian factorization machine** driven by **Thompson sampling**. Its numbers are easy to read wrongly in ways that sound authoritative. This file is the antidote — read it before writing the measured-vs-modeled section of a report.

## Posterior, not point estimate

Every model figure comes from the posterior store: thousands of joint draws from the posterior, queried at runtime. The pack reduces each to `{lo, mid, hi}`, a credible interval and its median; each variant's `reward` in `model.variants` is one. Always carry the uncertainty into the read: a 12% lift with an interval of [−3%, +27%] is not a winner, it's a "keep running." Thin exposures → wide intervals.

## The reference follows the control type

`control_type` on the optimization says what every lift figure is measured against:
- `variant`: the baseline variant, named when the optimization was created (the variant in `results` with `is_baseline`). Lift for any variant is `(p_variant − p_baseline) / p_baseline`. This is why the baseline's levels are never pruned — it's the measurement anchor. The holdout is served the baseline, so it stays well-measured even when the bandit's own weight on it reaches zero.
- `external`: the current version the holdout keeps, which is none of the variants. Holdout users train the model as that version, so the model's lifts are against it, adjusted like every variant's. Model versions trained before that have no current version: their lifts are null, so a day without lift in the history is one of those, not a zero. No variant carries `is_baseline`.
- `none`: an even split of traffic across the variants (below).

## No baseline = even split

A brand-new experience (a new screen, a CRM-triggered flow) has no "what users saw before", so it is created without a baseline: no variant is the original, there is no holdout, and `primary_metric_vs_holdout` is empty. The model then measures the policy against an **even split of traffic across the servable variants** — the counterfactual of picking one at random — on the same posterior draws: `model.policy_lift` is policy vs. even split, `model.ceiling_lift` is the best variant vs. even split, `model.p_beats_reference` is P(policy beats the even split), and `model.progress` is how far the allocation has moved from that split toward the best variant. These are the only lift figures such an optimization has, so they lead — labeled as model estimates, with the reference named. The stale-baseline trap below does not apply: there is no baseline arm to go stale.

## Traffic share IS P(best)

Thompson sampling is probability matching: a variant's `share` in `model.variants` is both the probability it is the best servable variant and the share of optimized traffic it receives. The weight served overall is

```
weight = share × (1 − holdout share)
```

So "P(best)", "traffic share" and "weight" are the **same number in different scalings**. Never present them as independent pieces of evidence — "the model is 80% confident *and* backs it with 80% of traffic" is one fact stated twice. Quote one and explain the identity.

A corollary: a variant can lead on raw rate yet hold little traffic while the model is unsure — trust `share`, not the rate ranking. And when `share` concentrates past ~90%, exploration is effectively over: the bandit has internally shipped that variant.

## The three lift numbers

The pack reports three figures that answer different questions:

| Number | Source field | What it is |
|---|---|---|
| **Measured** | `results.primary_metric_vs_holdout` | Empirical: Levered's traffic vs. the randomized holdout, per user, frequentist CI + p-value. The only number from a randomized comparison. |
| **Policy (now)** | `model.policy_lift` | Modeled: current allocation mix vs. the baseline arm's posterior. |
| **Best (ceiling)** | `model.ceiling_lift` | Modeled: serving the best variant everywhere (per segment) vs. the baseline arm's posterior, shrunk halfway toward the policy lift because a best-of-draws figure runs optimistic. Headroom, not a result. |

Lead with measured. Label everything. When measured and modeled disagree, do not assume measured will "catch up" — diagnose the gap (see below).

## The stale-baseline trap

The modeled numbers divide by the **model's posterior for the baseline arm**, and that posterior pools the baseline's *entire history* — early bandit traffic plus the continuous holdout. A late-converging winner's posterior, by contrast, is dominated by *recent* traffic. If the underlying base rate drifted between those periods, the modeled lift absorbs the drift: recent numerator ÷ historical denominator.

Symptoms and the check:

- **Symptom:** modeled policy/ceiling climbing week over week with no matching move in the measured series. The pack's `model_history` (the trend at the end of the script's MODELED block; `levered optimizations lift-history <id>` for longer) makes this visible — a ceiling that ran +2.3% → +5.3% in nine days while measured sat still is the trap in action, not the product getting better.
- **Check:** compare the baseline variant's `reward.mid` against the recent holdout conversion rate (the script's baseline-sanity gate). A gap worth a meaningful fraction of the claimed lift means the modeled figure is inflated by roughly that fraction.
- **Response:** keep the modeled number out of the headline and use the gap *diagnostically* — it tells you how much of the measured-vs-modeled disagreement is denominator staleness rather than convergence (in one real case, ~2/3 of it). Do **not** publish a re-denominated hybrid (model numerator ÷ observed holdout rate): subsampling the denominator but not the numerator is inconsistent, and the hybrid inherits the numerator's drift — observed to move over a percentage point in two days. Drift is a modeling problem, and only a model that accounts for time (day-type covariates, serial nuisance terms, whatever the platform runs) can produce quotable modeled lift under it — which is exactly what the baseline-sanity check verifies. Run the check each time rather than assuming either way: a passing check is what earns the modeled figures their place in the report.

This is the same failure family as pooling across a holdout-% change (SKILL.md validation step a): a numerator weighted to one calendar period, a denominator weighted to another, and drift booked as lift.

## Counts are users

Every count in `results` (per variant, per segment, and per day in `time_series`) is users, each counted once at their first exposure, with holdout users left out. It is the rollup the model trains on. The holdout comparison is per user too, from its own measurement. Exposure *events* appear only in the warehouse health checks (`diagnostics`), never next to a rate.

## Matured users only

Each variant also carries `matured_users` / `matured_converting_users`: the users whose conversion window has closed. The model trains on those alone, and the dashboard's Observed rate and vs-baseline lift are computed from them. Quote the matured pair when reading a variant's observed rate; `users - matured_users` are still inside the window and can't have converted yet. Counting them makes the variant that most recently received traffic look worst — which is usually the one the model is routing traffic *to* — and that reading contradicts Probability of best (Taxfix, 2026-10-19: variant 2 led on probability of best and read -7.7% vs baseline because half its users were still in the 24h window).

## Factor effects and importance

Design factors and context factors answer "what is this worth?" with two different figures, and they are not on one scale.

**Design factors: factor effect and level effects** (`model.factor_effects`, one entry per design factor, ranked by factor effect; each has `effect` and `relative` for the factor and a `levels` list with the same per level). Both are anchored on the current policy:

- A level's reward mixes the other design factors the way the Thompson policy mixes them within that level in each segment (its weight on each servable variant with that level, renormalized; where the policy never picks the level, its mix of the other factors overall), averaged over segments by traffic.
- The reference is the reward of the baseline variant's level, or, without a baseline, the level rewards mixed by each level's share of the servable variants.
- **Level effect:** level reward vs. the reference. The baseline's level is exactly 0.
- **Factor effect:** what optimizing the factor is worth when every segment takes its own best level, per draw, vs. the reference. Per draw it is at least every level effect, and it is never negative. Within one segment it is exactly the best level effect.

`relative` is the lift ("worth +x%"), `effect` the absolute reward difference (pp for a rate). The factor effect picks a best level over uncertain rewards, so it is biased upward: a factor with no effect still reads slightly positive. Check a factor effect whose interval starts near zero against the level effects and the exposure counts before calling the factor important; low means little to gain from optimizing it, so the factor is a candidate to drop in the next optimization. The level effects are the dashboard's per-level figures: quote them for the level-effects table, and do not re-derive them from `model.variants` (an equal-weight mean over the other factors is a different, unmixed figure).

**Factor uplift and factor importance** (`model.factor_importance`, from the store's `factor_importance` macro; only with two or more design factors): the policy lift split by design factor. Each entry in `factors` has an `uplift` (an interval), a `share` and a `share_interval`; `interaction` has the same for the interaction term.

- **Factor uplift:** the live policy over the factor's reference policy, which keeps the reference's mix over that factor's levels and mixes the other factors within each level as the policy does, i.e. what the policy's current choices on that factor earn. It equals the factor's level effects weighted by the policy's share of traffic on each level. It is signed, like the policy lift: below 0 when the policy currently does worse on that factor than on its reference level.
- **Interaction term:** 1 + the policy lift divided by the product of 1 + each factor uplift, minus 1. It is near 0 when the reward and the policy's traffic both factorize across the design factors. A negative one means levels pay together (moving either factor back loses the combination's gain, so each is credited with it); a positive one means factors stand in for each other.
- **Share:** a term's expected ln(1 + uplift) over the expected ln(1 + policy lift). The factors and the interaction term sum to 1 (except against the current version, below), so "the CTA accounts for 60% of the current lift" is right. This holds whatever the lift's sign: with a negative policy lift the shares allocate the loss, so a factor that lost has a positive share and one that gained a negative share. `share_interval` is the interval of the per-draw share ln(1 + uplift) / ln(1 + policy lift); quote it with the share ("60% [35%, 85%]"). It is wide while the policy lift is near 0, where the per-draw share is unstable. When the control is the current version, which has no level on any design factor, the uplifts and the interaction term split the lift over an even split of the variants, while the shares are still of the policy lift over the current version: what they leave of 100% is what that even split earns over the current version, which no factor accounts for. If the even split earns less than the current version, the factor shares sum to more than 100%: say that the factors made up that gap as well as the lift. The shares are null when the model has no estimate of the current version.

This is the one design figure that partitions anything. It reads what each factor contributes to the policy lift now; the factor effect reads what a factor could be worth. A factor can have a large factor effect and a small share while the policy is still exploring it.

**Context importance** (`model.context_importance`) splits the personalization uplift (`model.personalization`) by context factor, the way factor importance splits the policy lift by design factor:

- **Context-factor uplift** (`uplift`, also `model.importance.context`): the live policy over the same policy with that one factor averaged out (its segments pooled by weight before the policy is taken), still conditioning on the others. Signed.
- **Interaction term:** what the product of 1 + each uplift leaves of 1 + the personalization uplift. Negative when personalizing pays on factors together (removing any one loses what they earn jointly, so each is credited with it); positive when factors stand in for each other (each uplift small while the personalization uplift is large).
- **Share:** a term's expected ln(1 + uplift) over the expected ln(1 + personalization uplift); the factors and the interaction term sum to 1, so "device accounts for 60% of what personalizing adds" is right. `share_interval` is the interval of the per-draw share; quote it with the share.

Design shares are of the policy lift, context shares of the personalization gain: never put a design factor and a context factor side by side as a ranking. Factor importance and context importance are the only figures that partition anything: never sum, stack or apportion the others.

## Per-context figures

The store models every context (segment) separately, so the pack carries the model's own per-context view:

- `model.segments` — per context (one row per combination of every context factor, `weight` = its share of traffic): the policy lift vs. the reference, P(beats it), the policy's reward against the ceiling's (`ceiling_reward`: the best variant there), and the variant the model serves (`leader`, a variant key; the script labels it) with its share.
- `model.personalization` — what the contextual policy earns over the same policy blind to context, with P(> 0). This is what considering context has added so far; context importance splits it by factor.

These lead the "what context added" claim. A different `leader` by segment with a personalization interval above zero is a personalization benefit; the same leader everywhere with personalization near zero is "no personalization benefit detected so far". Per-level measured lift (cube vs. holdout) stays the basis for "how results varied".

## Asking the store directly

The pack is fixed queries over the store. Anything else is a `levered posterior query <id> --sql … --json`; build it the way the pack's figures are built, so what you quote matches the dashboard. The store describes itself: `duckdb_views()` and `duckdb_functions()` (`WHERE NOT internal`) list its views and macros, each with what it means as `comment`. For the headline's trend, `levered optimizations lift-history <id> [--days N]`.

Before the first posterior is published the route answers 404 ("No posterior has been published for this optimization yet"): traffic is an even split over the servable variants and there is no model estimate.

## The FM models interactions

A factor can matter only *in combination* — the factorization machine fits pairwise structure the per-level table hides. Reading those interactions correctly has its own traps: see [cross-effects.md](cross-effects.md).
