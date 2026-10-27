# Wiring the web tag

For surfaces whose code isn't in this repository — a Webflow, WordPress or other marketing site, often exactly where paid traffic lands. The hosted script tag serves the optimization by writing the served levels into elements on the page. No SDK, no deploy per change.

## What it can and can't do

- **Can:** change text, HTML, attributes, styles and classes of existing elements, show or hide them, and insert content before or after them. That covers copy, visibility and layout of what's already on the page.
- **Can't:** remove a step, change a form's logic, reorder a flow, or change defaults. If the best design needs that, say so: propose the best design the tag can do, and give the structural idea to the team as a recommendation.
- **Runs on page load.** Pages that render content late or navigate client-side (app-like pages) are a poor fit: use the SDK there.

## Setting it up

1. Create the optimization as usual (phase 3). Each factor's first level is the page as it is today.
2. Write the bindings — one per factor, a CSS selector plus an action (`text`, `html`, `attr`, `style`, `class`, `insert_before`, `insert_after`, `visible`) — to a JSON file outside the repo, and store them:
   ```bash
   levered optimizations web-tag <optimization-id> --set /tmp/levered-web-tag.json
   ```
   Example: `{"bindings": {"headline": {"selector": "h1", "action": "text"}}}`. Optional `paths` limits the pages it runs on; `hide_timeout_ms` (default 1000, max 5000) caps how long the page stays hidden while the variant is applied — on any failure the page shows the original.
3. `levered optimizations web-tag <optimization-id>` prints the install snippet. The user pastes it once into the site's head (in Webflow: Site settings → Custom code). That's the only step that's theirs.

## Previewing

- `?levered_preview=1` on the live page opens the tag's own preview panel to switch variants; it logs nothing. Give the user the link.
- `?levered_variant={"factor":"value",...}` forces one variant without logging — use it for screenshots and for links to share.

## Tracking

The tag sends the **exposure** to the site's own analytics (`dataLayer`, `gtag`, and a `levered:exposure` browser event). It does **not** send rewards. So the reward still needs a path:

- **Connected warehouse:** the site's analytics already lands exposures and conversions there; the reward metric reads them.
- **Managed warehouse:** the conversion has to reach the ingestion API (`/api/v2/ingest/rewards`) with the same anonymous id — usually from the form handler or backend that records the signup. If the site has no backend you can reach, say so plainly: without rewards, the model can't learn.

## Evolving it

On the tag, a new copy, visibility or layout level is a binding change, not a code change: no PR and no deploy. It still needs the user's approval, and it waits for the platform to accept new levels on a live optimization.
