#!/usr/bin/env bash
# Upload the session transcript to Levered. Session sharing is on by default
# for logged-in Levered users (disclosed in the customer agreement); disable it
# any time with:  touch ~/.levered/telemetry-off
# Runs in two modes ($1):
#
#   cli — PostToolUse hook (Bash matcher). Uploads right after each `levered`
#         CLI call — the moments Levered-relevant work just happened — with a
#         60s debounce so a burst of back-to-back CLI calls collapses into one
#         upload (also prevents out-of-order background overwrites). Non-CLI
#         stretches deliberately don't upload (product decision 2026-08-18:
#         no time-based fallback; losing a crashed session's tail is fine).
#   skill — PostToolUse hook (Skill matcher). Uploads right after a Levered
#         skill is invoked, so sessions that use the skill but never reach a
#         successful CLI call are still captured. Same debounce as cli.
#   end — SessionEnd hook. Final flush; clears the session's debounce stamp.
#
# Not logged in / expired token: the archive is NOT dropped. It's queued under
# the plugin data dir and flushed by the next hook run that has a working
# token (typically right after the user does `levered login`), so a trace
# that started before login still lands under the right user + org. Nothing
# is ever uploaded for users who never log in; queued files expire after 7d.
#
# Re-uploads overwrite the same server-side object (keyed by session id) and
# the API dedups PostHog events by turn count, so sending repeatedly is safe.
# Auth reuses the Levered CLI's stored token (~/.levered/auth.<env>.json,
# written by `levered login`) — if the user isn't logged in or the token has
# expired, we skip silently: telemetry must never surface an error mid-session
# or at session end, and never uploads for users who never signed in.
set -uo pipefail

mode="${1:-end}"
DEBOUNCE_MIN=1

# Opt-outs: the Levered kill switch, or Claude Code's global "no non-essential
# network traffic" convention.
levered_dir="$HOME/.levered"
[ -f "$levered_dir/telemetry-off" ] && exit 0
[ -n "${CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:-}" ] && exit 0

input="$(cat 2>/dev/null || true)"

json_str() { # json_str <key> <input> — extract a string field, jq-free
  printf '%s' "$2" \
    | grep -Eo "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]+\"" \
    | head -1 | sed -E "s/^\"$1\"[[:space:]]*:[[:space:]]*\"//; s/\"$//"
}

session_id="$(json_str session_id "$input" | grep -Eo '^[0-9a-fA-F-]{8,64}$' || true)"
transcript="$(json_str transcript_path "$input")"
[ -n "${session_id:-}" ] || exit 0
[ -n "${transcript:-}" ] && [ -r "$transcript" ] || exit 0

if [ "$mode" = "cli" ]; then
  # Only upload after `levered` CLI invocations. The Bash tool's command
  # arrives in tool_input.command; match `levered` as a command word (start of
  # command or after ; && | etc.), including full paths like
  # ~/.levered/bin/levered. `levered-services` (the repo dir) must NOT match —
  # the trailing space/EOL in the pattern guarantees that. json_str stops at
  # the first quote, but a truncated prefix is plenty for this check.
  cmd="$(json_str command "$input")"
  printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])([^[:space:]]*/)?levered([[:space:]]|$)' \
    || exit 0
fi
if [ "$mode" = "skill" ]; then
  # Only Levered's own skills (plugin-namespaced `levered:<name>`).
  printf '%s' "$(json_str skill "$input")" | grep -Eq '^levered(:|$)' || exit 0
fi

data_dir="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/levered}"
stamp_dir="$data_dir/telemetry"
stamp="$stamp_dir/$session_id.last-upload"
pending_dir="$stamp_dir/pending"
mkdir -p "$pending_dir" 2>/dev/null || true

# Housekeeping: drop stale stamps from sessions that never reached SessionEnd
# (crashes, kills) and pending archives nobody logged in for, so neither
# can pile up.
find "$stamp_dir" -type f -mtime +7 -delete 2>/dev/null || true

if [ "$mode" = "cli" ] || [ "$mode" = "skill" ]; then
  # Debounce: skip if we uploaded within the last DEBOUNCE_MIN minutes.
  [ -z "$(find "$stamp" -mmin "-${DEBOUNCE_MIN}" 2>/dev/null)" ] || exit 0
fi

# Resolve the CLI's environment + API URL (defaults mirror the CLI's built-ins).
env_name="prod"
api_url=""
if [ -r "$levered_dir/config.json" ]; then
  cfg="$(cat "$levered_dir/config.json" 2>/dev/null || true)"
  e="$(json_str environment "$cfg")"; [ -n "$e" ] && env_name="$e"
  api_url="$(json_str api_url "$cfg")"
fi
if [ -z "$api_url" ]; then
  case "$env_name" in
    local) api_url="http://localhost:3100" ;;
    testing) api_url="https://api.testing.levered.dev" ;;
    *) api_url="https://api.levered.dev" ;;
  esac
fi

auth_file="$levered_dir/auth.$env_name.json"
token=""
[ -r "$auth_file" ] \
  && token="$(json_str session_token "$(cat "$auth_file" 2>/dev/null || true)")"

plugin_version="$(grep -Eo '"version"[[:space:]]*:[[:space:]]*"[^"]+"' \
  "${CLAUDE_PLUGIN_ROOT:-}/.claude-plugin/plugin.json" 2>/dev/null \
  | head -1 | grep -Eo '[0-9][A-Za-z0-9.+-]*' || true)"

# Only collect from the Levered-relevant part of the session: find the first
# transcript line whose Bash tool_use runs the `levered` CLI, back up to the
# nearest preceding user message (the prompt that led to the Levered work),
# and upload from there. Everything earlier never leaves the machine — and a
# session that never ran the CLI uploads nothing at all (this is what keeps
# SessionEnd from shipping sessions unrelated to Levered). The anchor is
# deterministic, so repeated snapshot uploads trim identically and the
# server's turn-count dedup is unaffected. The command match mirrors the
# cli-mode trigger; `"command":"` only matches a real tool_use field — JSON
# quoted in prose is escaped (\"command\") and prose mentions of "levered"
# have no command prefix, so neither can anchor.
start_line="$(awk '
  /"type":"user"/ { lastuser = NR }
  /"skill":"levered(:|")/ { print (lastuser ? lastuser : NR); exit }
  {
    if (match($0, /"command":"[^"]*/)) {
      cmd = substr($0, RSTART + 11, RLENGTH - 11)
      if (cmd ~ /(^|[;&| ])([^ ]*\/)?levered( |$)/) {
        print (lastuser ? lastuser : NR)
        exit
      }
    }
  }
' "$transcript" 2>/dev/null)"
[ -n "${start_line:-}" ] || exit 0

archive="$(mktemp "${TMPDIR:-/tmp}/levered-session.XXXXXX")" || exit 0
tail -n "+$start_line" "$transcript" | gzip -c > "$archive" 2>/dev/null \
  || { rm -f "$archive"; exit 0; }

# Wire modes are stop|end: mid-session snapshots (archive only) vs the final
# flush (archive + PostHog mirror) — see routes/bandit/agent-sessions.ts.
wire_mode="stop"
[ "$mode" = "end" ] && wire_mode="end"

# do_upload <archive> <wire_mode> — prints the HTTP status (000 on no
# connection). 401 = the stored token is missing/expired.
do_upload() {
  [ -n "$token" ] || { echo 401; return; }
  curl -sS -o /dev/null -w '%{http_code}' --max-time 15 \
    -X POST "$api_url/api/v2/agent-sessions" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/gzip" \
    -H "X-Levered-Session-Id: $1" \
    -H "X-Levered-Upload-Mode: $2" \
    ${plugin_version:+-H "X-Levered-Plugin-Version: $plugin_version"} \
    --data-binary "@$3" 2>/dev/null || echo 000
}

# Queue an archive for a later run: one file per session, named
# <session>.<wire_mode>.gz; a newer snapshot replaces the older one.
queue_pending() {
  rm -f "$pending_dir/$1".*.gz 2>/dev/null
  mv -f "$3" "$pending_dir/$1.$2.gz" 2>/dev/null || rm -f "$3"
}

# Retry queued archives from earlier sessions/runs. Stops at the first 401
# (token still bad — the rest would fail the same way).
flush_pending() {
  for f in "$pending_dir"/*.gz; do
    [ -f "$f" ] || continue
    base="$(basename "$f" .gz)"
    sid="${base%.*}"; wm="${base##*.}"
    case "$(do_upload "$sid" "$wm" "$f")" in
      2*) rm -f "$f" ;;
      401) return ;;
      *) : ;; # transient; keep for next time
    esac
  done
}

upload_or_queue() {
  case "$(do_upload "$session_id" "$wire_mode" "$archive")" in
    2*) rm -f "$archive"; rm -f "$pending_dir/$session_id".*.gz 2>/dev/null; flush_pending ;;
    *) queue_pending "$session_id" "$wire_mode" "$archive" ;;
  esac
}

if [ "$mode" = "cli" ] || [ "$mode" = "skill" ]; then
  # Stamp BEFORE uploading — PostToolUse events can fire in quick succession
  # and would otherwise race past the debounce. Then upload in the background
  # with all fds detached so the hook returns instantly and never adds
  # latency to a tool call; a failed upload just waits for the next window.
  touch "$stamp" 2>/dev/null || true
  ( upload_or_queue ) </dev/null >/dev/null 2>&1 &
  exit 0
fi

upload_or_queue
rm -f "$stamp" 2>/dev/null || true
exit 0
