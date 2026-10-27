# The `.levered/` folder

What the growth engineer remembers between sessions. It lives in the user's repository so any session reads the same thing, and the team can review it like code. Create it in phase 3 (or earlier if there's something worth keeping). Read it first in every session.

| File | Who writes it | Purpose |
|---|---|---|
| `brief.md` | You draft it, the user owns it | Goals, reward, surfaces in scope, things never to touch, claims that need sign-off, and an **Ideas** section where the user adds ideas and hypotheses at any time |
| `state.json` | You | Machine state, schema below. Rewrite it at the end of every session that changed anything |
| `STATUS.md` | You | The same state in five lines a human reads in ten seconds: what's running, what's waiting on whom, what happens next |
| `learnings.md` | You propose, the user curates | **Why** things work on this product — mechanisms, not winners. Format below. Read before every design |
| `changes/<n>.md` | You | One per change actually applied (optimization created, levels added): hypothesis, what changed, source of each level (`user` / `research` / `agent`), primary metric, guardrail, when it matures, verdict once it has |
| `research/` | You (`references/quick-research.md`), or the growth-researcher skill | `brief.md` from quick research; deeper research documents and the hypotheses backlog when growth-researcher has run |

## `learnings.md`: mechanisms, not winners

Which version led doesn't help the next design. *Why* it led does: a mechanism carries to new levels and new pages; a winner doesn't. So each entry is a belief about what moves this product's visitors, with its evidence and how far it has been confirmed:

```markdown
## <The mechanism, as a short claim about visitors>
- **Status:** candidate | validated | retired
- **Mechanism:** <who hesitates or acts, and why>
- **Evidence:**
  - <month> <surface> — <which option led its factor>; <lift> vs. the holdout (change <n>)
  - <further results that confirm or contradict it>
- **Doesn't hold for:** <segments where it made no difference, if any>
- **Source:** <agent | user | research> (from change <n>)
```

- **candidate** — inferred from one optimization's results. Worth testing again, not yet worth building on alone.
- **validated** — held again in a **different form**: other wording, another lever, another page. Build new designs on these first.
- **retired** — a later test contradicted it. Keep the entry with the contradicting evidence; don't delete it.

Also record what the user tells you they tried before, as candidates with their evidence. Keep entries short and in plain language — the user curates this file, and it's the product's growth knowledge, not a log.

Never write secrets here (API keys, webhook URLs): those go in the env file the app already uses, and `.levered/` gets committed.

## `state.json`

```json
{
  "version": 1,
  "phase": "live",
  "updated_at": "2026-10-16T09:00:00Z",
  "optimizations": [
    {
      "id": "<optimization id>",
      "name": "<name>",
      "surface": { "route": "<route>", "url": "<dev server URL of the page>", "files": ["<files the change touches>"] },
      "method": "sdk",
      "reward": { "name": "<event name>", "metric_id": "<metric id>" },
      "status": "live",
      "went_live_at": "2026-10-16T08:40:00Z",
      "estimate": { "weekly_reward_events": null, "source": "assumed", "settle_weeks": [2, 4] }
    }
  ]
}
```

- `phase`: `start` | `first-look` | `prototype` | `launch` | `live` (older files may say `first-value`, the same phase). It tells the router where to resume.

## Resuming

At the start of every session, if `.levered/state.json` exists: read it and `STATUS.md`, and re-check the live facts with the CLI (status can change outside your sessions — someone may have shipped or paused from the dashboard). If the user asked for something specific, do that, with the state in mind. Otherwise say in one or two lines where things stand and what you propose next. Don't replay history.
