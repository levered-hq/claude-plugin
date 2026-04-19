---
name: optimize
description: End-to-end optimization setup. Claude proposes a design, prototypes the variants in your app so you can preview and iterate in the browser, and only wires up the Levered backend once you approve.
argument-hint: [what to optimize]
allowed-tools: Bash(levered *), Bash(npm *), Bash(npx *), Bash(yarn *), Bash(pnpm *), Read, Grep, Glob, Edit, Write
---

# End-to-End Optimization

The user wants to optimize something. You own the whole flow. Be opinionated about the design, but work in two phases: **prototype first, wire up second.**

1. **Prototype phase** — propose the design, implement the variants in the user's code with a local preview (no Levered backend yet), and let the user click through every variant in the browser. Iterate on factors, levels, copy, and layout based on what they see. Stay here until the user explicitly says they're happy.
2. **Wire-up phase** — only after approval, create the optimization in Levered, swap the local preview scaffolding for `useVariant`, and set up exposure logging.

Creating the optimization in the backend and wiring `useVariant` too early wastes the user's time: once an optimization is live, changing factors or levels means archiving and recreating. The preview loop is where design decisions get made.

## Your Job

Take "$ARGUMENTS" and make it happen. The user should not need to touch the terminal or make decisions unless truly ambiguous.

## Steps

### 1. Preflight

Confirm the CLI is installed, silently:

```bash
levered --version
```

If the CLI is not found, install it:
```bash
curl -fsSL https://cli.levered.dev/install.sh | bash
```
Then source the user's shell profile or use `~/.levered/bin/levered` so the command is available in the current session.

**Do not check auth or environment yet.** Login and warehouse/metric checks are deferred to the wire-up phase (step 6) — there's no point interrupting the user with a login prompt just to prototype in the browser.

### 2. Understand What to Optimize

Read the user's codebase. Find the component, page, or feature they want to optimize. Look at:
- The full flow the user goes through to reach the reward (not just one screen — the path from entry to conversion)
- The UI code: copy, layout, structure, steps, defaults, required vs. optional fields, what's shown vs. hidden
- The existing analytics/tracking (how conversions are measured)
- The tech stack (React? Next.js? Vanilla? Server-rendered?)

From this, determine:

- **Reward**: What counts as success? (click, signup, purchase, activation, revenue, etc.)
- **Design factors**: *What has the highest potential to move the reward metric?* Pick the biggest levers available, not the safest ones. Copy is one lever — often not the strongest. Consider the full space:
  - **Structural**: add or remove a step, collapse multi-step into single-step (or vice versa), change the order of steps, skip a screen, consolidate or split forms
  - **Flow**: change what happens on load vs. on click, gate vs. ungate content, defer sign-up vs. require it upfront, auto-advance vs. manual
  - **Layout**: one-column vs. two-column, above-the-fold composition, where the primary CTA sits, what's visible without scrolling, sticky vs. inline elements
  - **Content presence**: show/hide social proof, testimonials, pricing, FAQ, trust badges, progress indicators, example outputs
  - **Defaults**: pre-selected plan/option, pre-filled fields, opt-in vs. opt-out toggles, default quantities
  - **Copy**: headline, subheadline, CTA wording, value proposition framing, tone — use when structural/flow options are exhausted or genuinely expected to dominate

  Pick 1–3 factors that plausibly swing the metric by meaningful amounts. Don't pad the design with factors you don't believe in — each extra factor spreads traffic thinner. And don't restrict yourself to copy swaps just because they're easy to implement; if removing a step is the highest-leverage change, propose removing the step.

  **Exclude colors.** Colors are not a real lever — they almost never move conversion meaningfully. Don't propose them.

  **Don't invent content, period.** Variants must test *presentation* of what exists — not introduce claims, features, or content the app doesn't actually have. This is broader than commercial terms; it applies to everything:
  - **Commercial**: no invented pricing, guarantees, refund policies, trial lengths, discount codes, urgency framings, bundled features.
  - **Product specifics**: no invented workouts/exercises, menu items, lesson content, course modules, recipe steps, session durations.
  - **Outcome claims**: no invented result stats ("−4.2 kg in 4 weeks"), projected progress charts, conversion numbers.
  - **Social proof**: no invented testimonials, names, quotes, review counts, star ratings.
  - **Process claims**: no copy that implies the app does something it doesn't ("Calibrating intensity…" implies real calibration).

  Every invented element makes the variant un-shippable — if it wins, the business still can't deploy it. If you don't know whether something is real, **stop and ask the user**. Don't assume and don't fabricate plausible-looking placeholders. Reframing, re-ordering, or showing/hiding real content is fine; inventing new assertions is not.

  When you present the plan, briefly explain *why* you chose these factors — the hypothesis about why they'll move the metric.

### 3. Propose the design

Before creating anything or touching code, present the proposed reward, factors, and hypothesis in a short message. Keep it to one short paragraph plus a factor table — not a menu of alternatives to pick from, but a concrete plan the user can approve or redirect. End with a single closing question like "Want me to prototype these in the app so you can click through them?"

Do not edit application code yet. If they push back on a factor, revise and re-propose rather than starting the prototype.

### 4. Prototype with preview (no backend yet)

Once the user approves the design, implement the variants locally so they can click through every level in the browser — without creating anything in Levered's backend. This is the design-review phase.

For React apps, the preview tool is `LeveredAdminMenu` from `@levered_dev/sdk/react`. It's a floating admin pill that lets the user override factor values at runtime. Set it up like this:

1. **Install the SDK if not already present** and wrap the app root in `LeveredProvider` — no `optimizationId` is needed for preview; you just need the provider so the menu component works:
   ```tsx
   import { LeveredProvider } from '@levered_dev/sdk/react';

   <LeveredProvider apiUrl="https://api.levered.dev" anonymousId={anonymousId}>
     <App />
   </LeveredProvider>
   ```

2. **Define factors as local state**, with fallback values matching today's UI (so the baseline *is* the current experience):
   ```tsx
   const FALLBACK = {
     results_reveal: 'none',
     plan_price_framing: 'free_trial_first',
     social_proof_placement: 'plan_only',
   }

   const ADMIN_VARIANTS = [
     { name: 'results_reveal', label: 'Results Reveal',
       options: [{ value: 'none' }, { value: 'analyzing_only' }, { value: 'analyzing_plus_projection' }] },
     // ...
   ]

   const [override, setOverride] = useState<Record<string, string | number | boolean>>(FALLBACK)
   const active = { ...FALLBACK, ...override }
   ```

3. **Render the admin menu** near the app root:
   ```tsx
   <LeveredAdminMenu
     enabled
     variants={ADMIN_VARIANTS}
     currentValues={active}
     onOverride={(o) => setOverride(o as Record<string, string>)}
     onReset={() => setOverride(FALLBACK)}
   />
   ```

4. **Branch the UI on `active.<factor>`** to implement each level. Structural/flow/layout factors may require new components or altered step sequences — that's expected, and why we do this before wire-up.

5. **Guide the user to preview.** After you implement, tell them exactly how to try it:
   - Which URL to open (the dev server the demo/app is running on).
   - Where the admin pill appears (usually bottom-right; labeled "Levered").
   - Which combinations are worth seeing first (e.g., "try `results_reveal = analyzing_plus_projection` with `plan_price_framing = anchored_price` — that's the boldest cell").

For non-React apps, fall back to a query-param switch or feature-flag toggle and document it for the user in the same way.

### 5. Iterate until the user is happy

Expect multiple rounds. The user will look at variants and want to change things: reword a level, add/remove a level, drop a factor, rethink the structural change. Each time:

- Make the edits in the prototype (including the `FALLBACK` / `ADMIN_VARIANTS` definitions if factors/levels changed).
- Hand control back: "refresh and try it."
- Do **not** move to wire-up on your own initiative. Wait for an explicit signal like "looks good, wire it up" or "ship it." "Yeah" in response to showing a variant is not approval to create the optimization.

### 6. Check prerequisites (auth, warehouse, metrics)

Only enter this step once the user has explicitly approved the prototype.

```bash
levered whoami
levered env
levered warehouse status
levered metrics list
```

- If not authenticated, tell the user to run `levered login` (requires a browser) and stop.
- If not on the right environment, switch with `levered env use <prod|testing>` based on what the app's `apiUrl` points at.
- If no warehouse connected, tell the user to set one up in the Levered dashboard (https://app.levered.dev — Settings > Warehouse). Stop until they complete it.
- If no suitable reward metric exists, create one. If one exists, use it.

### 7. Create the Optimization

```bash
levered optimizations create \
  --name "..." \
  --design-factors '[...]' \
  --reward-metric-id <uuid> \
  --model-type cmab \
  --reward-name reward \
  --reward-type bool
```

The `--design-factors` JSON must match the factors and levels the user just approved in the prototype. Choose a clear, descriptive name. Don't ask the user what to name it.

### 8. Wire up `useVariant` (swap the preview scaffold)

Now replace the local-override scaffolding with a real `useVariant` hook bound to the optimization you just created. The fallback must stay the same — it's already the current UI.

1. **Add the `onExposure` callback to the provider.** Without it, Levered has no data to train on:
   ```tsx
   <LeveredProvider
     apiUrl="https://api.levered.dev"
     anonymousId={anonymousId}
     onExposure={(exposure) => {
       analytics.track('levered_exposure', {
         optimization_id: exposure.optimizationId,
         anonymous_id: exposure.anonymousId,
         variant: exposure.variant,
         timestamp: new Date().toISOString(),
       });
     }}
   >
     ...
   </LeveredProvider>
   ```

2. **Swap `override` state for `useVariant`** in the target component:
   ```tsx
   import { useVariant } from '@levered_dev/sdk/react';

   const { variant } = useVariant({
     optimizationId: '<the-uuid-you-just-created>',
     fallback: FALLBACK,  // same object used in the prototype
   });
   const active = variant ?? FALLBACK
   ```

3. **Keep `LeveredAdminMenu`** for internal QA — pass `enabled={process.env.NODE_ENV !== 'production'}` so it disappears in prod.

4. **Handle anonymous ID** — use whatever the app already has (cookies, session IDs, analytics IDs). If nothing exists, generate a UUID in localStorage.

5. **Set up exposure logging** — use whatever pipeline the app already has (Segment, Rudderstack, PostHog, direct warehouse inserts). The exposure must land in the warehouse with `anonymous_id`, `optimization_id`, `variant`, and `timestamp` columns.

For non-React apps, use `LeveredClient` directly instead of the hook.

Docs: [Integrate the SDK](https://docs.levered.dev/docs/getting-started/integrate-sdk).

### 9. Summarize

Tell the user what you did in 3-4 sentences:
- What optimization was created (name + ID)
- What design factors and levels you chose
- Where in their code the SDK was integrated
- How exposure logging was set up
- What they need to do next (deploy, and rewards will start flowing)
- Link to relevant docs for further reading (e.g., [Getting Started](https://docs.levered.dev/docs/getting-started))

Don't dump CLI output. Don't over-explain. Be brief and confident.

## Important Rules

- **Prototype first, wire up second.** Never call `levered optimizations create` or swap in `useVariant` before the user has seen the variants in the browser and explicitly approved them. The preview loop is where design decisions get made — once the optimization exists in the backend, changing factors means archiving and recreating.
- **"Wire this up" is ambiguous — resolve it.** If the user says "yes" or "wire it up" after you propose the design, interpret it as "build the prototype so I can preview it," not "create the optimization in Levered." When in doubt, say what you're about to do: "I'll build the variants locally with a preview pill — no Levered backend yet — so you can click through them."
- **Aim for impact, not safety.** The goal is to move the reward metric as much as possible. Copy-only optimizations cap out at small single-digit lift; structural and flow changes can deliver much more.
- **Be opinionated.** Pick the factors and levels yourself. The user wants a proposed plan, not a menu.
- **Scope honestly.** If a high-leverage change requires more code, do it. Flag the extra scope in your summary but don't shy away from it.
- **Use existing patterns.** If the codebase already has analytics, env vars for API URLs, or user ID generation — use those. Don't reinvent.
- **Fallback = current UI.** The `FALLBACK` object during prototyping (and `useVariant` fallback during wire-up) is always the current live experience, so the baseline is an unchanged user journey.
- **Focus the scope.** Optimize one well-chosen surface at a time.
- **Show the optimization ID.** After wire-up, give the user the ID so they can check results later.
