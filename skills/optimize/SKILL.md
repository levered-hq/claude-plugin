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

### 2. Understand What to Optimize

Read the user's codebase. Find the component, page, or feature they want to optimize. Look at:
- The UI code (what text, layout, or behavior varies)
- The existing analytics/tracking (how conversions are measured)
- The tech stack (React? Next.js? Vanilla? Server-rendered?)

From this, determine:
- **Design factors**: What should vary and what are good levels? Be creative but grounded. If optimizing a headline, propose 4-6 compelling alternatives. If optimizing a CTA, propose 3-4 action-oriented options.
- **Reward**: What counts as success? (click, signup, purchase, etc.)

### 3. Check Prerequisites

```bash
levered warehouse status
levered metrics list
```

- If no warehouse connected, tell the user they need to connect one and offer to help.
- If no suitable reward metric exists, create one.
- If a suitable metric already exists, use it.

### 4. Create the Optimization

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

### 5. Integrate the SDK

This is the most important step. Modify the user's code to:

1. **Install the SDK** if not already present:
   ```bash
   npm install @levered_dev/sdk
   ```

2. **Add the provider** (React apps) — find where the app root is and wrap it:
   ```tsx
   import { LeveredProvider } from '@levered_dev/sdk/react';

   <LeveredProvider apiUrl="https://api.levered.dev" anonymousId={anonymousId}>
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

For non-React apps, use `LeveredClient` directly instead of the hook.

### 6. Summarize

Tell the user what you did in 3-4 sentences:
- What optimization was created (name + ID)
- What design factors and levels you chose
- Where in their code the SDK was integrated
- What they need to do next (deploy, and rewards will start flowing)

Don't dump CLI output. Don't over-explain. Be brief and confident.

## Important Rules

- **Be opinionated.** Pick good factor levels yourself. The user said "optimize my headline" — they want you to propose the variants, not ask them what the variants should be.
- **Use existing patterns.** If the codebase already has analytics, env vars for API URLs, or user ID generation — use those. Don't reinvent.
- **Fallback values = current values.** The fallback in `useVariant` should always be what the component currently shows, so nothing changes if the API is down.
- **One component at a time.** Don't try to optimize the entire page. Focus on what the user asked about.
- **Show the optimization ID.** The user will need it to check results later.
