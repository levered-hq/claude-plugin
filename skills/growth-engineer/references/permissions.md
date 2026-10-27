# Permissions that last

The skill's pre-approvals hold only in turns the skill started; any other turn prompts again. So outside auto mode, the flow's rules go into the project's `.claude/settings.local.json`: the user's own file, never committed.

## When the user says build (or picks research)

**In auto mode, skip this file.** Commands already run without prompts there, and auto mode refuses an agent editing its own permissions. Say nothing about permissions, and there's nothing to trim after launch.

Otherwise, right after the skill is entered and before the first command, write the rules — one approval, because Claude Code asks before any change to its settings. Say it in one line first: what you're allowing and why (fewer prompts during the build), that it's only theirs, in `.claude/settings.local.json`, and that you'll trim it back once live.

If the file exists, read it and add these rules to its `allow` list; never remove the user's own. Then make sure `.claude/settings.local.json` is in the project's `.gitignore` (add the line if it isn't).

```json
{
  "permissions": {
    "allow": [
      "Bash(levered:*)",
      "Bash(~/.local/bin/levered:*)",
      "Bash(curl -fsSL https://cli.levered.dev/install.sh:*)",
      "Bash(sh ~/.levered/install.sh)",
      "Bash(npm:*)",
      "Bash(npx:*)",
      "Bash(yarn:*)",
      "Bash(pnpm:*)",
      "Bash(git:*)",
      "Bash(gh pr:*)",
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(grep:*)",
      "Bash(curl -s http://localhost:*/*)",
      "Bash(curl -s -X POST http://localhost:*/*)",
      "Bash(open http://localhost:*/*)",
      "Edit(./**)",
      "Write(./**)"
    ]
  }
}
```

The syntax is precise (tested): a trailing `:*` means "this command, then anything", so `Bash(git:*)` covers any `git` command. The local rules end in `:*/*`, which matches any port and path on localhost and nothing else. `Edit(./**)` and `Write(./**)` stay inside the project; anything outside it, and any command not listed, still asks.

Web search and fetch stay out: they're only needed while researching, inside the skill.

## Once launch is done — trim it back

These rules are broad (any `npx`, any `git`, any `levered` command), so they don't outlive the build. At the end of phase 3, replace the flow's rules with read-only ones — read results, record what you found — and nothing that changes what visitors see:

```json
{
  "permissions": {
    "allow": [
      "Bash(levered optimizations list:*)",
      "Bash(levered optimizations show:*)",
      "Bash(levered optimizations progress:*)",
      "Bash(levered optimizations results:*)",
      "Bash(levered optimizations guardrails:*)",
      "Bash(levered optimizations lift-history:*)",
      "Bash(levered optimizations report-data:*)",
      "Bash(levered knowledge list:*)",
      "Bash(levered whoami:*)",
      "Bash(~/.local/bin/levered optimizations list:*)",
      "Bash(~/.local/bin/levered optimizations show:*)",
      "Bash(~/.local/bin/levered optimizations progress:*)",
      "Bash(~/.local/bin/levered optimizations results:*)",
      "Bash(~/.local/bin/levered optimizations guardrails:*)",
      "Bash(~/.local/bin/levered optimizations lift-history:*)",
      "Bash(~/.local/bin/levered optimizations report-data:*)",
      "Bash(~/.local/bin/levered knowledge list:*)",
      "Bash(~/.local/bin/levered whoami:*)",
      "Read(.levered/**)",
      "Edit(.levered/**)",
      "Write(.levered/**)"
    ]
  }
}
```

Again keep any rules that were the user's own. When a later session needs the build rules again, add them back the same way, with the same one-line explanation, and trim again after.

If the user says no, carry on: commands prompt as usual. Don't ask twice in a session.
