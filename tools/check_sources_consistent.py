#!/usr/bin/env python3
"""Assert sources.json and docs/repos/*.md agree about every source.

The registry drives extraction; the entry pages drive the site. If they drift,
extraction reads a different URL than the page advertises, and the "source ↗"
link on the site points somewhere the index never fetched.

    python3 tools/check_sources_consistent.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

URL_RE = re.compile(r"^url:\s*(\S+)", re.MULTILINE)
FORMAT_IN_PAGE_RE = re.compile(r"^formats:\s*\[(.*?)\]", re.MULTILINE)


def main() -> int:
    registry = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    sources = {s["id"]: s for s in registry["sources"]}

    errors: list[str] = []

    page_ids = {p.stem for p in (ROOT / "docs" / "repos").glob("*.md")} - {"index"}
    for missing in sorted(page_ids - set(sources)):
        errors.append(f"docs/repos/{missing}.md exists but is not in sources.json")
    for missing in sorted(set(sources) - page_ids):
        errors.append(f"sources.json declares {missing} but docs/repos/{missing}.md is missing")

    for sid, src in sorted(sources.items()):
        page = ROOT / "docs" / "repos" / f"{sid}.md"
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8")

        m = URL_RE.search(text)
        if not m:
            errors.append(f"{sid}: entry page has no 'url:' in frontmatter")
            continue

        expected = f"https://github.com/{src['owner']}/{src['repo']}"
        if m.group(1) != expected:
            errors.append(f"{sid}: page url {m.group(1)} != registry {expected}")

        # The page states which formats its README uses; keep that honest too.
        fm = FORMAT_IN_PAGE_RE.search(text)
        if fm:
            declared = sorted(x.strip().strip("'\"") for x in fm.group(1).split(",") if x.strip())
            if declared != sorted(src["formats"]):
                errors.append(
                    f"{sid}: page formats {declared} != registry {sorted(src['formats'])}"
                )

    if errors:
        print(f"sources and entry pages disagree ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"sources.json and {len(sources)} entry pages agree on url and formats")
    return 0


if __name__ == "__main__":
    sys.exit(main())