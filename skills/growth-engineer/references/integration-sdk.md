# Wiring the SDK

Used in phase 3 once the optimization exists. Covers a connected warehouse and the Managed Warehouse.

Now replace the local-override scaffolding with a real `useVariant` hook bound to the optimization you just created. The fallback must stay the same — it's already the current UI.

1. **Add the `onExposure` callback to the provider.** Without it, Levered has no data to train on. Keep the env-driven `apiUrl` from the prototype step. For a **connected** warehouse, log the exposure into the customer's own warehouse (via their analytics pipeline):
   ```tsx
   <LeveredProvider
     apiUrl={LEVERED_API_URL}
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

   **If the org is on the Managed Warehouse** (checked in phase 3), don't log to a customer warehouse — you must wire **both** halves: POST every **exposure** to Levered's ingestion API, and POST the **reward** at the conversion point. Miss either and the model can't learn — exposures with no rewards give no signal, rewards with no exposures have nothing to attribute to.

   - **Prod ingestion URL:** `https://api.levered.dev/api/v2/ingest` (the `/exposures` and `/rewards` paths below). Drive the base from the same env-based `LEVERED_API_URL` as the provider so testing/local still work, but production ingestion must hit the prod host.
   - **API key — create it yourself and keep it server-side** (phase 3, step 6): a **write secret**, never in a `NEXT_PUBLIC_` / `VITE_` variable or the client bundle. Because `onExposure` runs in the browser, point it at a small backend route in the user's app that holds the key and forwards the event — don't `fetch` the ingestion API from the client with the key.

   Exposure — from the backend route, on each exposure:
   ```ts
   await fetch('https://api.levered.dev/api/v2/ingest/exposures', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.LEVERED_API_KEY}` },
     body: JSON.stringify({ events: [{
       anonymous_id: exposure.anonymousId,
       optimization_id: exposure.optimizationId,
       variant: exposure.variant,
     }] }),
   });
   ```

   Reward — from the backend, at the conversion point:
   ```ts
   await fetch('https://api.levered.dev/api/v2/ingest/rewards', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.LEVERED_API_KEY}` },
     body: JSON.stringify({ events: [{
       anonymous_id: anonymousId,   // SAME id sent on the exposure — the join key
       name: '<reward-name>',       // the reward metric name
       value: 1,                    // numeric amount; 1 = a conversion
     }] }),
   });
   ```
   See the Managed Warehouse section of the `levered-platform` skill for all fields and response codes (e.g. `409` = org not on the managed warehouse, `207` = partial accept, `403` = unknown/unauthorized `optimization_id`).

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

4. **The anonymous id** is the one from the prototype ([prototype.md](prototype.md)), and the reward must carry the same id. On a connected warehouse, the exposure must land with `anonymous_id`, `optimization_id`, `variant` and `timestamp` columns.

For non-React apps, use `LeveredClient` directly instead of the hook.

Docs: [Integrate the SDK](https://docs.levered.dev/docs/getting-started/integrate-sdk).
