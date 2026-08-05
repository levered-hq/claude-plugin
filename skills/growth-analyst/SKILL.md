---
name: growth-analyst
description: Read and explain optimization results as a customer-ready document — which variant is winning and why, how much lift Levered is delivering vs. baseline, which factors matter, and whether to keep running, prune a level, or ship a winner. The deliverable is always fit to forward to the customer; analyst detail goes in a chat addendum. Use whenever the user asks how an optimization or experiment is performing, wants a results summary or stakeholder report, asks about lift, winning variants, factor importance, or cross effects — for one optimization or the whole portfolio.
argument-hint: [optimization id, name, or "all"]
allowed-tools: Bash(levered *), Bash(curl -fsSL https://cli.levered.dev/install.sh*), Bash(python3 *), Read, Grep, Glob, Write
---

# Growth Analyst

The user wants to understand how an optimization is performing. Pull the live results from the Levered platform, read the model, and explain it in plain language — then recommend the highest-leverage next move.

Act autonomously: run the `levered` commands yourself and interpret the output. The only thing to ask of the user is `levered login` (it needs a browser). Default to **production data** — these are real, live experiments.

Two reference files carry the deep material. Read them at the point of need, not upfront:

- [references/reading-the-model.md](references/reading-the-model.md) — how the bandit works and how to read its numbers without fooling yourself: the three lift figures, the weight≡P(best) identity, the stale-baseline trap, per-user vs per-exposure counting. Read before writing the Impact section.
- [references/cross-effects.md](references/cross-effects.md) — how to detect and *interpret* factor interactions, including the two traps (coding conventions, synergy vs. saturation) that produce confident wrong narratives. Read before writing about interactions.
- [references/report-template.md](references/report-template.md) — a user-approved example report with annotations. Read before writing the document for its register and density; it is an example of the pyramid principle done right, not a required structure.

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
levered optimizations progress <id>        # runtime, per-arm enrollment (per user), convergence — the Progress section's facts
levered optimizations guardrails <id>      # guardrail metrics, bandit vs. holdout: lift, 95% CI, p-value, ok/pending/violated
levered optimizations lift-history <id>    # stored daily model estimates (policy + ceiling) — the trend behind the point-in-time numbers
```

`progress`, `guardrails`, and `lift-history` need CLI ≥ 0.1.7. The CLI self-updates: a run stages the update and prints "Restart levered to apply", and the next invocation runs the new version — so if a subcommand is missing, invoke the CLI twice and retry before concluding it's unavailable.

### 4. Validate before you narrate

Cumulative numbers are only as good as the run behind them. Three checks, in order — each exists because skipping it has produced a wrong customer-facing headline:

**a. Mid-run config changes.** Did the holdout %, conversion window, or factor design change mid-run? (Detect a holdout change from the warehouse: holdout share of exposures by day — a step change is unmistakable.) If the holdout % changed, the pooled measured lift is **biased, not just noisy**: the arm ratios differ across regimes, so each arm's pooled rate is weighted to a different calendar period and any base-rate drift between them is booked as lift. Recompute on post-change data only via `levered warehouse query`, per user, and say why your number differs from the CLI's (known gap: #369). Real case: a 50%→10% change turned +1.12% (p=0.052) into an apparent +1.41% (p<0.001) when pooled.

**b. Recency.** Every field in `results` is lifetime-cumulative, but allocation moves — a late-converging winner's rate is dominated by recent traffic while early-explored variants carry old traffic. Check `time_series` for recent reallocation; when it moved, quote recent-window rates for any load-bearing conclusion, and say which basis each number uses.

**c. Baseline sanity.** Compare the model's baseline-arm `expected_reward_mean` against the *recent* holdout conversion rate. This check selects how the modeled figures are presented (step 5, Impact): when the two agree, the model is tracking the base rate and its lift estimates present normally (labeled as modeled, as always). When they disagree by a meaningful fraction of the claimed lift, the modeled figures are inflating from a stale denominator (mechanism in [reading-the-model.md](references/reading-the-model.md)) — they still appear in Impact but carry the inflation caveat, stay out of the Summary, and never headline. Do **not** publish a "corrected" hybrid (model numerator ÷ observed holdout rate): re-basing the denominator without the numerator is inconsistent, and the result inherits the model's drift anyway. The gap is a diagnostic for explaining measured-vs-modeled, not a third number to quote.

**d. Story verification.** Numbers have gates; stories need them more, because a compelling mechanism narrative survives re-reading on plausibility alone. Before any causal or design claim enters a report: (1) write down what the claim predicts for every cell it governs, and check each prediction against the complete masked deviation matrix, not just the cells that inspired the claim; (2) require the finding to survive two independent constructions (for example raw aggregated deviations and a second parameterization, or raw data and model estimates — agreement is the license, disagreement is a finding); (3) treat uniformly-signed coefficient tables as alarms (cross-effects.md Trap 3); (4) when any part of a fit is untrustworthy, distrust every coefficient from that fit, including the ones that support your story. A claim that fails a check is downgraded to a named observation or cut. Claims inherited from earlier reports are re-verified against current data before reuse: repetition is not evidence.

If any check fires, it shapes the document (exclusions, softened claims) and is reported to the user in the analyst's addendum (step 5) — a finding about data validity outranks a finding about variants.

### 5. Report — a customer-ready document, always

The deliverable is a document the user can forward to their customer or stakeholders **unchanged**. Everything above is the kitchen; the document is the plate — its rigor shows up as what's *absent*, not as visible apparatus. There is no separate internal report mode: analytical depth the user needs goes in the **analyst's addendum** (end of this section), never in the document.

**Structure: Summary → Progress → Impact → Variants and factors → Recommended action → method notes.** [references/report-template.md](references/report-template.md) is a user-approved worked example of the register and density — borrow its conventions (bold-labeled Summary bullets, bold claim openers, compact `·`-joined tables, verdict column, numbered actions, italic fine-print method notes) as sensible defaults, but treat it as an example, not a required structure: adapt the rendering to what the data and story need. The deliverable is ONE markdown file, sent to the user as a file — no SVG or image files (user ruling 2026-08-03); the analyst's addendum stays in chat. **The governing rule — the one thing that is not negotiable — is Minto's Pyramid Principle**:

- **Apex — the governing thought.** The Summary's first line is one bold sentence giving the answer: what happened, what it's worth, what to do. Everything below exists to support it.
- **Answer first at every level.** The Summary bullets summarize the sections; each section opens with a **bold claim sentence** giving its "so what" (plus at most one supporting sentence), then goes straight to the data. Never build up to a conclusion, and never pad the opener into a paragraph.
- **Each level raises the question the level below answers.** The governing thought provokes "how do you know?" — the bullets answer it; a section opener provokes exactly the question its tables settle. If a table doesn't answer a question the opener raised, it belongs elsewhere or nowhere.
- **Groupings are MECE and parallel.** The four sections decompose the story without overlap: how far along (Progress), how much value (Impact), why (Variants and factors), what next (Recommended action). File every fact under the single question it answers.

The test: a reader who takes only the governing thought gets the answer; only the bullets, the justified answer; only the section openers, a coherent executive read — and the tables let any of them verify it. Facts over narration — the story is the ordering and the claims, not paragraphs.

- **Summary** — one bold governing sentence, then four bullets whose bold labels match the section names (`**Progress:** …`, `**Impact:** …`, `**Variants and factors:** …`, `**Recommended action:** …`); a reader who stops here has the whole story:
  - **Progress:** how far the model has converged, how big the sample is, whether results are stable.
  - **Impact:** measured lift vs. baseline **with its absolute translation** (additional conversions per month); modeled impact (now + best potential) **only if the baseline-sanity gate (4c) passes**.
  - **Variants and factors:** the winning variant and the design factors that carry the outcome (named to match the section).
  - **Recommended action:** one or two short sentences — the move now, then the follow-up.
- **Progress** — a small table of facts: how long the experiment has been running; users enrolled (per user — state full-run and measurement-window counts separately, and never attach the current holdout % to a full-run count that spans an earlier config); conversions tracked; how far the model has converged (progress-to-best, winner's traffic share) and whether allocation has been stable recently (`time_series`). Denominator trap: the CLI's `weight` is the variant's share of ALL traffic including the holdout (weight 0.90 at a 10% holdout = essentially 100% of optimized traffic); customer documents state traffic as share of optimized traffic, and a weight change must never be read against a share-of-optimized figure from an earlier report.
- **Impact** — two parts, measured first and authoritative:
  1. **Measured** — the lift table: **reward metric and each guardrail metric** × holdout / Levered / lift / 95% CI, per user, valid-regime window. Guardrail rows come from `levered optimizations guardrails` (empirical bandit vs. holdout with CI, p-value, and status) — quote them as published; recompute from the warehouse only for cuts the CLI doesn't give (e.g. a post-config-change window), and label the basis. A `pending` guardrail is reported as pending — never invent a row. Guardrail windows can differ from the reward window (the command prints them); when they do, say so in method notes. Measured is the causal number and always leads (`results` reports three lift figures; the other two are modeled — [reading-the-model.md](references/reading-the-model.md)). Follow the table with **the absolute translation** — additional conversions per month at current traffic, central estimate with an honest range from the CIs; it's the sentence stakeholders retell. Wording discipline is symmetric: a guardrail whose CI cannot rule out material harm gets "no detectable change", never "no degradation" — and a guardrail with a positive effect at p < 0.05 is reported as positive ("at the threshold of significance" while borderline or newly crossed), never flattened to "no detectable change". Judge significance by the p-value, not by a rounded CI edge reading "+0.0%". When guardrails differ, the Summary bullet names them separately, never one lumped verdict. When metrics use different windows, say why in method notes. Measurement pending → say so plainly; never substitute a modeled number. Never place a per-exposure rate next to a per-user one as if comparable (#286).
  2. **Modeled** — current policy and best-variant (ceiling), clearly labeled model estimates, **always shown here**: these are the dashboard Model tab's “Lift (now)” / “Lift (best variant)” cards, so the customer can see them anyway — reference them by those names (the measured lift is on the dashboard too, on the Lift Measurement tab; don't imply only the modeled figures are visible there), and remember an unexplained gap between dashboard and report is worse than an explained one. The baseline-sanity gate (4c) selects the *presentation*, not inclusion: gate passes → present normally; gate fails → present **with a caveat** stating the mechanism and direction in one customer-safe sentence (the model's baseline reference lags a shifting base rate, so these figures are temporarily inflated; the measured figures are authoritative; a correction is in progress and these estimates are expected to come down). The caveat pre-registers the correction — when the fix deploys and the numbers drop, that's a kept promise, not a surprise. The caveat must **never contain an alternative number** (that's the banned hybrid). Gate status also controls the Summary: modeled figures reach the Summary bullet only when the gate passes — a caveat in the Impact body does not travel with a number quoted from the Summary.
- **Variants and factors:**
  0. **Open with the key insight and its takeaway** (Minto): the winning combination, why it wins in one or two sentences, and the portable design rule the customer can reuse on other surfaces. Lead with the strongest defensible finding, which is typically the largest main effect with direct validation, rather than the most intriguing one; subtler findings (an interaction result, a settled design question) follow in one sentence as a second finding. The section's tables exist to support this opener, and the rule is not restated at the bottom.
  1. **Winning variant + top 3 contenders** — exactly 4 variant rows, with a **variant # column**, plus the baseline as a reference row: rates, traffic share (weight and P(best) are one number in two scalings; quote one — and note the weight-denominator trap from the Progress bullet: weights include the holdout share, while the document reports share of optimized traffic), and the baseline's exposure count — the original was measured thoroughly, more exposures than any variant except the winner, and lost. Include variant screenshots when they've been uploaded to the platform.
  2. **Factor-level utilities** — average effect vs. the original level, in pp, labeled *model estimates*, every level on its own row — and **interaction effects** — top observed-vs-additive deviations from raw per-user data, in pp with n and z, headed by the LR statistic that licenses them (method and traps in [cross-effects.md](references/cross-effects.md)). Level *contrasts* are fine as labeled model estimates; modeled lift-vs-baseline figures stay out. Saturation exceptions (both levels weak, positive term) go in a footnote, never a peer row. Mark |z| < 2 rows *directional* and phrase any narrative resting on them accordingly — claim strength tracks the evidence inside this section too.
  3. **Context factors, if the optimization has them** — context factor importance and best variant per context. This needs the context-aware model state (#333, not shipped) — until then say it's not yet reportable rather than guessing.
  4. **After the interaction table, interpret it**: state what the deviations show (mechanism, worst cell, any dependence of the winner on a pairing), with directional labels respected. The insight and the portable rule already live in the section opener.
- **Recommended action** — a bold opener stating whether a decision is needed now, then a short numbered list of clear actions (the exemplar uses three), each beginning with a bold imperative phrase and carrying its condition inline (guardrail status, how much more data, path (a) vs. (b) with the measurement consequence). A ship/lock-in recommendation names the mechanism and its measurement consequence: keep serving through Levered (no engineering, holdout keeps measuring) vs. hard-code the variant and end the optimization (measurement ends too).
- **Method notes** — fine print: after a `---` section break, **one italic paragraph beginning `*Method notes: …*`** — inline label, no headline. Counting basis, conversion window, where measurement starts and why. A mid-run change becomes one neutral line here, not a story.

Rules that keep it customer-safe:

- **Neutral analyst voice.** Write as if the customer's own analysts prepared the report for their management, not as the vendor. No vendor first person ("we recommend", "Levered is delivering") and no sales-pitch sentences; verdicts are attributed to the data ("sign-up conversion is measurably higher on the optimized screen"), recommendations are stated impersonally ("path (a) is preferable"), and the platform is named only as a system component when mechanics require it. Label comparison arms neutrally (Optimized vs. Holdout).
- **Open questions are reported as questions answered.** When the test settles something the team wondered about, write "whether X was an open question going into the test, and the answer is Y", never "the hypothesis that X was wrong". The report informs colleagues; it defeats nobody.
- **Succinct copy, minimal prose.** The document is tables and short claim sentences, not essay paragraphs. Prose budget: one bold claim sentence plus at most one supporting sentence per section opener; at most one or two sentences after any table; nothing that only connects, recaps, or narrates. If a fact fits a table cell, it does not also get a sentence; if a sentence can be deleted without losing a claim or a number, delete it. When in doubt, shorter.
- **Style: complete sentences, no dashes, affirmative statements.** Prose is written in full sentences, and that includes table lead-ins: never a bare noun-phrase label with a colon ("Modeled estimates, the Lift (now) cards:") — every lead-in is a complete sentence whose claim gives the so-what, with any dashboard cross-reference as the supporting clause. Dashes are replaced by periods, commas, and colons. Numeric ranges in prose read "500 to 700" (compact notation stays fine inside tables). Bullet points are sentences too, starting with a capital and ending with a period. State what the data shows rather than negating an objection: "the original screen received a thorough test" instead of "was not under-tested", and "levels interact" instead of "the utilities do not simply add". Honest statistical findings ("no detectable change") keep their negation, because there the negative IS the result. Language stays literal: no figurative idioms ("restarts the clock", "locks in the win", "banks the result"); standard statistical phrasing ("the interval narrows") is fine.
- **No internal machinery.** No issue numbers, no CLI/dashboard discrepancies, no validation narration, no day-over-day p-value movement.
- **Standalone test.** Nothing may require having followed the investigation; if a sentence only makes sense against yesterday's version, cut it.
- **Claim strength tracks the data.** "Statistically significant" only when it has held for a week or more; while it oscillates around the threshold, write "at the threshold of significance" — the customer will re-read this document after the numbers move.
- **No charts.** The user retired all SVG/image charts from the deliverable (2026-08-03), including the interaction heatmap and any trend chart. Evidence that used to be a chart is rendered as a compact markdown table or dropped.

**Pattern claims ship with their complete evidence.** Any interaction or mechanism claim in the document is accompanied by the full masked matrix, never only the supporting rows — a short top-deviations table plus the full matrix as a compact markdown table (rows = one factor's levels, columns = the other's, cells = deviation in pp, masked cells as `·`). The artifact that could falsify the claim travels with the claim; a reader who can check the story is the report's last line of defense.

**The analyst's addendum — to the user in chat, never in the document.** After the document, add a short note with what the user needs but the customer must not carry: which validity checks fired and how they shaped the document (exclusions, softened claims), the measured-vs-modeled gap and its diagnosis, anything oscillating day to day, open platform issues. A validity finding outranks a variant finding — it lands here first, and it is *why* the document says what it says.

### 6. Decide the recommendation — it lands in Recommended action

Recommend the **highest-leverage move the evidence supports** — help the team have impact with confidence, don't just pick from a menu. Common calls:

- **Ship the winner** — clearly ahead, tight interval, adequate exposures. Quote the **measured** lift, never the modeled ceiling.
- **Prune a level** — clearly dragging, tight interval, enough exposures. Name it. **Never prune an index-0 (baseline) level** — it's the measurement anchor.
- **Keep running** — leader still overlaps, or variants under-exposed. Say roughly how much more data you'd want. When the bandit has already concentrated (weight > ~90% on one variant), exploration is over and the only open question is proof — the recommendation is usually "change nothing, let the holdout accumulate," because any change restarts that clock.

Surface the structural insight when the analysis reveals one — often higher-leverage than any ship/prune: drop a noise factor to concentrate learning, merge redundant levels, consolidate two factors **only when the cross effects show true synergy** (see the synergy-vs-saturation rule in [cross-effects.md](references/cross-effects.md) — a positive interaction between two *negative* levels is a floor effect, not an argument to combine them), or spin up a follow-up around the dominant factor.

**Always check guardrails before recommending a ship.** Run `levered optimizations guardrails <id>` and let the status drive the wording: all `ok` → the recommendation may state that guardrails show no violation, naming the metrics; any `pending` or `violated` → say so and condition the ship on it. The wording rule from Impact applies here too: an `ok` whose CI cannot rule out material harm is "no detectable change", never "no degradation".

## Principle: present published metrics, analyze raw data

Two rules, not one. (1) For anything the dashboard already shows — lift, factor importance, users, rates, probability-of-best — use the value from `results`; don't re-derive it (your number will drift from the dashboard and confuse the user). (2) For insights the platform *doesn't* publish — cross effects, custom breakdowns, segment cuts, post-change recomputations — do the analysis yourself on raw data via `models state` or `levered warehouse query`. That's the analyst's value-add. **Never recompute a published number; always feel free to compute an unpublished one.**

## Scope — what this skill cannot tell you (today)

- **Individual past decisions.** The platform logs the chosen variant per serve, not the per-variant probabilities at that moment — "why did user X get variant Y" needs decision-time logging that doesn't exist yet.
- **Context × design (personalization) effects.** "Wins on mobile, loses on desktop" needs the context-aware model state that isn't shipped (#333). Design×design interactions you *can* derive (see cross-effects.md); context-conditional ones you cannot — say so rather than guessing.

If asked for any of these, say plainly it's a backend gap — don't fabricate a decision trace or a personalization read.

## Portfolio reads (`all`)

Lead with a one-row-per-optimization scoreboard: name, status, best lift so far, confidence (tight/wide), one-word call (ship / prune / wait). Offer to drill into any single one with the full report. Flag cross-experiment patterns only when the evidence is real — don't over-read a small portfolio.

## Troubleshooting

- **No results / "still training"** — needs exposures. Check `observations <id>` for incoming data and `show <id>` for status; if exposures aren't flowing, the integration or reward join is the issue — hand off to platform setup.
- **Flat lift** — confirm the reward metric fires (`levered metrics preview <id>`) and `anonymous_id` matches between exposures and rewards. No join → no learning.
- **Wide intervals everywhere** — early days or too many variants spreading traffic thin. Recommend patience; quote exposure counts.

For deeper concepts: [concepts.md](../levered-platform/concepts.md) and [docs.levered.dev/docs/concepts/optimizations](https://docs.levered.dev/docs/concepts/optimizations).
