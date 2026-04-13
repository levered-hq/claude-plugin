---
name: optimize
description: End-to-end optimization setup. Claude owns the whole flow — analyzes your code, creates the optimization, integrates the SDK, and gets you live.
argument-hint: [what to optimize]
allowed-tools: Bash(levered *), Bash(npm *), Bash(npx *), Bash(yarn *), Bash(pnpm *), Read, Grep, Glob, Edit, Write
---

# End-to-End Optimization

The user wants to optimize something. You own this entirely. Be decisive, not consultative.

## Your Job

Take "$ARGUMENTS" and make it happen. The user should not need to touch the terminal or make decisions unless truly ambiguous.

## Steps

### 1. Preflight

Run these checks silently — don't narrate them unless something is wrong:

```bash
levered --version
```

If the CLI is not found, install it:
```bash
curl -fsSL https://cli.levered.dev/install.sh | bash
```
Then source the user's shell profile or use `~/.levered/bin/levered` so the command is available in the current session.

Then check auth and environment:
```bash
levered whoami
levered env
```

If not authenticated, tell the user to run `levered login` (requires a browser) and stop.
If not on the right environment, switch with `levered env use prod` (or whichever makes sense).

### 2. Check for Existing Optimizations

Before creating anything new, check if the target already has an optimization:

```bash
levered optimizations list
```

Also grep the codebase for existing `useVariant` or `getVariant` calls near the code the user mentioned — there may already be an optimization covering the same area.

- **If a matching optimization exists with status `completed`**: Tell the user there's already a completed optimization for this. Show the name and ID. Ask if they want to:
  1. **Apply the winner** — get results with `levered optimizations results <id> --json`, find the variant with the highest `weight`, hardcode it into the code, remove the `useVariant` hook, and clean up. See the levered skill's "Applying a Completed Optimization" section for the full procedure.
  2. **Create a new optimization anyway** — proceed to Step 3.
- **If a matching optimization exists with status `live`**: Tell the user there's already a live optimization running. Show the name, ID, and current results. Ask if they want to wait for it to complete, or create a separate optimization for a different aspect.
- **If no matching optimization exists**: Proceed to Step 3.

### 3. Understand What to Optimize

Read the user's codebase. Find the component, page, or feature they want to optimize. Look at:
- The UI code (what text, layout, or behavior varies)
- The existing analytics/tracking (how conversions are measured)
- The tech stack (React? Next.js? Vanilla? Server-rendered?)

From this, determine:
- **Design factors**: What should vary and what are good levels? Be creative but grounded. If optimizing a headline, propose 4-6 compelling alternatives. If optimizing a CTA, propose 3-4 action-oriented options.
- **Reward**: What counts as success? (click, signup, purchase, etc.)

### 4. Check Prerequisites

```bash
levered warehouse status
levered metrics list
```

- If no warehouse connected, tell the user to set one up in the Levered dashboard (https://app.levered.dev — go to Settings > Warehouse). This is a one-time setup best done from the UI. Stop and wait for them to complete it before continuing.
- If no suitable reward metric exists, create one.
- If a suitable metric already exists, use it.

### 5. Create the Optimization

```bash
levered optimizations create \
  --name "..." \
  --design-factors '[...]' \
  --reward-metric-id <uuid> \
  --model-type cmab \
  --reward-name reward \
  --reward-type bool
```

Choose a clear, descriptive name. Don't ask the user what to name it.

### 6. Integrate the SDK

This is the most important step. Docs: [Integrate the SDK](https://docs.levered.dev/docs/getting-started/integrate-sdk). Modify the user's code to:

1. **Install the SDK** if not already present:
   ```bash
   npm install @levered_dev/sdk
   ```

2. **Add the provider** (React apps) — find where the app root is and wrap it. The `onExposure` callback is **required** — without it, Levered has no data to train on:
   ```tsx
   import { LeveredProvider } from '@levered_dev/sdk/react';

   <LeveredProvider
     apiUrl="https://api.levered.dev"
     anonymousId={anonymousId}
     onExposure={(exposure) => {
       // Log to the user's warehouse/analytics pipeline
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

3. **Use the variant** in the target component:
   ```tsx
   import { useVariant } from '@levered_dev/sdk/react';

   const { variant } = useVariant({
     optimizationId: '<the-uuid-you-just-created>',
     fallback: { headline: 'Original Text', cta_text: 'Original CTA' },
   });
   ```

4. **Replace hardcoded values** with `variant.headline`, `variant.cta_text`, etc.

5. **Handle anonymous ID** — look for existing user ID patterns in the codebase (cookies, session IDs, analytics IDs). Use whatever the app already has. If nothing exists, generate a UUID stored in localStorage.

6. **Set up exposure logging** — look for existing analytics/tracking in the codebase (Segment, Rudderstack, PostHog, direct warehouse inserts). Use whatever pipeline the app already has. The exposure must land in the warehouse with `anonymous_id`, `optimization_id`, `variant`, and `timestamp` columns so Levered can join with reward data.

For non-React apps, use `LeveredClient` directly instead of the hook.

### 7. Summarize

Tell the user what you did in 3-4 sentences:
- What optimization was created (name + ID)
- What design factors and levels you chose
- Where in their code the SDK was integrated
- How exposure logging was set up
- What they need to do next (deploy, and rewards will start flowing)
- Link to relevant docs for further reading (e.g., [Getting Started](https://docs.levered.dev/docs/getting-started))

Don't dump CLI output. Don't over-explain. Be brief and confident.

## Important Rules

- **Be opinionated.** Pick good factor levels yourself. The user said "optimize my headline" — they want you to propose the variants, not ask them what the variants should be.
- **Use existing patterns.** If the codebase already has analytics, env vars for API URLs, or user ID generation — use those. Don't reinvent.
- **Fallback values = current values.** The fallback in `useVariant` should always be what the component currently shows, so nothing changes if the API is down.
- **One component at a time.** Don't try to optimize the entire page. Focus on what the user asked about.
- **Show the optimization ID.** The user will need it to check results later.
- **Detect completion.** If the user asks to optimize something that already has a completed optimization, don't blindly create a new one. Surface the completed results and offer to apply the winner first.
