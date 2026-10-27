# Variant screenshots for the dashboard

Run in the background after go-live (phase 3, step 8). It isn't needed to go live, so it never delays anything.

**Two prerequisites first:**

1. **The dev server is running.** Check it still serves; if it stopped, start it again and wait until it does.
2. **The URL of the optimized page.** Reuse it from the prototype phase or `.levered/state.json` (`surface.url`). Work it out from the routes only if neither has it; ask the user only as a last resort.

The CLI captures a **sample first** and stops, so you can check it before the full run:

```bash
levered optimizations screenshot <optimization-id> --url <dev URL of the optimized page> --device desktop
levered optimizations screenshot <optimization-id> --url <dev URL of the optimized page> --device desktop --yes
```

- **Look at the sample PNGs before `--yes`:** the variants should differ and match their factors.
- **`--device desktop|mobile`** picks a preset viewport; capture `mobile` too when the page has a distinct mobile layout. Add `--selector '<css selector>'` when content loads late and `--full-page` when the change is below the fold.
- It intercepts the SDK's serve call locally, so nothing reaches Levered's serve endpoint and training is untouched; the app's own exposure logging still fires against the dev server, which is expected. Never screenshot variants by calling the real serve endpoint.
- **Act on the failure it reports:** *"SDK likely not installed / initialized"* or *"not applying the served variant props"* → fix the app's wiring yourself and re-run; *"requested these optimization(s) instead"* → the app is wired to a different optimization: ask the user which to capture; *"dev server does not seem to be running"* → start it and re-run.
- If capture still can't succeed, say so in a line and move on: screenshots can be taken any time. If the CLI lacks the `screenshot` subcommand or its flags, ask the user to update the CLI rather than writing a capture script.
