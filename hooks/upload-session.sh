#!/usr/bin/env bash
# Upload the session transcript to Levered, if (and only if) the user opted in
# this session. Runs in two modes ($1):
#
#   stop — Stop hook, after each assistant response. Re-uploads the transcript
#          at most every 30 minutes, so long sessions are captured while the
#          CLI token (24h) is still fresh and a crash loses only the tail.
#   end  — SessionEnd hook. Final flush; consumes the consent marker so a
#          session can never upload after it ended and consent never outlives
#          the session.
#
# Re-uploads overwrite the same server-side object (keyed by session id) and
# the API dedups PostHog events by turn count, so sending repeatedly is safe.
# Consent is a per-session marker file written by Claude when the user says
# yes (see telemetry-consent.sh). Auth reuses the Levered CLI's stored token
# (~/.levered/auth.<env>.json, written by `levered login`) — if the user isn't
# logged in or the token has expired, we skip silently: telemetry must never
# surface an error mid-session or at session end.
set -uo pipefail

mode="${1:-end}"
THROTTLE_MIN=30

input="$(cat 2>/dev/null || true)"

json_str() { # json_str <key> <input> — extract a string field, jq-free
  printf '%s' "$2" \
    | grep -Eo "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]+\"" \
    | head -1 | sed -E "s/^\"$1\"[[:space:]]*:[[:space:]]*\"//; s/\"$//"
}

session_id="$(json_str session_id "$input" | grep -Eo '^[0-9a-fA-F-]{8,64}$' || true)"
transcript="$(json_str transcript_path "$input")"
[ -n "${session_id:-}" ] || exit 0

data_dir="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/levered}"
consent_dir="$data_dir/telemetry-consent"
marker="$consent_dir/$session_id"
stamp="$consent_dir/$session_id.last-upload"

# Housekeeping: drop stale markers/stamps from sessions that never reached
# SessionEnd (crashes, kills) so consent files can't pile up.
find "$consent_dir" -type f -mtime +7 -delete 2>/dev/null || true

[ -f "$marker" ] || exit 0

if [ "$mode" = "stop" ]; then
  # Throttle: skip if we uploaded within the last THROTTLE_MIN minutes.
  [ -z "$(find "$stamp" -mmin "-${THROTTLE_MIN}" 2>/dev/null)" ] || exit 0
else
  rm -f "$marker" 2>/dev/null || true
fi

[ -n "${transcript:-}" ] && [ -r "$transcript" ] || exit 0

# Resolve the CLI's environment + API URL (defaults mirror the CLI's built-ins).
levered_dir="$HOME/.levered"
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
[ -r "$auth_file" ] || exit 0
token="$(json_str session_token "$(cat "$auth_file" 2>/dev/null || true)")"
[ -n "$token" ] || exit 0

plugin_version="$(grep -Eo '"version"[[:space:]]*:[[:space:]]*"[^"]+"' \
  "${CLAUDE_PLUGIN_ROOT:-}/.claude-plugin/plugin.json" 2>/dev/null \
  | head -1 | grep -Eo '[0-9][A-Za-z0-9.+-]*' || true)"

archive="$(mktemp "${TMPDIR:-/tmp}/levered-session.XXXXXX")" || exit 0
trap 'rm -f "$archive"' EXIT
gzip -c "$transcript" > "$archive" 2>/dev/null || exit 0

if curl -fsS --max-time 15 -X POST "$api_url/api/v2/agent-sessions" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/gzip" \
  -H "X-Levered-Session-Id: $session_id" \
  -H "X-Levered-Upload-Mode: $mode" \
  ${plugin_version:+-H "X-Levered-Plugin-Version: $plugin_version"} \
  --data-binary "@$archive" >/dev/null 2>&1; then
  [ "$mode" = "stop" ] && touch "$stamp" 2>/dev/null
fi
[ "$mode" = "end" ] && rm -f "$stamp" 2>/dev/null

exit 0
