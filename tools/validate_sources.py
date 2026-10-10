#!/usr/bin/env python3
"""Validate sources.json.

Two failure modes matter, and they fail differently:

  - A malformed source entry is a config error. Reject it loudly at startup.
  - A source declaring a format the parser registry does not implement is a
    coverage gap. Reject it too — per the extraction spec, a format with no
    parser is unimplemented, not empty. Discovering that at run time means a
    source silently contributes nothing.

    python3 tools/validate_sources.py
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "sources.json"

REQUIRED = ("id", "owner", "repo", "branch", "formats")

# Must stay in step with the parser registry in extract_links.py.
KNOWN_FORMATS = {"table_row", "bullet_separator", "repo_relative", "project_prose", "html_details"}

NAME_OK = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._")


def main() -> int:
    errors: list[str] = []

    if not REGISTRY.exists():
        print(f"! {REGISTRY} does not exist", file=sys.stderr)
        return 1

    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    sources = data.get("sources")

    if not isinstance(sources, list) or not sources:
        print("! sources.json has no 'sources' array", file=sys.stderr)
        return 1

    seen_ids: dict[str, int] = {}

    for i, src in enumerate(sources):
        label = src.get("id", f"index {i}") if isinstance(src, dict) else f"index {i}"

        if not isinstance(src, dict):
            errors.append(f"{label}: not an object")
            continue

        for field in REQUIRED:
            if field not in src:
                errors.append(f"{label}: missing required field '{field}'")
        if any(f not in src for f in REQUIRED):
            continue

        for field in ("owner", "repo", "branch", "id"):
            value = src[field]
            if not isinstance(value, str) or not value:
                errors.append(f"{label}: '{field}' must be a non-empty string")
            elif not set(value) <= NAME_OK:
                errors.append(f"{label}: '{field}' has characters outside [A-Za-z0-9-._]: {value!r}")

        if src["id"] in seen_ids:
            errors.append(f"{label}: duplicate id, also at index {seen_ids[src['id']]}")
        else:
            seen_ids[src["id"]] = i

        formats = src["formats"]
        if not isinstance(formats, list) or not formats:
            errors.append(f"{label}: 'formats' must be a non-empty array")
        else:
            unknown = [f for f in formats if f not in KNOWN_FORMATS]
            if unknown:
                errors.append(
                    f"{label}: unimplemented format(s) {unknown}; "
                    f"known formats are {sorted(KNOWN_FORMATS)}"
                )

    # Every source must have a corresponding hand-written page, or the site
    # links to something that does not exist.
    repo_docs = {p.stem for p in (ROOT / "docs" / "repos").glob("*.md")} - {"index"}
    for src in sources:
        if isinstance(src, dict) and src.get("id") and src["id"] not in repo_docs:
            errors.append(f"{src['id']}: no docs/repos/{src['id']}.md page")

    if errors:
        print(f"sources.json is invalid ({len(errors)} problem(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"sources.json is valid — {len(sources)} sources")
    for src in sources:
        print(f"  {src['id']:<24} {src['owner']}/{src['repo']}@{src['branch']}  {','.join(src['formats'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())