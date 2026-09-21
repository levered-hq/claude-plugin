#!/usr/bin/env python3
"""Fetch two variant snapshots from the Levered platform and emit the report's
side-by-side embed block (base64 data URIs, self-contained markdown).

Usage:
    python3 embed_snapshots.py <optimization-id> \
        --winner 9 --winner-caption "Winner, variant 9: ..." \
        --original 1 --original-caption "Original, variant 1: ..." \
        [--cache-dir ~/.levered/reports/<id>/snapshots] [--env prod] \
        [--out snippet.md]

Auth: the CLI's session token from ~/.levered/auth.<env>.json. A 401 means the
token expired — ask the user to run `levered login` and retry; do not probe
other header shapes. Fetched PNGs are cached in --cache-dir and reused, so a
report refresh does not re-download unchanged snapshots (pass --force to
re-fetch, e.g. after the winner changed).
"""

import argparse
import base64
import json
import pathlib
import sys
import urllib.request

API = {"prod": "https://api.levered.dev", "testing": "https://api.testing.levered.dev"}


def fetch(opt_id, number, token, env, cache_dir, force):
    cache = cache_dir / f"variant{number}.png"
    if cache.exists() and not force:
        return cache.read_bytes(), "cache"
    url = f"{API[env]}/api/v2/optimizations/{opt_id}/variants/by-number/{number}/screenshot"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as r:
        data = r.read()
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(data)
    return data, "fetched"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("optimization_id")
    ap.add_argument("--winner", type=int, required=True)
    ap.add_argument("--winner-caption", required=True)
    ap.add_argument("--original", type=int, default=1)
    ap.add_argument("--original-caption", required=True)
    ap.add_argument("--env", default="prod", choices=sorted(API))
    ap.add_argument("--cache-dir")
    ap.add_argument("--out", help="Write the snippet here instead of stdout.")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    auth_path = pathlib.Path.home() / f".levered/auth.{args.env}.json"
    try:
        token = json.load(open(auth_path))["session_token"]
    except (OSError, KeyError, json.JSONDecodeError):
        sys.exit(f"No usable session token at {auth_path} — run `levered login` first.")

    cache_dir = pathlib.Path(
        args.cache_dir or pathlib.Path.home() / f".levered/reports/{args.optimization_id}/snapshots"
    ).expanduser()

    try:
        win, win_src = fetch(args.optimization_id, args.winner, token, args.env, cache_dir, args.force)
        orig, orig_src = fetch(args.optimization_id, args.original, token, args.env, cache_dir, args.force)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit("401 from the platform — the session token expired. Ask the user to run `levered login`, then retry.")
        sys.exit(f"Snapshot fetch failed: HTTP {e.code} for variant endpoint ({e.url}). A 404 means no snapshot was uploaded for that variant.")

    b_win = base64.b64encode(win).decode()
    b_orig = base64.b64encode(orig).decode()
    snippet = (
        "**Variant snapshots** (as served in the app):\n\n"
        f"| *{args.winner_caption}* | *{args.original_caption}* |\n"
        "|---|---|\n"
        f"| ![Variant {args.winner}, winner](data:image/png;base64,{b_win}) "
        f"| ![Variant {args.original}, original](data:image/png;base64,{b_orig}) |\n"
    )
    if args.out:
        pathlib.Path(args.out).write_text(snippet)
        print(f"snippet written to {args.out} (winner: {win_src}, original: {orig_src}; {len(snippet)} bytes)")
    else:
        print(snippet)


if __name__ == "__main__":
    main()
