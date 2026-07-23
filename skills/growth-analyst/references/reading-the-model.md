# Reading the model

Levered's bandit is a **Bayesian factorization machine** driven by **Thompson sampling**. Its numbers are easy to read wrongly in ways that sound authoritative. This file is the antidote — read it before writing the measured-vs-modeled section of a report.

## Posterior, not point estimate

Each variant carries `expected_reward_mean` plus `expected_reward_lo`/`expected_reward_hi` — the bounds of its credible interval. Always carry the uncertainty into the read: a 12% lift with an interval of [−3%, +27%] is not a winner, it's a "keep running." Thin exposures → wide intervals.

## Baseline = all-first-level

The reference variant is the index-0 level of every factor. Lift for any variant is `(p_variant − p_baseline) / p_baseline`. This is why the baseline level is never pruned — it's the measurement anchor. Levered also forces traffic to the baseline (the holdout is served the baseline), so it stays well-measured even when the bandit's own weight on it reaches zero.

## Weight IS P(best)

Thompson sampling is probability matching. For every variant, exactly:

```
weight = prob_best × (1 − holdout share)
```

So the `WEIGHT` and `P(BEST)` columns are the **same number in two scalings**. Never present them as two independent pieces of evidence — "the model is 80% confident *and* backs it with 80% of traffic" is one fact stated twice. Quote one and explain the identity.

A corollary: a variant can lead on raw rate yet hold little traffic while the model is unsure — trust `prob_best`, not the rate ranking. And when `prob_best` concentrates past ~90%, exploration is effectively over: the bandit has internally shipped that variant.

## The three lift numbers

`results` reports three figures that answer different questions:

| Number | Source field | What it is |
|---|---|---|
| **Measured** | `primary_metric_vs_holdout` | Empirical: Levered's traffic vs. the randomized holdout, per user, frequentist CI + p-value. The only number from a randomized comparison. |
| **Policy (now)** | `estimated_improvement_percent` | Modeled: current allocation mix vs. the baseline arm's posterior. |
| **Best (ceiling)** | `best_vs_baseline_percent` | Modeled: best single variant vs. the baseline arm's posterior. Headroom, not a result. |

Lead with measured. Label everything. When measured and modeled disagree, do not assume measured will "catch up" — diagnose the gap (see below).

## The stale-baseline trap

The modeled numbers divide by the **model's posterior for the baseline arm**, and that posterior pools the baseline's *entire history* — early bandit traffic plus the continuous holdout. A late-converging winner's posterior, by contrast, is dominated by *recent* traffic. If the underlying base rate drifted between those periods, the modeled lift absorbs the drift: recent numerator ÷ historical denominator.

Symptoms and the check:

- **Symptom:** modeled policy/ceiling climbing week over week with no matching move in the measured series. `lift-history` makes this visible — a ceiling that ran +2.3% → +5.3% in nine days while measured sat still is the trap in action, not the product getting better.
- **Check:** compare the baseline arm's `expected_reward_mean` against the recent holdout conversion rate. A gap worth a meaningful fraction of the claimed lift means the modeled figure is inflated by roughly that fraction.
- **Response:** present the holdout-denominated figure alongside (modeled policy rate ÷ recent holdout rate), and keep the modeled number out of the headline. In one real case the reported +3.7% policy lift was +2.1% against the recent holdout rate — most of the modeled/measured gap was denominator, not convergence.

This is the same failure family as pooling across a holdout-% change (SKILL.md validation step a): a numerator weighted to one calendar period, a denominator weighted to another, and drift booked as lift.

## Per-user vs per-exposure (#286)

The holdout comparison is per *user*. The per-variant `rate` in `results` is per *exposure* when the per-user rollup isn't populated (the fields are then named `exposures`/`conversions`, not `users`/`converting_users`). A user can be exposed many times, so the two bases are not comparable — never quote them side by side as if they were, and label exposure-based columns **Exposures**.

## The FM models interactions

A factor can matter only *in combination* — the factorization machine fits pairwise structure the per-level table hides. Reading those interactions correctly has its own traps: see [cross-effects.md](cross-effects.md).
