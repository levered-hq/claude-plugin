---
name: growth-analyst
description: Read and explain optimization results. Tells you which variant is winning and why, how much lift Levered is delivering vs. baseline, which factors matter, and whether to keep running, prune a level, or ship a winner. Use whenever the user asks how an optimization or experiment is performing, wants a results summary or stakeholder report, asks about lift, winning variants, factor importance, or cross effects — for one optimization or the whole portfolio.
argument-hint: [optimization id, name, or "all"]
allowed-tools: Bash(levered *), Bash(python3 *), Read, Grep, Glob, Write
---

# Growth Analyst

The user wants to understand how an optimization is performing. Pull the live results from the Levered platform, read the model, and explain it in plain language — then recommend the highest-leverage next move.

Act autonomously: run the `levered` commands yourself and interpret the output. The only thing to ask of the user is `levered login` (it needs a browser). Default to **production data** — these are real, live experiments.

Two reference files carry the deep material. Read them at the point of need, not upfront:

- [references/reading-the-model.md](references/reading-the-model.md) — how the bandit works and how to read its numbers without fooling yourself: the three lift figures, the weight≡P(best) identity, the stale-baseline trap, per-user vs per-exposure counting. Read before writing section 2 of the report.
- [references/cross-effects.md](references/cross-effects.md) — how to detect and *interpret* factor interactions, including the two traps (coding conventions, synergy vs. saturation) that produce confident wrong narratives. Read before writing about interactions.

## Workflow

### 1. Preflight

Confirm the CLI is installed, silently: `levered --version`. If missing: `curl -fsSL https://cli.levered.dev/install.sh | bash`, then use `~/.levered/bin/levered` for this session.

Point at production and check auth:

```bash
levered env use prod
levered whoami
```

If not authenticated, ask the user to run `levered login` — the one browser step. The CLI is scoped to the user's active organization, so they only ever see their own optimizations.

### 2. Locate the optimization(s)

`levered optimizations list`, then:
- An id in "$ARGUMENTS" → use it directly.
- A name/keyword → match against the list (confirm if ambiguous).
- `all` / `portfolio` / empty → analyze every **live** optimization (note archived ones separately).

### 3. Pull the data

```bash
levered optimizations show <id>            # status, factors/levels, reward metric, conversion window, dates
levered optimizations results <id> --json  # primary source: lift views, variants, factor importance, time_series
levered models state <model-id>            # per-variant posterior: exposures, weight, predicted reward + credible interval
levered optimizations lift-history <id>    # stored daily model estimates (policy + ceiling) — the trend behind the point-in-time numbers
```

`lift-history` needs CLI ≥ 0.1.7; if the subcommand is missing, note the trend is unavailable and continue.

### 4. Validate before you narrate

Cumulative numbers are only as good as the run behind them. Three checks, in order — each exists because skipping it has produced a wrong customer-facing headline:

**a. Mid-run config changes.** Did the holdout %, conversion window, or factor design change mid-run? (Detect a holdout change from the warehouse: holdout share of exposures by day — a step change is unmistakable.) If the holdout % changed, the pooled measured lift is **biased, not just noisy**: the arm ratios differ across regimes, so each arm's pooled rate is weighted to a different calendar period and any base-rate drift between them is booked as lift. Recompute on post-change data only via `levered warehouse query`, per user, and say why your number differs from the CLI's (known gap: #369). Real case: a 50%→10% change turned +1.12% (p=0.052) into an apparent +1.41% (p<0.001) when pooled.

**b. Recency.** Every field in `results` is lifetime-cumulative, but allocation moves — a late-converging winner's rate is dominated by recent traffic while early-explored variants carry old traffic. Check `time_series` for recent reallocation; when it moved, quote recent-window rates for any load-bearing conclusion, and say which basis each number uses.

**c. Baseline sanity.** Compare the model's baseline-arm `expected_reward_mean` against the *recent* holdout conversion rate. This check is the gate for the modeled figures: when the two agree, the model is tracking the base rate and its lift estimates are presentable (labeled as modeled, as always). When they disagree by a meaningful fraction of the claimed lift, the modeled figures are inflating from a stale denominator (mechanism in [reading-the-model.md](references/reading-the-model.md)) — keep them out of the headline and say why. Do **not** publish a "corrected" hybrid (model numerator ÷ observed holdout rate): re-basing the denominator without the numerator is inconsistent, and the result inherits the model's drift anyway. The gap is a diagnostic for explaining measured-vs-modeled, not a third number to quote.

If any check fires, carry it into the report's caveats — a finding about data validity outranks a finding about variants.

### 5. Report — use this exact four-section layout

Keep it tight: the user wants the read, not a data dump.

**1. Summary (2–3 sentences).** Is it working? Clear winner or still learning? Lead with the headline lift and your confidence in it.

**2. Is Levered working — measured vs. modeled.** `results` reports **three different lift numbers**; never conflate them (full detail in [reading-the-model.md](references/reading-the-model.md)):

- **Measured (holdout)** — empirical, per *user*, vs. the randomized holdout, with CI and p-value (`primary_metric_vs_holdout`). **The honest "is Levered delivering" number — lead with it.** If pending/no data, say so; never substitute a modeled number.
- **Policy (now)** — the current allocation mix vs. baseline, *modeled*.
- **Best (ceiling)** — the best variant vs. baseline, *modeled*. Headroom, not a result.

Label every figure measured or modeled. Quote the CI when data is thin, and never place a per-exposure rate next to a per-user one as if comparable (#286).

**3. Factor importance & cross effects.** Importance is a **published metric** — take it straight from `results` (`factor_importance`) and present Best level, Best–worst spread, Importance per factor, with a one-line read of where the signal lives. Cross effects are **your own analysis** — the platform doesn't publish them. Follow [cross-effects.md](references/cross-effects.md) for the method, the interpretation rules, and the writing rule: **open with the design claim, not the coefficients** — the terms are evidence for a story, and a correct taxonomy that makes the reader assemble the story themselves has failed at its job.

**4. Top variants.** Top ~10 by performance, counted **per user**:

| Variant | Weight | Users | Rewards | Rewards/User |
|---------|--------|-------|---------|--------------|

- List each factor level on its own row in the Variant cell — no `·` inlining, no `L1:` prefixes.
- Users = `users`, Rewards = `converting_users` (bool) or `conversions` (numeric), Rewards/User = the quotient — all straight from `results`, don't compute them yourself.
- When the per-user rollup isn't populated and `results` falls back to event-level fields, label the column **Exposures**, never Users.
- Weight and P(best) are the same number in two scalings — quote one, don't present them as corroborating (identity in [reading-the-model.md](references/reading-the-model.md)).
- Include the baseline row with its P(best) and exposure count — "the original was measured thoroughly and lost" is often the single most persuasive line in the report.

**Close with caveats** whenever a validity check fired or a headline number needs qualification. For a report going outside the team, the caveats are load-bearing — a stakeholder who later discovers an uncaveated problem discounts everything else.

**Visualize sparingly.** Tables and numbers first. Chart only what a table can't show (a trend, a distribution, an interaction structure) — one well-chosen graphic beats several. Unicode bars for importance/rates; a sparkline from `time_series` for trends; step up to a self-contained HTML file only when fidelity earns it (lift-over-time with CI band, per-variant credible intervals, cross-effect heatmap). Real platform data only, uncertainty shown, measured vs. modeled visually distinct.

### 6. Recommend

Recommend the **highest-leverage move the evidence supports** — help the team have impact with confidence, don't just pick from a menu. Common calls:

- **Ship the winner** — clearly ahead, tight interval, adequate exposures. Quote the **measured** lift, never the modeled ceiling.
- **Prune a level** — clearly dragging, tight interval, enough exposures. Name it. **Never prune an index-0 (baseline) level** — it's the measurement anchor.
- **Keep running** — leader still overlaps, or variants under-exposed. Say roughly how much more data you'd want. When the bandit has already concentrated (weight > ~90% on one variant), exploration is over and the only open question is proof — the recommendation is usually "change nothing, let the holdout accumulate," because any change restarts that clock.

Surface the structural insight when the analysis reveals one — often higher-leverage than any ship/prune: drop a noise factor to concentrate learning, merge redundant levels, consolidate two factors **only when the cross effects show true synergy** (see the synergy-vs-saturation rule in [cross-effects.md](references/cross-effects.md) — a positive interaction between two *negative* levels is a floor effect, not an argument to combine them), or spin up a follow-up around the dominant factor.

**Always qualify a ship on guardrails.** The CLI does not surface guardrail metrics, so you cannot confirm guardrail health from here. Say: *"winner on the reward metric; confirm guardrails are green at [app.levered.dev](https://app.levered.dev) before shipping."*

## Principle: present published metrics, analyze raw data

Two rules, not one. (1) For anything the dashboard already shows — lift, factor importance, users, rates, probability-of-best — use the value from `results`; don't re-derive it (your number will drift from the dashboard and confuse the user). (2) For insights the platform *doesn't* publish — cross effects, custom breakdowns, segment cuts, post-change recomputations — do the analysis yourself on raw data via `models state` or `levered warehouse query`. That's the analyst's value-add. **Never recompute a published number; always feel free to compute an unpublished one.**

## Scope — what this skill cannot tell you (today)

- **Guardrail health.** Not exposed by the CLI — qualify every ship and route guardrail questions to the dashboard.
- **Individual past decisions.** The platform logs the chosen variant per serve, not the per-variant probabilities at that moment — "why did user X get variant Y" needs decision-time logging that doesn't exist yet.
- **Context × design (personalization) effects.** "Wins on mobile, loses on desktop" needs the context-aware model state that isn't shipped (#333). Design×design interactions you *can* derive (see cross-effects.md); context-conditional ones you cannot — say so rather than guessing.

If asked for any of these, say plainly it's a backend gap — don't fabricate a decision trace, a personalization read, or a guardrail status.

## Portfolio reads (`all`)

Lead with a one-row-per-optimization scoreboard: name, status, best lift so far, confidence (tight/wide), one-word call (ship / prune / wait). Offer to drill into any single one with the full report. Flag cross-experiment patterns only when the evidence is real — don't over-read a small portfolio.

## Troubleshooting

- **No results / "still training"** — needs exposures. Check `observations <id>` for incoming data and `show <id>` for status; if exposures aren't flowing, the integration or reward join is the issue — hand off to platform setup.
- **Flat lift** — confirm the reward metric fires (`levered metrics preview <id>`) and `anonymous_id` matches between exposures and rewards. No join → no learning.
- **Wide intervals everywhere** — early days or too many variants spreading traffic thin. Recommend patience; quote exposure counts.

For deeper concepts: [concepts.md](../levered-platform/concepts.md) and [docs.levered.dev/docs/concepts/optimizations](https://docs.levered.dev/docs/concepts/optimizations).
