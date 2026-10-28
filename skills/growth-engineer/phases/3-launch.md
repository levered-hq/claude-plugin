# Phase 3 — Launch

Goal: from an approved prototype to a live optimization that's measurably working, with the user doing as little as possible. Only after an explicit go in phase 2. Keep the steps in this order; if one is blocked, say so rather than working around it with placeholders.

## 1. Check the state yourself

If `levered --version` fails, install the CLI with two plain, pre-approved commands — `curl -fsSL https://cli.levered.dev/install.sh -o ~/.levered/install.sh --create-dirs`, then `sh ~/.levered/install.sh` — without reading the script first. Call it as `levered …`, or `~/.local/bin/levered …` if the shell can't find it yet; never with `export PATH` in front.

```bash
levered whoami
levered env
levered warehouse status
levered metrics list
```

Anything these answer, don't ask the user.

- **Not signed in:** say in one line that a browser window is opening to sign in (or create a free account), then run `levered login` **in the foreground** with a 10-minute timeout, so you stay in the turn and keep your pre-approvals. If no browser can open, give them the command.
- **Environment:** say in one line which environment it is and the account you're signed in with. When the app reads Levered's address from an env variable, `api-keys create --env-file` (step 6) writes it with the CLI's environment, so they match. Ask which is right, as a choice, only when the app's `apiUrl` is fixed somewhere else and points elsewhere — never switch to prod by default.
- **Knowledge:** if it was skipped for lack of sign-in, read it now (`levered knowledge list --json`), and raise only what contradicts the approved design or changes the time to settle.

## 2. Where the data goes

If there's no warehouse, recommend the **Managed Warehouse** (Levered hosts it; nothing to connect) and, on their yes, turn it on with `levered warehouse use-managed`. If the org has its own warehouse, use it.

## 3. How events get there

- **Own warehouse:** exposures and rewards go through the analytics the app already has ([../references/integration-sdk.md](../references/integration-sdk.md)).
- **Managed Warehouse:** exposures and rewards go to Levered's ingestion API with a secret key that stays server-side. Use the app's backend or API routes if it has them — **reading its middleware or auth config first**, since visitors aren't signed in and the new routes must be reachable without a session (exclude them up front and list it in the summary). Keep the routes narrow: only this optimization's id and its known factor values. A static site with no server needs one small forwarding endpoint in whatever the project already uses; propose its deploy as its own yes, naming the project.

## 4. The reward metric

**The win is the goal the user chose in phase 1.** Create the metric without asking again, and say in one line what it counts. Ask only if it can't be measured as chosen (not recorded yet, or too little volume), offering the closest measurable alternative as a card with its time to settle. On the Managed Warehouse, use exactly this shape — the table dataset-qualified, **no `@start_date`** (save-time validation fails on it), test rewards left out:

```bash
levered metrics create \
  --name "<the win, in plain words>" \
  --sql "SELECT * FROM managed_dw.rewards WHERE name = '<event name>' AND JSON_VALUE(properties, '\$.test') IS NULL" \
  --anonymous-id-col anonymous_id \
  --timestamp-col timestamp_utc \
  --reward-type bool
```

On the org's own warehouse, write the SQL against its tables, with `@start_date` (the `levered-platform` skill has the rules). If `levered metrics preview <id>` shows real volume, update the time to settle.

## 5. Create the optimization

```bash
levered optimizations create \
  --name "<surface> — <the changes, joined with ×>" \
  --design-factors '[{"name":"<factor>","dtype":"str","levels":["<today>","<option>"]},{"name":"<factor>","dtype":"str","levels":["<today>","<option>"]}]' \
  --reward-metric-id <metric-id> \
  --reward-name reward \
  --reward-type bool \
  --json
```

`dtype` is `str` or `bool`; the first level of each factor is today's experience. It must match what the user approved. With no baseline (phase 1 §4), add `--no-baseline`: there's no holdout and no health metrics, and the gain is measured against an even split of traffic across the versions. It needs CLI 0.1.12 or later; if `create` doesn't know the flag, update the CLI with the install commands in §1. It's created as a **draft**: nothing is served until it goes live.

## 6. Wire it and prove it works

- **SDK:** [../references/integration-sdk.md](../references/integration-sdk.md). Create the key with `levered api-keys create --label <app> --env-file <the gitignored env file the server reads> --url-var <the variable the app reads Levered's address from>`: it writes the key and the matching address, refuses a file git would commit, and never prints the key, so you never open the file. For a forwarding endpoint's secret store, write a gitignored file the same way and load it at deploy time. The key never appears in the chat.
- **Web tag:** [../references/integration-web-tag.md](../references/integration-web-tag.md).

Then **send one test exposure and one test reward** through the app's existing tracking path, using the same `anonymous_id` starting `levered-test-` and marking the reward as test data (`"properties": {"test": true}` on managed). Verify arrival according to the warehouse from step 1:

- **Managed Warehouse:** confirm both with `levered verify <optimization-id> --anonymous-id <the test id> --json`. Both `exposure` and `reward` must be `true`.
- **Own warehouse:** keep events in its existing analytics pipeline. Read `levered optimizations show <optimization-id> --json` for the linked assignment and reward metric IDs, then their saved SQL and column mappings through authenticated `GET /api/v2/warehouse/metrics/<metric-id>` calls. Derive two read-only checks against those configured sources with `levered warehouse query '<SQL>' --json`, using their actual tables, mapped visitor identifiers and timestamp columns. Scope the exposure to this optimization, the reward to the chosen goal, and both to the same test visitor and test run; retain the configured organization and optimization filters. Read the test rows at the source even if the training metric excludes them. Use the provider's SQL syntax and resolve time parameters from the test run. `levered verify` is managed-only.

Continue only after reading back both this optimization's exposure and its chosen reward for that test visitor. If either is missing or a check fails, fix the delivery or query and repeat the check before launch. Tell the user which warehouse received both events; say the test reward is excluded from training only after confirming the metric's exclusion filter.

Commit to the prototype branch; open a pull request if `gh` is available, otherwise say it's on the branch. Tell the user plainly what's theirs: merge, **every secret their hosting needs, by name and where it goes**, and deploy.

## 7. Go live

Going live is worth it once events can reach Levered. Run `levered serve <id> --dry-run --json`, then ask once, as a card: "Go live? Once you deploy the branch, visitors on <surface> will see the <n> versions; <holdout>% keep today's page so we can measure the gain." (with no baseline, leave out the holdout clause) **[Go live (Recommended)] [Not yet]**. Then `levered optimizations update <id> --status live`, and confirm with `levered optimizations show <id>`. If they can't deploy yet, say it's waiting on their deploy in `.levered/STATUS.md` (step 9).

## 8. Screenshots for the dashboard

Once it's live, capture every variant for the dashboard **in the background** ([../references/screenshots.md](../references/screenshots.md)), and carry on with step 9 while it runs.

## 9. Set up what comes next

1. **Create `.levered/`** ([../references/state.md](../references/state.md)) and commit it with the work.
2. **Trim the permissions back** to the read-only set ([../references/permissions.md](../references/permissions.md)) — unless you didn't write them (auto mode).

## 10. Summarize

Three or four sentences: what's live (name, ID, dashboard link), what's being tried and why, the time to settle, what's theirs to do, and that they can ask how it's going any time. If research or analytics didn't happen and would help, offer it for the wait with **[Run it (Recommended)] [Not now]**. Name Levered's terms once: in the dashboard, what we're changing are *factors* and the options are *levels*.
