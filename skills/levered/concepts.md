# Levered Concepts

## What Levered Does

Levered is an optimization platform that uses contextual multi-armed bandits (CMABs) to automatically find the best variant of anything — headlines, CTAs, prices, layouts, email subjects, etc. Unlike traditional A/B testing, Levered continuously learns and shifts traffic toward winning variants in real time.

## Core Concepts

### Optimization
An optimization is the top-level entity. It defines what you're testing (design factors) and what success looks like (reward metric). Each optimization has one model that learns from data.

### Design Factors
The things you're varying. Each factor has a name and a list of levels (possible values). The combination of all factor levels produces the variant space.

Example:
- Factor `headline` with levels `["Fast", "Reliable", "Simple"]`
- Factor `cta_text` with levels `["Try Now", "Get Started"]`
- This produces 3 x 2 = 6 total variants

### Context Factors (optional)
Attributes about the user/session that the model uses to personalize variant selection. Examples: `device`, `country`, `time_of_day`. When context factors are provided, the model learns which variants work best for which contexts (true contextual bandit).

### Model Type: CMAB
Contextual Multi-Armed Bandit. Uses Thompson Sampling with Bayesian logistic regression. The model maintains a posterior distribution over variant effectiveness and samples from it to balance exploration (trying different variants) and exploitation (showing the best).

### Reward
The success signal. Usually binary (bool) — did the user convert? Can also be numeric. Defined by a warehouse metric that queries your data warehouse.

### Metric
A SQL query against your connected data warehouse that defines how to measure rewards. Maps columns to `anonymous_id`, `timestamp`, and optionally `value`. Levered periodically runs this query to get fresh reward data.

### Warehouse Connection
Levered connects to BigQuery or Snowflake to pull reward data. The connection is per-organization.

### Exposures
Each time a variant is served to a user, that's an exposure. Exposures are logged and joined with rewards for model training.

### Lift
The improvement in conversion rate that Levered's optimization provides over random/uniform assignment. Shown as a percentage with confidence intervals.

### Serve
The API call that returns the best variant for a given user. The model uses Thompson Sampling to select, considering the user's context if available.

## Typical Workflow

1. **Connect warehouse** — Link BigQuery/Snowflake so Levered can read reward data
2. **Create metric** — Write SQL that defines what a "conversion" is
3. **Create optimization** — Define design factors (what to vary) and link the reward metric
4. **Integrate SDK** — Add `@levered_dev/sdk` to the app, call `useVariant()` or `getVariant()`
5. **Monitor** — Check results, lift, and variant performance via CLI or dashboard
6. **Iterate** — Add/remove levels, adjust factors, create new optimizations

## Key Numbers

- Model retrains automatically as new data arrives
- Serve latency: ~50ms p95
- SDK has a 2s timeout with graceful fallback
- Lift is reported with 95% confidence intervals
