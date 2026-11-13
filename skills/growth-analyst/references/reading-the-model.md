# Reading the model

Levered's bandit is a **Bayesian factorization machine** driven by **Thompson sampling**. Its numbers are easy to read wrongly in ways that sound authoritative. This file is the antidote — read it before writing the measured-vs-modeled section of a report.

## Posterior, not point estimate

Every model figure comes from the posterior store: thousands of joint draws from the posterior, queried at runtime. <!-- LEGACY(model-source) --> (An optimization created before the store, `model.source == "bandit"`, carries the model's own summaries instead, in the same shape; see [Optimizations from before the store](#optimizations-from-before-the-store).) The pack reduces each to `{lo, mid, hi}`, a credible interval and its median; each variant's `reward` in `model.variants` is one. Always carry the uncertainty into the read: a 12% lift with an interval of [−3%, +27%] is not a winner, it's a "keep running." Thin exposures → wide intervals.

## Baseline = all-first-level

The reference variant is the index-0 level of every factor. Lift for any variant is `(p_variant − p_baseline) / p_baseline`. This is why the baseline level is never pruned — it's the measurement anchor. Levered also forces traffic to the baseline (the holdout is served the baseline), so it stays well-measured even when the bandit's own weight on it reaches zero.

The API, not the key convention, says which variant that is: each variant in `results` carries `is_baseline`, and `results.stats.reference` says what every lift figure is measured against — `"baseline"` or, for an optimization created without one (`has_baseline: false`), `"equal_split"`.

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

## Per-user vs per-exposure (#286)

The holdout comparison is per *user*. The per-variant `rate` in `results` is per *exposure* when the per-user rollup isn't populated (the fields are then named `exposures`/`conversions`, not `users`/`converting_users`). A user can be exposed many times, so the two bases are not comparable — never quote them side by side as if they were, and label exposure-based columns **Exposures**.

## Matured users only

Each variant also carries `matured_users` / `matured_converting_users`: the users whose conversion window has closed. The model trains on those alone, and the dashboard's Observed rate and vs-baseline lift are computed from them. Quote the matured pair when reading a variant's observed rate; `users - matured_users` are still inside the window and can't have converted yet. Counting them makes the variant that most recently received traffic look worst — which is usually the one the model is routing traffic *to* — and that reading contradicts Probability of best (Taxfix, 2026-10-19: variant 2 led on probability of best and read -7.7% vs baseline because half its users were still in the 24h window). The fields are null when the rollup predates them; fall back to `users` / `converting_users` then and say the rate includes pending users.

## Factor effects and importance

Design factors and context factors answer "what is this worth?" with two different figures, and they are not on one scale.

**Design factors: factor effect and level effects** (`model.factor_effects`, one entry per design factor, ranked by factor effect; each has `effect` and `relative` for the factor and a `levels` list with the same per level). Both are anchored on the current policy:

- A level's reward mixes the other design factors the way the Thompson policy serves them in each segment (renormalized over the servable variants with that level; an even split where the policy puts no weight), averaged over segments by traffic.
- The reference is the reward of the baseline variant's level, or, without a baseline, the average of the factor's levels.
- **Level effect:** level reward vs. the reference. The baseline's level is exactly 0.
- **Factor effect:** what optimizing the factor is worth when every segment takes its own best level, per draw, vs. the reference. Per draw it is at least every level effect, and it is never negative. Within one segment it is exactly the best level effect.

`relative` is the lift ("worth +x%"), `effect` the absolute reward difference (pp for a rate). The factor effect picks a best level over uncertain rewards, so it is biased upward: a factor with no effect still reads slightly positive. Check a factor effect whose interval starts near zero against the level effects and the exposure counts before calling the factor important; low means little to gain from optimizing it, so the factor is a candidate to drop in the next optimization. The level effects are the dashboard's per-level figures: quote them for the level-effects table, and do not re-derive them from `model.variants` (an equal-weight mean over the other factors is a different, unmixed figure).

**The interaction** (`model.importance.interaction`, `lift` of `interaction_draws`): the best design over the design made of each factor's best level, each picked on its own in every segment and draw on its level reward (the other factors mixed the way the current policy serves them, as in `factor_draws`). Only reported with two or more design factors. Near zero means the factors don't interact; when it is as large as the top factor effect, the winner is a specific combination, so don't read factors one at a time.

**Context factors: importance** (`model.importance.context`), an oracle lift `reward_oracle / reward − 1`: the best the model could do with everything, over the best it could do denied conditioning on that context factor. It is not on the design factor effects' scale: never put "hero is worth +4%" and "platform is worth +1%" side by side as a ranking. None of these figures are shares and none partition anything: never sum them, stack them to 100%, or describe one as a fraction of the total. Two context factors that stand in for each other can both read low while conditioning on either is worth a lot. Both sides of the oracle ratio are best-of-draws figures, so check a narrow interval near zero against the exposure counts before calling a context factor worthless.

## Per-context figures

The store models every context (segment) separately, so the pack carries the model's own per-context view:

- `model.segments` — per context (one row per combination of every context factor, `weight` = its share of traffic): the policy lift vs. the reference, P(beats it), the policy's reward against the ceiling's (`ceiling_reward`: the best variant there), and the variant the model serves (`leader`, a variant key; the script labels it) with its share.
- `model.personalization` — what the contextual policy earns over the same policy blind to context, with P(> 0). This is what considering context has added so far; context importance is what each factor could add.

These lead the "what context added" claim. A different `leader` by segment with a personalization interval above zero is a personalization benefit; the same leader everywhere with personalization near zero is "no personalization benefit detected so far". Per-level measured lift (cube vs. holdout) stays the basis for "how results varied".

## Asking the store directly

The pack is fixed queries over the store. Anything else is a `levered posterior query <id> --sql … --json`; pass the SQL through a quoted heredoc as below, so the shell leaves its quotes and `$params` alone. The response is `{columns, rows, model_version, available_versions, n_samples, …}`. Views and macros: `posterior_reward(variant_id, context_id, sample_id, reward)`, `variants`, `contexts(…, weight)`, the policies `thompson_policy` / `thompson_policy_marginal` / `baseline_policy`, `thompson_traffic_share`, the per-draw macros `policy_draws[_by_context](pol, alt)`, `variant_draws[_by_context](alt)`, `oracle_draws[_by_context](context_factors, design_factors)`, `interaction_draws[_by_context]`, `factor_draws[_by_context](factor)`, and the reducers `dist(x, q)` and `p_gt(x, t)`. Use the pack's conventions: quantiles `[0.025, 0.5, 0.975]`, median as the estimate, and one oracle restriction per query (two can exceed memory on large models). Design factors are read with `factor_draws`, not an oracle restriction.

Trend of the headline: `levered optimizations lift-history <id> [--days N]` prints it one point per day (each day's newest version). The same figures for any set of versions: run this once per version in `available_versions`, passing `--version`, and tabulate.

```bash
levered posterior query <id> --version <v> --json --sql "$(cat <<'SQL'
SELECT quantile_cont(lift, [0.025, 0.5, 0.975]) AS policy_lift,
       quantile_cont((lift + headroom_lift) / 2, [0.025, 0.5, 0.975]) AS ceiling_lift,
       avg((lift > 0)::DOUBLE) AS p_beats_reference
FROM policy_draws('thompson_policy', 'baseline_policy')
SQL
)"
```

Lift of variant `$b` over variant `$a` in one context (`$context` is a `context_key`, `{}` without context factors):

```bash
levered posterior query <id> --json \
  --param q='[0.025,0.5,0.975]' --param 'a={"cta":"lv_cta_0"}' --param 'b={"cta":"lv_cta_1"}' --param 'context={}' \
  --sql "$(cat <<'SQL'
WITH a AS (SELECT context_id, variant_id, (variant_key = $a)::DOUBLE AS pi FROM contexts, variants)
SELECT unnest(dist(d.lift, $q::DOUBLE[])), unnest(p_gt(d.lift, 0))
FROM variant_draws_by_context('a') d
JOIN variants v USING (variant_id) JOIN contexts c USING (context_id)
WHERE v.variant_key = $b AND c.context_key = $context
SQL
)"
```

Design factor `$factor`'s level effects and factor effect in one segment (`$context` is a `context_key`). `factor_draws_by_context` gives per level and draw `reward`, `reward_ref` (the reference), `reward_best`, `lift` (the level effect) and `best_lift` (the factor effect, the same on every level row; in one segment exactly the best level's lift). For all traffic, which is what `model.factor_effects` carries, read `FROM factor_draws($factor)` and drop the join and the `WHERE`. For the absolute difference, reduce `reward - reward_ref`.

```bash
levered posterior query <id> --json \
  --param factor=hero --param q='[0.025,0.5,0.975]' --param 'context={"platform":"ios"}' \
  --sql "$(cat <<'SQL'
SELECT level,
       quantile_cont(lift, $q::DOUBLE[]) AS lift,
       quantile_cont(best_lift, $q::DOUBLE[]) AS best_lift
FROM factor_draws_by_context($factor) d JOIN contexts c USING (context_id)
WHERE c.context_key = $context
GROUP BY level
SQL
)"
```

`level` is the level id inside `variant_key` (e.g. `lv_hero_1`); `model.factor_effects[].levels[].value` carries its name.

Before the first posterior is published the route answers 404 ("No posterior has been published for this optimization yet"): traffic is an even split over the servable variants and there is no model estimate.

<!-- LEGACY(model-source): this whole section. -->
## Optimizations from before the store

An optimization created before the posterior store has `model_source: "bandit"`, and its pack's `model.source` is `"bandit"`: the figures are the model's own summaries, so its numbers did not change when the store arrived. Policy and ceiling lift, P(beats the reference), progress, each variant's `share` and `reward`, and the trend in `model_history` mean exactly what they mean above. What differs:

- **Factor effects:** once bandit reports them, a `"bandit"` pack carries `model.factor_effects` and lift-kind importance with the store's definitions (no absolute `effect`, lifts only): read them exactly as for a store pack.
- **Importance** (`model.importance.kind == "share"`, a fit from before that): design-factor and interaction importance are shares of the reward's variance: the share of what moves the reward that each factor's main effect carries, and the share only combinations of factors explain. They sum to 1 together, so "the CTA carries 60% of what moves the reward, combinations 10%" is right, and "the CTA is worth +60%" is wrong. A small share means the factor moves the reward little relative to the others, not that optimizing it is worth nothing in absolute terms. Context importance is a lift ("worth +x%") on both sources, and is not comparable with the shares.
- **Context:** there is no personalization figure, and each segment carries the policy's reward and the best variant's reward only. "What context added" leads with the context importance and the cross-check.
- **No posterior queries:** the pack and `lift-history` are the whole model view. Do not mix in `levered posterior query` figures: where the store answers at all, its numbers are not the ones this optimization reports.

## The FM models interactions

A factor can matter only *in combination* — the factorization machine fits pairwise structure the per-level table hides. Reading those interactions correctly has its own traps: see [cross-effects.md](cross-effects.md).
