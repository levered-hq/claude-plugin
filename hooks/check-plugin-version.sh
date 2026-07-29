#!/usr/bin/env bash
# SessionStart hook — nudge the user when a newer Levered plugin is published.
#
# Why a hook and not the skills: skills can't self-trigger and their allowed-tools
# don't permit curl, so a per-skill check would prompt on every run. A SessionStart
# hook runs once per session, has network access, sees ${CLAUDE_PLUGIN_ROOT}, and
# costs zero model tokens. It only speaks up when there's actually a newer version
# — silent when current or offline, and never blocks the session (always exit 0).
#
# The "latest" version is read from the public marketplace repo that the
# sync-claude-plugin workflow mirrors this plugin into, so it's the same source of
# truth users install from. NOTE: this only fires when the plugin `version` is
# bumped per release — unchanged version means installed == latest == no nudge.
set -uo pipefail

LATEST_URL="https://raw.githubusercontent.com/levered-hq/claude-plugin/main/.claude-plugin/plugin.json"
CACHE_TTL_MIN=360 # re-check GitHub at most every 6h; stay fast + offline-friendly

# Pull the semver out of a plugin.json (our own file, so a targeted grep is safe
# and avoids a hard dependency on jq).
version_of() {
  grep -Eo '"version"[[:space:]]*:[[:space:]]*"[^"]+"' "$1" 2>/dev/null \
    | head -1 | grep -Eo '[0-9][A-Za-z0-9.+-]*'
}

plugin_json="${CLAUDE_PLUGIN_ROOT:-}/.claude-plugin/plugin.json"
[ -f "$plugin_json" ] || exit 0
installed="$(version_of "$plugin_json")"
[ -n "$installed" ] || exit 0

data_dir="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/levered}"
mkdir -p "$data_dir" 2>/dev/null || true
cache="$data_dir/latest-plugin.json"

# Refresh the cached "latest" at most once per TTL window.
if [ -z "$(find "$cache" -mmin "-${CACHE_TTL_MIN}" 2>/dev/null)" ]; then
  if curl -fsS --max-time 3 "$LATEST_URL" -o "$cache.tmp" 2>/dev/null; then
    mv "$cache.tmp" "$cache" 2>/dev/null || rm -f "$cache.tmp" 2>/dev/null
  else
    rm -f "$cache.tmp" 2>/dev/null
  fi
fi
[ -f "$cache" ] || exit 0

latest="$(version_of "$cache")"
[ -n "$latest" ] || exit 0

# Only nudge when `latest` is strictly newer than `installed` (semver-aware via
# `sort -V`), so a local/dev build ahead of the public repo stays quiet.
newest="$(printf '%s\n%s\n' "$installed" "$latest" | sort -V | tail -1)"
if [ "$installed" != "$latest" ] && [ "$newest" = "$latest" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"A newer Levered plugin is available (installed %s, latest %s). The first time the user uses any Levered skill this session, BEFORE starting their task, tell them a newer version is available and ask whether to update first. If they agree, have them run: /plugin marketplace update levered , then /plugin update levered@levered , then /reload-plugins . Ask once — if they decline, continue with the task and do not raise it again this session."}}\n' \
    "$installed" "$latest"
fi
exit 0
