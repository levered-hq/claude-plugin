# Levered Plugin for Claude Code

Create and manage growth optimizations using multi-armed bandits and contextual bandits directly from Claude Code.

## Install

```
/plugin install levered-hq/claude-plugin
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
| `levered` | Automatic | Activates when you mention optimizations, A/B tests, experiments, variants, or bandits. Runs CLI commands and helps with the platform. |
| `optimize` | `/optimize [what to optimize]` | End-to-end workflow. Analyzes your code, creates the optimization, integrates the SDK. |

## Requirements

- A [Levered](https://levered.dev) account
- A connected data warehouse (BigQuery or Snowflake) for reward tracking

The CLI is installed automatically when needed.

## Links

- [Levered](https://levered.dev)
- [SDK](https://www.npmjs.com/package/@levered_dev/sdk)
- [CLI](https://github.com/levered-hq/levered-services/tree/dev/services/levered-cli)
