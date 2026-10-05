# Levered Plugin for Claude Code

Create and manage real-time product optimization and personalization directly from Claude Code.

## Install

```
/plugin marketplace add levered-hq/claude-plugin
/plugin install levered@levered
```

## What it does

Tell Claude what you want to optimize and it handles the rest:

- Installs the Levered CLI if needed
- Analyzes your code to determine what to vary
- Creates the optimization on the Levered platform
- Integrates the SDK into your codebase
- Gets you live

## Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `levered-platform` | Automatic | Activates when you mention optimizations, variants, personalization, lift, or conversion. Runs CLI commands and helps with the platform. |
| `growth-engineer` | `/growth-engineer [what to optimize]` | End-to-end workflow. Analyzes your code, creates the optimization, integrates the SDK. |
| `growth-analyst` | `/growth-analyst [optimization or "all"]` | Reads your results. Tells you which variant is winning and why, the lift vs. baseline, which factors matter, and whether to keep running, prune, or ship. |

## Session sharing

When you first sign in to the Levered dashboard, it asks once whether you want
to share your Claude Code sessions with Levered to improve the agent and build
better optimizations. The answer is saved on your account and applies to every
session on every machine — there is no per-session prompt. Nothing is shared
unless you said yes, and `levered login` must have run after that (the choice
travels with your login). Only the part of a conversation from your first
Levered skill or CLI interaction onward is collected — sessions that never
touch Levered send nothing. To stop sharing from one machine regardless of the
account setting:

```
touch ~/.levered/telemetry-off
```

## Requirements

- A [Levered](https://levered.dev) account
- A connected data warehouse (BigQuery or Snowflake) for reward tracking

The CLI is installed automatically when needed.

## Links

- [Levered](https://levered.dev)
- [SDK](https://www.npmjs.com/package/@levered_dev/sdk)
- [CLI](https://github.com/levered-hq/levered-services/tree/dev/services/levered-cli)
