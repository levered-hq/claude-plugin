# Phase 1 — First look

Goal: within a minute or two, learn what the user wants more of and show them something true and useful about how **their own product** gets in the way of it: where it loses those conversions, why, and what you'd try instead. Three short turns: the goal; the insights, which they confirm or adjust; then what you'd try — the moment they decide the tool is worth it. This file is self-contained, and may be read on its own before the plugin is installed (see the end).

**Each step after the goal is its content written out as text, ending with its question.** Both are markdown text in your reply and stay on the page after they answer: the question in a line, then its options numbered on one line, your pick first and marked (recommended), so they can answer with a number or in their own words. The user can't see your thinking: the findings reach them only as what you write. No preamble, no narration between reads, no recap of what you read.

**Until then, only read** — with the Read tool, several files at once, and Glob and Grep to find and search. They need no permission, while before the plugin is installed every shell command is a prompt. No installs.

**Words:** describe Levered as it is — versions of the page, live traffic, the model learning which works best. In this file, "options" means the choices you offer the user, except in the design table, where a change's options are its variations.

## 1. Read the project in one go

In a single turn, read together: `package.json`, `index.html` or the app's root layout, the README, the router or `App` file, and the pages it points to. With file-based routing there's no router file: read the root layout and the home page directly, then follow the nav's links and the page's imports. For a returning user with the CLI signed in, also `levered knowledge list --json`; otherwise don't touch Levered.

**The `<head>` is a source of true copy:** the title, meta description and social tags often say what the product is more clearly than the page does. So do the README and the knowledge base.

## 2. Settle the goal

From what you read, list the conversions this product records or offers: what the code tracks, the actions the page asks for, the steps of the funnel. Then, unless the user already named one, ask a single choice card (AskUserQuestion), with no table and no findings yet:

- **Question:** in one or two short sentences, that you've read their product (name the site or app) and what they want more of, and that you'll show where visitors drop off for it. The context goes in the question itself, so the card makes sense on its own.
- **First option, marked "(Recommended)":** the deepest conversion that still has the volume to learn, in plain words; its description says in one clause why (what you saw that records it).
- **One or two more options:** other conversions you found, earlier or later in the funnel, each with one clause.

Their answer sets the surface and the win for everything that follows. Your reply to it is the insights (§5, step 1): the problems written out as text in that reply, ending with its question.

**When their request already says enough, skip ahead.** A named goal: no card, straight to §3. A named surface but no goal: the card, about that surface. A design of their own: check it against §4 (the version count, the time to settle, coherent combinations, nothing invented), then show it as the design (§5, step 2) — their ideas as the rows, your view in a clause where you'd change something — ending with its question.

## 3. Find the surface and read it like a visitor

The goal decides where to look: the place where visitors make the decision it counts — for a page, usually the one paid traffic lands on; for a broad goal, the step where most of it is lost. If the user named a page or step, use it unless the evidence clearly points elsewhere (say so in a line).

Read it the way a first-time visitor would, with your knowledge of growth, UX research and behavioral science: what they see first, what they must do, what holds them back from the goal. Ground every observation in something real on the page or in the code, specific to this product.

## 4. Work out what you'd try

- **What counts as a win:** the goal they chose — the event the code records for it, or the tracking it needs if none does.
- **How many versions:** every combination a visitor can be served. Multiply, across the changes, each change's number of variations, today's included. It's what the user clicks through and what the table line shows; the time to settle comes from the options, below.
- **What do users outside the optimization see:** one of three answers, settled before designing.
    - *One combination is what visitors see today:* list its level first in every factor. That version is the baseline the gain is measured against, and the holdout is served it (`--control variant`, the default).
    - *The holdout keeps today's version, but today's version is none of the combinations* (for example the new versions all share a redesign and the holdout keeps the legacy component): the holdout is required and its users never train the model (`--control external`). Their app shows today's version whenever the SDK returns `isHoldout: true` and ignores the returned variant. When the code you're changing renders a different component in the holdout branch than in any version, this is the case: say so with the design.
    - *Nothing existed before* (a new screen or flow, every version new): no baseline, no holdout (`--control none`).

  Never call a new version the baseline because it's listed first. If the request doesn't make it clear, ask in one sentence before designing.
- **How many visitors:** from analytics if you have it; otherwise a sensible range from the product's stage and audience, said as an assumption. Time to settle ≈ the options of the change with the most × ~400 conversions ÷ weekly conversions, as a range: the model learns every change from all the traffic at once, so it grows with options, not versions (big changes need far fewer; [../references/sizing.md](../references/sizing.md)). If even the smallest design worth testing wouldn't settle within about six weeks, use a win with more volume that comes earlier in the same journey (keep the deeper one as a guardrail) or fewer versions, and say which in a line.
- **What to change:** draw on your best knowledge of product growth, conversion optimization, UX research and behavioral science to choose the changes most likely to move their goal on this surface — judged by the effect you expect, not by how easy they are to build. As many changes as the traffic can settle, and no more.
- **Every combination must make sense:** independent changes are separate factors; things that only work together are one factor. Each change alters what the visitor understands, believes or must do; styling alone isn't one. **Nothing invented:** every option uses what's real in the code, on the site, in the `<head>`, the README or the knowledge base. Draft the copy yourself.
- **What could strengthen it**, from what you've already read:
  - *Their analytics:* a tool connected in this session that reads this product's analytics (check the tools you have, as you check the code for tags); otherwise PostHog or Mixpanel running here (an init call, the package, its snippet, or events it fires) and not already synced to Levered (it syncs only those two).
  - *Public data worth researching:* a live URL for the product (`og:url`, `canonical`, `homepage`, a domain in the deploy config). With ads signals too (a Google Ads `AW-` tag, a Meta pixel, UTM handling, campaign-style routes), the research also checks where paid traffic lands.
- **How it's served:** the SDK when the page's code is in this repo; the web tag ([../references/integration-web-tag.md](../references/integration-web-tag.md)) when it isn't and the changes are copy, visibility or layout.

## 5. Show what you found, in two steps

How Levered works waits until launch. Names, classes, file paths and event names stay in the code: write in the visitor's terms, plain markdown, long quotes cut with "…".

### Step 1: what holds them back

The insights alone, before any change: so the user agrees on the problem first.

> <One line on how you looked at the page.>
>
> **What holds <visitors or users, by surface> back from <the goal, in plain words>**
>
> | | Problem | What we saw |
> |---|---|---|
> | 1 | **<The belief about the visitor, as a short claim>** | <One piece of evidence: today's real copy or element, quoted or named> |
> | … | … | … |
>
> <Only when you read real numbers: one line on where they actually drop off and what's at stake, with the number and its source.>
>
> <The question.> **1.** <Your pick> (recommended) · **2.** … · **3.** …

The 3–5 problems you'd act on, most important first. About 10 words per cell: the problem as a short claim; the evidence as only what a visitor sees, quoted or named, long quotes cut with "…" — what it means is already in the claim. The question asks whether the <n> problems above are the ones to work on; first **Show what I'd try**; then, only when §4 found something to strengthen it with, one option named for it (checking their analytics, researching their market in about 10 minutes, or both); last **Change these, or tell me your own hunch**.

When they change the problems, or bring a hunch, show them revised and ask the same question again. When they want to reason it out, rank as many hypotheses as the evidence supports, most likely first (who is stopped by what, the evidence, how we'd know), with your recommendation ([../references/factor-design.md](../references/factor-design.md), "The user's own hypotheses").

### Step 2: what we'd try

Once they confirm the problems: the design, one change per problem it answers. Exact wording is reviewed later, on the page itself.

> **What we'd try**
>
> | Change | Options | For example |
> |---|---|---|
> | <n>. <The change, for problem n, in a few words> | <How many, today's included> | <One new option, quoted or named> |
> | … | … | … |
>
> <The number of versions> versions; **a win** = <their goal, in plain words>; at <the traffic you assumed>, about <a range> to settle — tell me if traffic is very different.
>
> <The question.> **1.** <Your pick> (recommended) · **2.** … · **3.** …

Today's page is the baseline, so it gets no row; versions appear only as a count. About 10 words per cell: one new option, quoted or named; the others wait for the build. The question asks whether to build the <n> changes above: first, worded exactly, **Build these so I can click through**; then the strengthen option if they haven't used it; last **Change the design first**.

### If they pick the strengthen option

Do it, then show the same step again, revised: a line on what changed, with the number behind it, or that it held up; then the same question without the option they used.

- **Their analytics:** through the tool connected in this session when there is one, naming the project you read. Otherwise it needs a Levered sign-in (phase 3, §1), then the one link https://app.levered.dev/knowledge → **Connect PostHog** → **Sync**; check it with `levered knowledge list --json` and read it with `levered knowledge view`. Use the real numbers for the time to settle.
- **Research:** follow [../references/quick-research.md](../references/quick-research.md); say it takes about 5–10 minutes. If the plugin isn't installed yet, install it first (§6).

Don't touch application code until they say build.

## 6. If the plugin isn't installed yet

When this file was read on its own (the "first look" entry), install the plugin only once the user wants to build or picks research: `claude plugin marketplace add levered-hq/claude-plugin`, then `claude plugin install levered@levered` (two commands). Say in one line that the skill now loads by itself in their next sessions. Then carry on in this turn, without waiting for a reload: read the installed skill's `SKILL.md`, then `phases/2-prototype.md` after build or `references/quick-research.md` after research, and the files they point to. Read them from the plugin's folder (`claude plugin list` shows where), or from `https://raw.githubusercontent.com/levered-hq/claude-plugin/main/skills/growth-engineer/` followed by the same path.
