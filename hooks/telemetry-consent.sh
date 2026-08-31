#!/usr/bin/env bash
# SessionStart hook — set up the per-session telemetry consent ask.
#
# We only share a session's conversation with Levered when the user explicitly
# opts in, and consent is per session — never remembered across sessions. A
# hook can't talk to the user, so this script just hands Claude the session id
# and the marker-file protocol: Claude asks at the first Levered skill use, and
# a granted consent becomes a marker file that the SessionEnd hook
# (upload-session.sh) checks before uploading anything. No marker, no upload —
# declining is the default and requires no action.
set -uo pipefail

input="$(cat 2>/dev/null || true)"

# Pull session_id out of the hook input JSON (a UUID, so a targeted grep is
# safe and avoids a hard dependency on jq — same trick as check-plugin-version.sh).
session_id="$(printf '%s' "$input" \
  | grep -Eo '"session_id"[[:space:]]*:[[:space:]]*"[^"]+"' \
  | head -1 | grep -Eo '[0-9a-fA-F-]{8,64}' | head -1)"
[ -n "${session_id:-}" ] || exit 0

data_dir="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/levered}"
marker="$data_dir/telemetry-consent/$session_id"

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"Levered telemetry consent: the FIRST time any Levered skill (levered-platform, growth-engineer, growth-analyst) is used this session, BEFORE starting the task, ask the user once, using the AskUserQuestion tool (a single question with two options: Share this session / Do not share; never as free-form prose text), whether they want to share this session Levered usage data with Levered. In the question text explain plainly: if they opt in, the conversation from this session is shared with Levered to improve the quality of the Levered agent and to build better optimizations in the future; only the part of the session from the first Levered skill or CLI use onward is uploaded to the Levered API (during the session and at its end), and nothing is shared without opting in. If the user picks Share this session, record consent by creating the empty file %s with the Write tool. If they decline or do not clearly agree, create nothing, continue with their task, and do not raise it again this session. Ask at most once per session; consent applies to this session only."}}\n' \
  "$marker"
exit 0
