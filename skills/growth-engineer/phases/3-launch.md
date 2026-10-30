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

If there's no warehouse, recommend the **Managed Warehouse** (Levered hosts it; nothing to connect) and, on their yes, turn it on with `levered warehouse use-managed`. If the org has its own warehouse, use it, and settle its exposures table before anything else:

- **Find the id the SDK gets** in the code (what's passed as `anonymousId`: a signed-in user id, a device id, a cookie). That id is the join key and decides the holdout.
- **Read the exposures table** (`levered warehouse status` for its name, `levered warehouse columns <table>`) and `levered warehouse exposure-columns` for what Levered reads. Pick the column that holds the SDK's id, not a similar one: a table often has both a device id and a user id. Set the id, time and variant columns with `levered warehouse exposure-columns --anonymous-id <col> --timestamp <col> --variant <col>` when they differ; say in a line which you chose and why. The table must also have `optimization_id`, and should have `is_holdout`.
- If the app doesn't log exposures yet, they get the columns of [../references/integration-sdk.md](../references/integration-sdk.md).

`levered warehouse exposure-columns` and `levered verify` without `--anonymous-id` need CLI 0.1.16 or later; if the CLI doesn't know them, update it with the install commands in §1.

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

On the org's own warehouse, write the SQL against its tables, with `@start_date` (the `levered-platform` skill has the rules), and return the **same id as the exposures' id column** as `anonymous_id`. If `levered metrics preview <id>` shows real volume, update the time to settle.

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

`dtype` is `str` or `bool`; the first level of each factor is today's experience. It must match what the user approved. Pass what users outside the optimization see (phase 1 §4): nothing for a baseline among the versions; `--control external --holdout <pct>` when the holdout keeps a version that is none of the combinations (check that the holdout branch ignores the returned variant and still logs the exposure); `--control none` when every version is new (no holdout, no health metrics, gain measured against an even split of traffic). `--control` and `--holdout` need CLI 0.1.15 or later; if `create` doesn't know a flag, update the CLI with the install commands in §1. It's created as a **draft**: nothing is served until it goes live.

## 6. Wire it and prove it works

- **SDK:** [../references/integration-sdk.md](../references/integration-sdk.md). Create the key with `levered api-keys create --label <app> --env-file <the gitignored env file the server reads> --url-var <the variable the app reads Levered's address from>`: it writes the key and the matching address, refuses a file git would commit, and never prints the key, so you never open the file. For a forwarding endpoint's secret store, write a gitignored file the same way and load it at deploy time. The key never appears in the chat.
- **Web tag:** [../references/integration-web-tag.md](../references/integration-web-tag.md).

Then test it end to end, in this order (the steps a careful QA person asks about; answer them by doing them):

1. **The id.** Run `levered verify <optimization-id> --json`. It reports how many exposure ids appear in the reward metric and, with an `is_holdout` column, how many holdout rows Levered's hash also puts in the holdout. With representative non-test data, a low share (`warnings` set, `ok: false`) blocks launch: fix the mapping (§2) or metric and recheck. Query errors and failed holdout checks block until fixed, including for QA users. When the sole unresolved condition is missing representative non-test data or reward overlap from intentionally excluded QA rewards, record the aggregate identity check as **pending** and preserve the valid mapping. Check raw event arrival below, and repeat the aggregate check when representative data arrives.
2. **Test users.** Use fresh test ids for this run starting `levered-test-` (or fresh QA accounts), so earlier events cannot satisfy the arrival check. For each, `levered serve <optimization-id> --anonymous-id <id> --dry-run --json` shows the variant and `is_holdout`; it records nothing on Levered's side. When `holdout_percentage` is greater than 0, membership is a fixed hash of the id: try ids until one comes back `is_holdout: true` (about one in ten at 10%) and keep one in and one outside the holdout. When it is 0, including `--control none`, use one ordinary test id; there is no holdout path to test.
3. **Test events.** Send one test exposure and one test reward per test id through the app's existing tracking path: a dry run doesn't stop the app from logging, it only means Levered stores nothing. Mark rewards as test data (`"properties": {"test": true}` on managed).
4. **Arrival.**
   - **Managed Warehouse:** run `levered verify <optimization-id> --anonymous-id <the test id> --json` and require `exposure: true` and `reward: true`. It also runs the aggregate identity check: inspect `identity`, its warnings/errors and `identity.ok` separately; top-level `ok` combines both checks. A false top-level `ok` or exit 1 is pending only when its sole cause is the documented lack of representative non-test data or overlap from intentionally excluded QA rewards. Missing events, query/auth errors, a failed holdout check or identity failures with representative data still block. For arrival-only confirmation, authenticated `GET /api/v2/warehouse/verify?optimization_id=<id>&anonymous_id=<the same test id>` returns the two event booleans without running identity; it does not resolve a pending or failed identity check.
   - **Own warehouse:** read `levered optimizations show <optimization-id> --json` for the linked assignment and reward metric IDs, then fetch their saved SQL and column mappings through authenticated `GET /api/v2/warehouse/metrics/<metric-id>` calls. Derive two read-only checks with `levered warehouse query '<SQL>' --json` against those actual sources and mapped visitor/timestamp columns. Scope the exposure to this optimization, the reward to the chosen goal, and both to the same test visitor and test run; preserve the configured organization and optimization filters. Use the provider's SQL syntax and resolve time parameters from this run. Read raw test rows even when training excludes QA data, relaxing only that deliberate test-data exclusion for the targeted checks. The id and `is_holdout` must match the dry run; timestamps must belong to this run and factors must match the rendered variant (empty factors are allowed for external holdouts). Then repeat aggregate verification if representative non-test data is available.
5. **Test users after launch.** Say in a line that they would count like real users once it's live. Unless the user wants them in, filter their ids out of the reward metric and the exposure source (`PUT /api/v2/warehouse/metrics/<id>`, through `levered warehouse query` first to check the filter), or rely on the managed `properties.test` filter.

Continue only after both raw events arrived for each test user and step 1 is either passed or pending solely for lack of representative non-test data. If a delivery or runnable identity check fails, fix it and repeat it. Report event delivery and aggregate identity separately: a pending aggregate check is not a passed overall verification. Tell the user which warehouse received the events and whether test users are left out of the results; say a test reward is excluded only after confirming the filter.

Commit to the prototype branch; open a pull request if `gh` is available, otherwise say it's on the branch. Tell the user plainly what's theirs: merge, **every secret their hosting needs, by name and where it goes**, and deploy.

## 7. Go live

Going live is worth it once events can reach Levered. Run `levered serve <id> --dry-run --json`, then ask once, as a card: "Go live? Once you deploy the branch, visitors on <surface> will see the <n> versions; <holdout>% keep today's page so we can measure the gain." (with `--control none`, leave out the holdout clause; with `--control external`, say "keep the current version") **[Go live (Recommended)] [Not yet]**. Then `levered optimizations update <id> --status live`, and confirm with `levered optimizations show <id>`. If they can't deploy yet, say it's waiting on their deploy in `.levered/STATUS.md` (step 9).

## 8. Screenshots for the dashboard

Once it's live, capture every variant for the dashboard **in the background** ([../references/screenshots.md](../references/screenshots.md)), and carry on with step 9 while it runs.

## 9. Set up what comes next

1. **Create `.levered/`** ([../references/state.md](../references/state.md)) and commit it with the work.
2. **Trim the permissions back** to the read-only set ([../references/permissions.md](../references/permissions.md)) — unless you didn't write them (auto mode).

## 10. Summarize

Three or four sentences: what's live (name, ID, dashboard link), what's being tried and why, the time to settle, what's theirs to do, and that they can ask how it's going any time. If research or analytics didn't happen and would help, offer it for the wait with **[Run it (Recommended)] [Not now]**. Name Levered's terms once: in the dashboard, what we're changing are *factors* and the options are *levels*.
