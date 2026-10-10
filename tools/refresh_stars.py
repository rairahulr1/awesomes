#!/usr/bin/env python3
"""Refresh the `stars` and `stars_as_of` fields on the ten index entry pages.

Scope: this is the *list-level* refresher — 10 API calls, one per indexed awesome
list. It is deliberately NOT the entry-level enrichment described by the
`entry-metadata` capability in AI-memory's openspec (`repo-entry-index`), which
covers ~5,186 repository entries and needs a resumable, checkpointed design. Don't
conflate the two.

Star counts rot. This reads the canonical owner/repo out of each entry's frontmatter,
asks the GitHub REST API for the current figure, and rewrites the two fields in place.

    python3 tools/refresh_stars.py --dry-run    # report, write nothing
    python3 tools/refresh_stars.py              # apply

Set GITHUB_TOKEN to lift the API ceiling from 60/hr unauthenticated to 5000/hr.

Exits 0 and prints "no changes" when nothing moved, so a scheduled run that finds
nothing to do produces no commit.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

REPO_DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs" / "repos"
API = "https://api.github.com/repos/{owner}/{repo}"
SOURCE = "github-rest-api"

# owner/repo from the frontmatter url field. Anchored per line — without re.MULTILINE the ^ only
# matches the very start of the file, which is the frontmatter fence, so nothing matches at all.
URL_RE = re.compile(
    r"^url:\s*https?://(?:www\.)?github\.com/([^/#?\s]+)/([^/#?\s]+)", re.MULTILINE
)


def fetch_stars(owner: str, repo: str, token: str | None, timeout: int = 20) -> int | None:
    req = urllib.request.Request(
        API.format(owner=owner, repo=repo),
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "awesomes-star-refresh",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        print(f"  ! {owner}/{repo}: HTTP {exc.code} {exc.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as exc:
        print(f"  ! {owner}/{repo}: {exc.reason}", file=sys.stderr)
        return None

    count = payload.get("stargazers_count")
    if not isinstance(count, int):
        print(f"  ! {owner}/{repo}: no stargazers_count in response", file=sys.stderr)
        return None
    return count


def replace_field(text: str, key: str, value: str) -> tuple[str, bool]:
    """Replace a scalar frontmatter field in place. Returns (text, changed)."""
    pattern = re.compile(rf"^({re.escape(key)}:)(.*)$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return text, False
    if match.group(2).strip() == value:
        return text, False
    return pattern.sub(lambda m: f"{m.group(1)} {value}", text, count=1), True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or None
    today = date.today().isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    changed_files: list[pathlib.Path] = []
    failures = 0

    for path in sorted(REPO_DOCS.glob("*.md")):
        if path.name == "index.md":
            continue

        text = original = path.read_text(encoding="utf-8")

        url_match = URL_RE.search(text)
        if not url_match:
            # Not a skip: an entry with no resolvable source URL is a data error, and counting it
            # as "nothing to do" is how a broken run reports success.
            print(f"  ! {path.name}: no github.com URL in frontmatter", file=sys.stderr)
            failures += 1
            continue
        owner, repo = url_match.group(1), url_match.group(2)

        stars = fetch_stars(owner, repo, token)
        if stars is None:
            failures += 1
            continue

        text, c1 = replace_field(text, "stars", str(stars))
        text, c2 = replace_field(text, "stars_as_of", today)
        text, c3 = replace_field(text, "stars_source", SOURCE)

        if not (c1 or c2 or c3):
            print(f"    {path.name}: unchanged at {stars:,}")
            continue

        deltas = []
        if c1:
            old = re.search(r"^stars: *(\d+)", original, re.MULTILINE)
            if old:
                deltas.append(f"{int(old.group(1)):,} -> {stars:,}")
        detail = f" ({', '.join(deltas)})" if deltas else ""

        print(f"    {path.name}: updated{detail}, as-of {today}")
        changed_files.append(path)

        if not args.dry_run:
            path.write_text(text, encoding="utf-8")

    print(f"\n[{stamp}] {len(changed_files)} file(s) {'would change' if args.dry_run else 'changed'}"
          f"{f', {failures} lookup(s) failed' if failures else ''}")

    if args.dry_run and changed_files:
        print("dry run: nothing written")

    # Signal to CI whether a commit is warranted.
    print("CHANGED=1" if changed_files else "CHANGED=0")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())