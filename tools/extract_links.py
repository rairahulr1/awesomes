#!/usr/bin/env python3
"""Extract repository entries from the indexed source READMEs.

One parser per source link format, dispatched from the registry in sources.json.
A format with no parser is an error, never an empty result — per the extraction
spec, a format that silently matches nothing is indistinguishable from a source
having no entries.

    python3 tools/extract_links.py --dry-run     # report only, write nothing
    python3 tools/extract_links.py               # write data/entries.json

Every source declares a *set* of formats: several READMEs mix two.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "sources.json"
OUT = ROOT / "data" / "entries.json"
CACHE = ROOT / ".cache"

# GitHub-hosted paths that are not repositories.
NON_REPO_OWNERS = {
    "user-attachments", "assets", "shields", "topics", "collections", "trending",
    "sponsors", "orgs", "users", "features", "marketplace", "apps", "events",
    "security", "blog", "site", "about", "pricing", "login", "join", "search",
    "settings", "notifications", "explore", "stars", "watchers", "issues", "pulls",
}
NON_REPO_NAMES = {"badge.svg", "shields", "blob", "tree", "raw"}

GH = "https://github.com/"


def owner_repo(url: str) -> tuple[str, str] | None:
    """Canonical owner/repo for a github.com URL, or None if it is not a repo."""
    if not url.lower().startswith(GH):
        return None
    rest = url[len(GH):].split("?")[0].split("#")[0]
    parts = [p for p in rest.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if owner.lower() in NON_REPO_OWNERS or repo.lower() in NON_REPO_NAMES:
        return None
    # Strip only a literal .git suffix. rstrip('.git') would eat the trailing
    # g/i/t of a real repo name — pr-agent -> pr-agen.
    if repo.endswith(".git"):
        repo = repo[: -len(".git")]
    if not owner or not repo:
        return None
    return owner, repo


def clean_desc(text: str) -> str:
    """Trim a captured description tail down to plain text."""
    text = text.strip()
    # Drop leading separators left by the delimiter.
    text = re.sub(r"^[\s\-–—:•]+", "", text)
    # Emphasis markers at the edges only; keep inner markdown intact.
    text = re.sub(r"^(\*\*|__|\*|_)", "", text)
    text = re.sub(r"(\*\*|__|\*|_)$", "", text)
    return text.strip().rstrip(".").strip()


# --------------------------------------------------------------------------
# Format parsers. Each takes (text, source) and yields raw entry dicts.
# --------------------------------------------------------------------------

def parse_bullet_separator(text: str, src: dict):
    """`- [name](url) - description` and `* [name](url) - description`.

    The first link on the line is the entry. Extra links on the same line are
    badge or mirror decorations (Glama scores, docs links) and are ignored.
    """
    line_re = re.compile(
        r"^\s*[-*]\s+\[([^\]]+)\]\((https?://[^\)\s]+)\)(.*)$", re.MULTILINE
    )
    for name, url, tail in line_re.findall(text):
        # A tail that never yields " - words" is decoration, not a description.
        m = re.search(r"\s[-–—]\s+(\S.*)$", tail)
        desc = clean_desc(m.group(1)) if m else ""
        yield {"name": name.strip(), "url": url, "description": desc}


def parse_table_row(text: str, src: dict):
    """`| [name](url) | ... | description |` — first cell links, last cell describes."""
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        link = re.search(r"\[([^\]]+)\]\((https?://[^\)\s]+)\)", cells[0])
        if not link:
            continue
        # Description is the last cell that is prose rather than a badge or link.
        desc = ""
        for cell in reversed(cells[1:]):
            if not cell or cell.startswith("!") or cell.startswith("["):
                continue
            if "http" in cell and "]" not in cell:
                continue
            candidate = clean_desc(re.sub(r"!\[[^\]]*\]\([^)]*\)", "", cell))
            if len(candidate) > 8:
                desc = candidate
                break
        yield {"name": link.group(1).strip(), "url": link.group(2), "description": desc}


def parse_repo_relative(text: str, src: dict):
    """`- [name](path/to/dir/)` resolved against the source repository.

    These are entries that live *inside* the source repo. Resolving them here is
    what makes them visible; unresolved links are reported, never dropped.
    """
    base = f"{GH}{src['owner']}/{src['repo']}"
    line_re = re.compile(
        r"^\s*[-*]\s+\[([^\]]+)\]\((?!https?://|#)([^\)\s]+)\)\s*(.*)$", re.MULTILINE
    )
    for name, path, tail in line_re.findall(text):
        path = path.split("#")[0]
        if not path or path.endswith(".md") or path in ("./", "./"):
            continue
        if path.startswith(("http", "mailto")):
            continue
        if re.match(r"^[\w.-]+\.(png|jpg|jpeg|gif|svg|webp)$", path, re.I):
            continue
        clean = path.strip("./").rstrip("/")
        if not clean:
            continue
        m = re.search(r"\s[-–—:]\s+(\S.*)$", tail)
        yield {
            "name": name.strip(),
            "url": f"{base}/tree/{src['branch']}/{clean}",
            "description": clean_desc(m.group(1)) if m else "",
            "relative": True,
        }


def parse_project_prose(text: str, src: dict):
    """`## [name](url)` followed by a prose block.

    The description is the first prose paragraph after the heading, before any
    <details> block or subheading.
    """
    blocks = re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]
    for block in blocks:
        head = block.split("\n", 1)[0]
        link = re.match(r"\[([^\]]+)\]\((https?://[^\)\s]+)\)", head.strip())
        if not link:
            continue
        body = block.split("\n", 1)[1] if "\n" in block else ""
        # Stop at the first <details>, heading, image, or table.
        prose = re.split(r"<details|^#{1,6}\s|^!\[|^\|", body, flags=re.MULTILINE)[0]
        lines = [
            l.strip() for l in prose.splitlines()
            if l.strip() and not l.strip().startswith(("<!--", "---"))
        ]
        desc = clean_desc(" ".join(lines[:3]))
        yield {"name": link.group(1).strip(), "url": link.group(2), "description": desc}


def parse_html_details(text: str, src: dict):
    """<details><summary><b>name</b> ... <a href="url"> ... <blockquote>desc</blockquote>

    All entries in awesome-opencode's plugin/theme sections are raw HTML, not
    markdown bullets.
    """
    block_re = re.compile(r"<details>\s*<summary>\s*<b>([^<]+)</b>(.*?)</details>", re.S)
    for name, body in block_re.findall(text):
        link = re.search(r'<a href="(https?://[^"]+)"', body)
        if not link:
            continue
        quote = re.search(r"<blockquote>(.*?)</blockquote>", body, re.S)
        desc = ""
        if quote:
            plain = re.sub(r"<[^>]+>", " ", quote.group(1))
            plain = re.sub(r"\s+", " ", plain).strip()
            desc = clean_desc(plain)
        yield {"name": name.strip(), "url": link.group(1), "description": desc}


PARSERS = {
    "table_row": parse_table_row,
    "bullet_separator": parse_bullet_separator,
    "repo_relative": parse_repo_relative,
    "project_prose": parse_project_prose,
    "html_details": parse_html_details,
}


# --------------------------------------------------------------------------


def fetch_readme(src: dict, offline: bool = False) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{src['id']}.md"
    if cached.exists() and cached.stat().st_size > 0:
        return cached.read_text(encoding="utf-8", errors="replace")
    if offline:
        raise FileNotFoundError(f"{src['id']}: not cached and --offline was requested")
    url = f"https://raw.githubusercontent.com/{src['owner']}/{src['repo']}/{src['branch']}/README.md"
    req = urllib.request.Request(url, headers={"User-Agent": "awesomes-extract"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8", "replace")
    cached.write_text(text, encoding="utf-8")
    return text


def previous_counts() -> dict[str, int]:
    if not OUT.exists():
        return {}
    try:
        data = json.loads(OUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {s: n for s, n in data.get("source_counts", {}).items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--offline", action="store_true", help="use cached READMEs only")
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    prev = previous_counts()

    entries: dict[str, dict] = {}
    source_counts: dict[str, int] = {}
    unresolved: list[dict] = []

    for src in registry["sources"]:
        try:
            text = fetch_readme(src, args.offline)
        except Exception as exc:  # noqa: BLE001 — report, do not abort the corpus
            print(f"  ! {src['id']}: could not read README — {exc}", file=sys.stderr)
            source_counts[src["id"]] = 0
            continue

        raw: list[dict] = []
        for fmt in src["formats"]:
            parser = PARSERS.get(fmt)
            if parser is None:
                # Loud, by design. A missing parser must not look like an empty source.
                print(
                    f"  ! {src['id']}: no parser for format '{fmt}' — refusing to "
                    f"treat this source as empty",
                    file=sys.stderr,
                )
                return 2
            try:
                raw.extend(parser(text, src))
            except Exception as exc:  # noqa: BLE001
                print(f"  ! {src['id']}: parser '{fmt}' failed — {exc}", file=sys.stderr)
                return 2

        kept = 0
        for e in raw:
            pair = owner_repo(e["url"])
            if pair is None:
                if e.get("relative"):
                    unresolved.append({"source": src["id"], "link": e["url"]})
                continue
            owner, repo = pair
            if e.get("relative"):
                # A project inside a monorepo is not the same entry as that repository.
                # Key on the full resolved path, or all 119 projects in one source
                # collapse onto a single owner/repo.
                key = e["url"].lower().rstrip("/")
            else:
                key = f"{owner.lower()}/{repo.lower()}"
            if key in entries:
                existing = entries[key]
                if src["id"] not in existing["sources"]:
                    existing["sources"].append(src["id"])
                # Keep the first description; record a conflicting one alongside it.
                if e["description"] and e["description"] != existing.get("description"):
                    existing.setdefault("alt_descriptions", []).append(
                        {"source": src["id"], "text": e["description"]}
                    )
            else:
                entries[key] = {
                    "owner": owner,
                    "repo": repo,
                    "name": e["name"],
                    "url": e["url"],
                    "description": e["description"],
                    "sources": [src["id"]],
                    "in_repo": bool(e.get("relative")),
                    "stars": None,
                    "verified_at": None,
                    "unavailable": False,
                }
                kept += 1
        source_counts[src["id"]] = kept

    # Category attribution: the source's own headings, namespaced. No invented taxonomy.
    print(f"\n{'source':<24} {'entries':>8} {'previous':>9} {'delta':>8}")
    print("-" * 54)
    for sid, n in sorted(source_counts.items(), key=lambda x: -x[1]):
        before = prev.get(sid)
        delta = f"{n - before:+d}" if before is not None else "—"
        flag = ""
        if before is not None and n < before * 0.9:
            flag = "  <-- large drop, check the parser"
        print(f"{sid:<24} {n:>8,} {str(before if before is not None else '—'):>9} {delta:>8}{flag}")
    print("-" * 54)
    multi = sum(1 for e in entries.values() if len(e["sources"]) > 1)
    print(f"unique entries: {len(entries):,}   in >1 source: {multi}   unresolved: {len(unresolved)}")

    if args.dry_run:
        print("\ndry run: nothing written")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_counts": source_counts,
        "unresolved": unresolved,
        "entries": sorted(entries.values(), key=lambda e: e["owner"].lower()),
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())