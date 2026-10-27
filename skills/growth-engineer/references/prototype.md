# Prototype with preview (no backend yet)

The local preview loop used in phase 2.

Once the user approves the design, implement the variants locally so they can click through every level in the browser — without creating anything in Levered's backend. This is the design-review phase.

For React apps, the preview tool is `LeveredAdminMenu` from `@levered_dev/sdk/react`. It's a floating admin pill that lets the user override factor values at runtime. Set it up like this:

1. **Install the SDK if not already present** and wrap the app root in `LeveredProvider` — no `optimizationId` is needed for preview; you just need the provider so the menu component works. Pull the API URL from an env var using whichever style the app already uses, so the same build works against local / testing / prod. Default to prod only so the provider mounts — during prototype the admin menu overrides the variant, no API call is needed.

   ```tsx
   import { LeveredProvider } from '@levered_dev/sdk/react';

   const LEVERED_API_URL =
     process.env.NEXT_PUBLIC_LEVERED_API_URL ?? 'https://api.levered.dev';

   <LeveredProvider apiUrl={LEVERED_API_URL} anonymousId={anonymousId}>
     <App />
   </LeveredProvider>
   ```

   Use the framework's own public prefix and env access (`NEXT_PUBLIC_` with `process.env` in Next.js, `VITE_` with `import.meta.env` in Vite, and so on): the wrong prefix silently falls back to prod.

   **`anonymousId` is required** — the stable id of this visitor, the same one the reward will carry. Reuse the analytics tool's id when there is one (PostHog `posthog.get_distinct_id()`, Mixpanel `mixpanel.get_distinct_id()`, Segment `analytics.user().anonymousId()`); otherwise a random id kept in `localStorage`. Don't leave it out: the provider won't type-check without it.

2. **Define factors as local state**, with fallback values matching today's UI (so the baseline *is* the current experience):
   ```tsx
   const FALLBACK = {
     <factor>: '<today>',
     <factor>: '<today>',
   }

   const ADMIN_VARIANTS = [
     { name: '<factor>', label: '<Factor, in plain words>',
       options: [{ value: '<today>' }, { value: '<option>' }, { value: '<option>' }] },
     // ...
   ]

   const [override, setOverride] = useState<Record<string, string | number | boolean>>(FALLBACK)
   const active = { ...FALLBACK, ...override }
   ```

   Also initialize the override from a `levered_variant` URL query param (JSON of factor values). This makes every variant addressable by URL — which lets you screenshot variants headlessly (below) and lets the user deep-link a teammate to a specific combination:
   ```tsx
   useEffect(() => {
     const raw = new URLSearchParams(window.location.search).get('levered_variant')
     if (raw) try { setOverride({ ...FALLBACK, ...JSON.parse(raw) }) } catch {}
   }, [])
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

5. **Look at every version yourself before asking the user to click through.** If this session has a browser tool, use it: open each version's `?levered_variant=` link on the dev server and look. Otherwise, with the dev server running, take one screenshot per version with the Playwright command line — one plain command per version, run from the project root like the `npx playwright install chromium` that installed its browser, so both use the same Playwright:

   ```bash
   npx playwright screenshot --viewport-size=1280,900 --wait-for-timeout=1500 "http://localhost:<port>/<path>?levered_variant=<the version's factor values as URL-encoded JSON>" node_modules/.cache/levered-screenshots/<nn>-<version>.png
   ```

   The `levered_variant` value is the version's factor values as URL-encoded JSON. Save them inside the project in `node_modules/.cache/levered-screenshots/` — the command creates the folder, so no `mkdir`, and no warm-up request first (it waits for the page) (already gitignored, and readable without a permission prompt, unlike `/tmp`), and look at them yourself before showing the user anything (phase 2, step 3). They're your own throwaway check; durable, dashboard-visible screenshots come later via `levered optimizations screenshot`. The browser starts installing in the background when the user says yes; if it isn't ready yet, wait for it.

6. **Present it** as phase 2, step 3 describes: open the page on the dev server, where the admin pill (usually bottom-right, labeled "Levered") switches between the versions, with your view and recommended tweaks.

For non-React apps, fall back to a query-param switch or feature-flag toggle and document it for the user in the same way.
