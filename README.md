# Levered Plugin for Claude Code

Create and manage real-time product optimization and personalization directly from Claude Code.

## Install

```
/plugin marketplace add levered-hq/claude-plugin
/plugin install levered@levered
```

## What it does

Your AI growth engineer. Ask it to improve your product — or just run `/growth-engineer` — and it leads:

- Finds where your product loses conversions, from your code, your live pages and your analytics
- Proposes what to change, sized to your traffic, and prototypes it in your app so you can click through every variant
- Launches it on Levered (SDK, or the hosted web tag for pages outside your repo) and confirms it's working

It keeps its memory in a `.levered/` folder in your repository, so any session picks up where the last one left off.

## Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `levered-platform` | Automatic | Activates when you mention optimizations, variants, personalization, lift, or conversion. Runs CLI commands and helps with the platform. |
| `growth-engineer` | `/growth-engineer [what to optimize]` | Your growth engineer, end to end: finds what to optimize, prototypes it in your app, and launches it. |
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
