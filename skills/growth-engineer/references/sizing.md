# Sizing a design to traffic

Every design you propose — and every addition to a live one — comes with how long it should take to settle. The user should never wonder whether "nothing yet" after a week is normal.

## Get the volume

You need roughly how many **reward events per week** reach the optimized surface. Take the best source you have, and say which one you used:

1. Real counts: an existing metric's `levered metrics preview <metric-id>`, or the optimization's own numbers once it runs (`levered optimizations progress <id> --json`).
2. The analytics knowledge (PostHog / Mixpanel report in `levered knowledge list --json`).
3. A traffic estimate from research in `.levered/research/`, if any — label it an estimate.
4. If none of these exist, **assume** — don't ask and don't skip. Pick a sensible range from what you can see of the product's stage and audience (paid ads, reviews, the size of the brand), say it in a clause, and give the time to settle from it: "Assuming <the range you picked>, about <a range of weeks> — tell me if traffic is very different." A design without a time to settle is incomplete.

## The rule of thumb

Levered's model learns each option of each change on its own, and every visitor counts toward every change at once. So the data it needs grows with the **options of the largest change**, not with the number of versions: another change adds a little on top, not a multiple.

Detecting a 20% relative lift needs about **400 reward events per option**; a 10% lift about 1,600. The need falls with the square of the effect: a change that **doubles** the rate needs only a few dozen per option.

**Expected time to settle ≈ options in the largest change × events needed ÷ weekly reward events × 1 / (1 − holdout share)**, using the effect you honestly expect. Give a range ("about 2–4 weeks"), never a winner date.

**Context factors are the exception.** A winner per segment is learned within each segment, so to personalize, each segment you care about has to settle on its own traffic: work out the time from the smallest of them.

## Using it

- **Choose the reward and the number of versions together.** If even the smallest design worth running won't settle within about six weeks, use a higher-volume reward and keep the deeper one as a guardrail.
- **Keep it at or under 100 versions,** so the user can review them and read the results.
- **When traffic is thin, rank what you'd change by the effect you expect, not by how interesting it is.** Keep the changes likely to move the rate a lot — they're also the ones you can measure on little traffic — and cut the ones whose effect would be small. If a change is close to certain to help, suggest shipping it outright instead of spending visitors proving it.
- **Never plan to add a factor after launch** to make a design smaller now — a live optimization can't take one yet.
- **Show the numbers when trimming:** the traffic and rate you assumed, how long the full design would take, and how long the trimmed one would.
