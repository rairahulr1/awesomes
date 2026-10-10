#!/usr/bin/env python3
"""Enrich the 5,583 repository entries in data/entries.json with stars and provenance.

Scope: this is the *entry-level* refresher — one lookup per distinct repository,
checkpointed per source so it survives the rate ceiling. It is deliberately NOT
tools/refresh_stars.py, which refreshes the ten list-level entry pages in ten API
calls. Don't conflate the two.

Four fields are added per entry, and they mean different things:

    stars             stargazers_count as reported by the REST API, or null
    verified_at       the date *this tool* last confirmed the link (a positive fetch)
    source_updated_at the upstream repository's own pushed_at date
    stars_source      "github-rest-api", so the figure's provenance is explicit

verified_at is about our observation; source_updated_at is about the repository.
Neither is derived from the other — a repo pushed last week and confirmed today
records both, and they must never be substituted for one another.

Failure policy — a failed lookup may never cost an entry data it already had:

    404 / 451     unavailable: true. `stars` is left exactly as it was. Never 0,
                  never "", never decremented. A repository that comes back is
                  refetched and revived.
    5xx, timeout, connection error
                  entry left completely untouched and retried on the next run of
                  that source. Stale data beats missing data; missing data beats
                  wrong data.
    403 / 429     Retry-After honoured, then exponential backoff. A hard stop
                  aborts the source rather than grinding through 5,000 doomed
                  requests — the checkpoint is not written, so the rerun resumes.

Entries with in_repo=True are paths *inside* a source repository rather than
repositories of their own; their owner/repo is the list's. Looking those up would
stamp one repository's star count onto every subdirectory, so they are skipped
and counted in the report.

Requires GITHUB_TOKEN. Unauthenticated is 60 req/hr and this corpus would take 86
hours; without a token this exits 2 rather than starting.

    python3 tools/enrich_stars.py --dry-run                    # report, write nothing
    python3 tools/enrich_stars.py --source awesome-php         # one source
    python3 tools/enrich_stars.py                              # all sources
    python3 tools/enrich_stars.py --offline                    # no network at all
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "entries.json"
CKPT_DIR = ROOT / "data" / "enrichment"

STARS_SOURCE = "github-rest-api"

# GitHub Enterprise override. Also the seam used to exercise the failure paths
# against a stub server, since a real 404/500 cannot be provoked on demand.
API_BASE = os.environ.get("GITHUB_API_BASE", "https://api.github.com").rstrip("/")

# 0.8s/request is ~4,500/hr, under the 5,000/hr authenticated ceiling with
# headroom for the secondary (abuse) limit. Raise it on 403/429; never lower it.
DEFAULT_DELAY = 0.8

# Outcome of one lookup.
OK = "ok"                # a positive fetch; stars may be written
GONE = "gone"            # 404/451 — permanently unavailable, keep prior stars
TRANSIENT = "transient"  # 5xx/timeout/connection — entry left untouched, retried
THROTTLED = "throttled"  # 403/429 with retries exhausted — source aborts


class RateLimitHit(Exception):
    """A limit that cannot be waited out in this run. The source is left resumable."""


@dataclass
class Rate:
    """X-RateLimit-* as reported on the last response."""

    remaining: int | None = None
    reset_at: float | None = None

    @classmethod
    def from_headers(cls, headers) -> "Rate":
        def num(name: str) -> float | None:
            try:
                return float(headers[name])
            except (KeyError, TypeError, ValueError):
                return None

        # Read as a float, not `int(x or -1) or None`: a remaining count of 0 is
        # the single most interesting value and must survive as 0, not become None.
        remaining = num("X-RateLimit-Remaining")
        return cls(remaining=None if remaining is None else int(remaining),
                   reset_at=num("X-RateLimit-Reset"))


@dataclass
class Lookup:
    status: str
    stars: int | None = None
    pushed_at: str | None = None
    rate: Rate | None = None
    detail: str = ""


# --------------------------------------------------------------------------
# HTTP


def retry_after(headers) -> float | None:
    """Seconds to wait, from a Retry-After header given as seconds or a date."""
    raw = (headers.get("Retry-After") if headers else None) or ""
    raw = raw.strip()
    if not raw:
        return None
    try:
        return max(0.0, float(raw))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, when.timestamp() - time.time())


def fetch_repo(
    owner: str,
    repo: str,
    token: str,
    *,
    timeout: int,
    max_retries: int,
    backoff: float = 2.0,
    max_backoff: float = 60.0,
) -> Lookup:
    """GET /repos/{owner}/{repo}, retrying transient failures with backoff.

    Returns a Lookup describing the outcome. Never raises for an expected HTTP
    condition; a THROTTLED result is the caller's cue to abort the source.
    """
    url = f"{API_BASE}/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "awesomes-enrich-stars",
        "Authorization": f"Bearer {token}",
    }
    wait = backoff
    detail = ""

    for attempt in range(max_retries + 1):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.load(resp)
                rate = Rate.from_headers(resp.headers)
        except urllib.error.HTTPError as exc:  # noqa: PERF203 — retry loop
            code = exc.code
            if code in (403, 429):
                if attempt == max_retries:
                    return Lookup(THROTTLED, detail=f"HTTP {code} after {attempt} retries")
                pause = retry_after(exc.headers)
                pause = max(pause, wait) if pause is not None else wait
                print(f"  ! {owner}/{repo}: HTTP {code} — sleeping {pause:.0f}s", file=sys.stderr)
                time.sleep(pause)
                wait = min(wait * 2, max_backoff)
                continue
            if code in (404, 451):
                return Lookup(GONE, detail=f"HTTP {code} {exc.reason}")
            detail = f"HTTP {code} {exc.reason}"
            if code < 500:
                # 4xx other than rate limiting will not fix itself.
                return Lookup(TRANSIENT, detail=detail)
        except urllib.error.URLError as exc:
            detail = f"{exc.reason}"
        except (TimeoutError, json.JSONDecodeError, ValueError) as exc:
            detail = f"{type(exc).__name__}: {exc}"
        else:
            # Success. Everything below this point is retry-on-failure, so a
            # missing return here silently reports every good lookup as failed
            # and enriches nothing.
            stars = payload.get("stargazers_count")
            if not isinstance(stars, int):
                return Lookup(TRANSIENT, detail="no stargazers_count in response")
            return Lookup(OK, stars=stars, pushed_at=payload.get("pushed_at"), rate=rate)

        if attempt == max_retries:
            break
        time.sleep(wait)
        wait = min(wait * 2, max_backoff)

    return Lookup(TRANSIENT, detail=detail or f"failed after {max_retries} retries")


class RateGate:
    """Pauses before the hourly budget runs out instead of collecting 403s.

    Reacting to 403s alone means the last `low_water` requests of every hour are
    wasted on errors that the response headers had already predicted.
    """

    def __init__(self, low_water: int = 50, max_wait: float = 300.0) -> None:
        self.low_water = low_water
        self.max_wait = max_wait

    def hold(self, rate: Rate | None) -> None:
        if rate is None or rate.remaining is None or rate.remaining > self.low_water:
            return
        if rate.reset_at is None:
            return
        pause = rate.reset_at - time.time()
        if pause > self.max_wait:
            raise RateLimitHit(
                f"{rate.remaining} requests left, reset in {pause / 60:.0f}min "
                f"(over the {self.max_wait / 60:.0f}min cap) — rerun to resume"
            )
        if pause > 0:
            print(f"  … {rate.remaining} requests left; waiting {pause:.0f}s for reset",
                  file=sys.stderr)
            time.sleep(pause)


# --------------------------------------------------------------------------
# entries.json


def entry_key(entry: dict) -> tuple[str, str]:
    return (entry["owner"].lower(), entry["repo"].lower())


def load_entries() -> tuple[dict, dict[tuple[str, str], dict]]:
    if not OUT.exists():
        print(f"  ! {OUT} not found — run tools/extract_links.py first", file=sys.stderr)
        raise SystemExit(2)
    data = json.loads(OUT.read_text(encoding="utf-8"))
    index: dict[tuple[str, str], dict] = {}
    for entry in data.get("entries", []):
        index.setdefault(entry_key(entry), entry)
    return data, index


def write_entries(data: dict) -> None:
    """Write via a temp file: a crash mid-write must not truncate a tracked input."""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.parent / (OUT.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    tmp.replace(OUT)


def iso_date(stamp: str | None) -> str | None:
    """`2024-05-06T07:08:09Z` -> `2024-05-06`, the form verified_at uses."""
    return stamp[:10] if isinstance(stamp, str) and len(stamp) >= 10 else None


def apply_success(entry: dict, stars: int, pushed: str | None, today: str) -> None:
    entry["stars"] = stars
    entry["source_updated_at"] = pushed
    entry["stars_source"] = STARS_SOURCE
    entry["verified_at"] = today
    # Reachable again, so a prior 404 no longer stands.
    entry["unavailable"] = False


def apply_gone(entry: dict) -> None:
    """Mark unavailable and change nothing else. In particular, not `stars`."""
    entry["unavailable"] = True


# --------------------------------------------------------------------------
# checkpoints


def checkpoint_path(source_id: str) -> pathlib.Path:
    return CKPT_DIR / f"{source_id}.json"


def read_checkpoint(source_id: str) -> dict:
    path = checkpoint_path(source_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"  ! {source_id}: unreadable checkpoint, redoing source", file=sys.stderr)
        return {}


def write_checkpoint(source_id: str, done: dict) -> None:
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": source_id,
        "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "api_base": API_BASE,
        **done,
    }
    path = checkpoint_path(source_id)
    tmp = CKPT_DIR / f"{source_id}.json.tmp"
    tmp.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


# --------------------------------------------------------------------------


def select_sources(data: dict, only: list[str] | None) -> list[str]:
    known = {s for e in data.get("entries", []) for s in e.get("sources", [])}
    if not only:
        return sorted(known)
    unknown = [s for s in only if s not in known]
    if unknown:
        print(f"  ! unknown source id(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"  ! known: {', '.join(sorted(known))}", file=sys.stderr)
        raise SystemExit(2)
    return [s for s in only if s in known]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Enrich data/entries.json with stars, verified_at and provenance."
    )
    ap.add_argument("--dry-run", action="store_true", help="report, write nothing")
    ap.add_argument("--offline", action="store_true", help="make no network calls at all")
    ap.add_argument("--source", action="append", metavar="ID",
                    help="limit to one source (repeatable, or comma-separated)")
    ap.add_argument("--force", action="store_true",
                    help="redo sources that are already checkpointed")
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                    help=f"seconds between requests (default {DEFAULT_DELAY})")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--max-retries", type=int, default=4)
    ap.add_argument("--flush-every", type=int, default=200,
                    help="write entries.json every N updates within a source")
    ap.add_argument("--max-consecutive-failures", type=int, default=10,
                    help="abort a source after this many failures in a row")
    args = ap.parse_args()

    # Requirement, not advice: 60 req/hr against 5,583 entries is 86 hours.
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print(
            "error: GITHUB_TOKEN is not set.\n"
            "       The GitHub REST API allows 60 requests/hour unauthenticated and\n"
            "       this corpus holds ~5,225 distinct repositories — about 86 hours.\n"
            "       For local use: export GITHUB_TOKEN=$(gh auth token)",
            file=sys.stderr,
        )
        return 2

    only: list[str] | None = None
    if args.source:
        only = [s.strip() for chunk in args.source for s in chunk.split(",") if s.strip()]

    data, index = load_entries()
    today = datetime.now(timezone.utc).date().isoformat()
    sources = select_sources(data, only)

    # in_repo entries are directories inside a source repo, not repositories.
    # Looking them up would copy the list's own star count onto each one.
    repos = [e for e in data["entries"] if not e.get("in_repo")]
    in_repo = len(data["entries"]) - len(repos)

    totals = {"planned": 0, "updated": 0, "unavailable": 0, "failed": 0, "skipped": 0}
    rows: list[tuple[str, int, int, int, int, int]] = []
    aborted = False

    if args.offline:
        print("offline: no network calls")
        for sid in sources:
            planned = len({entry_key(e) for e in data["entries"] if sid in e.get("sources", [])
                           and not e.get("in_repo")})
            rows.append((sid, planned, 0, 0, 0, 0))
            totals["planned"] += planned
    else:
        gate = RateGate()
        for sid in sources:
            # Repos reachable from this source. A repo listed by several sources is
            # fetched once; whichever source runs first writes it.
            keys = sorted({entry_key(e) for e in data["entries"]
                           if sid in e.get("sources", []) and not e.get("in_repo")})

            ckpt = {} if args.force else read_checkpoint(sid)
            # JSON has no tuples: pending keys come back as ["owner","repo"]
            # lists, which cannot be looked up in a dict. Rebuild the tuples.
            pending = [tuple(k) for k in ckpt.get("pending", []) if tuple(k) in index]
            if ckpt and not pending:
                print(f"\n{sid}: already checkpointed ({len(keys)} entries) — skipping")
                rows.append((sid, 0, 0, 0, 0, len(keys)))
                totals["skipped"] += len(keys)
                continue

            todo = pending if pending else keys
            started_from = "retrying %d transient failure(s)" % len(pending) if pending else "full run"
            print(f"\n{sid}: {len(todo)} lookup(s) ({started_from})")

            updated = unavailable = failed = 0
            unresolved: list[list[str]] = []
            streak = 0
            since_flush = 0
            dirty = False

            for n, key in enumerate(todo, 1):
                owner, repo = key
                result = fetch_repo(owner, repo, token, timeout=args.timeout,
                                    max_retries=args.max_retries)

                if result.status == OK:
                    entry = index[key]
                    if result.stars is None:
                        # A 200 with no count is not a confirmation of anything.
                        failed += 1
                        unresolved.append(list(key))
                        streak += 1
                        print(f"  ! {owner}/{repo}: no stargazers_count — left untouched",
                              file=sys.stderr)
                    else:
                        apply_success(entry, result.stars, iso_date(result.pushed_at), today)
                        updated += 1
                        dirty = True
                        streak = 0
                        gate.hold(result.rate)
                elif result.status == GONE:
                    apply_gone(index[key])
                    unavailable += 1
                    dirty = True
                    streak = 0
                    print(f"  x {owner}/{repo}: {result.detail} — marked unavailable, "
                          f"stars kept at {index[key].get('stars')}", file=sys.stderr)
                elif result.status == THROTTLED:
                    unresolved.append(list(key))
                    print(f"  ! {sid}: rate limited at {owner}/{repo} ({result.detail}) — "
                          f"source not checkpointed, rerun to resume", file=sys.stderr)
                    aborted = True
                    break
                else:
                    failed += 1
                    unresolved.append(list(key))
                    streak += 1
                    print(f"  ! {owner}/{repo}: {result.detail} — left untouched",
                          file=sys.stderr)

                if args.delay > 0 and n < len(todo):
                    time.sleep(args.delay)

                # Flush inside a long source so a rate wall or a kill costs at
                # most flush-every lookups rather than the whole source.
                since_flush += 1
                if dirty and not args.dry_run and since_flush >= args.flush_every:
                    write_entries(data)
                    since_flush = 0

                if streak >= args.max_consecutive_failures:
                    print(f"  ! {sid}: {streak} consecutive failures — aborting source, "
                          f"not checkpointed", file=sys.stderr)
                    aborted = True
                    break

            if dirty and not args.dry_run:
                write_entries(data)

            rows.append((sid, len(todo), updated, unavailable, failed, 0))
            totals["planned"] += len(todo)
            totals["updated"] += updated
            totals["unavailable"] += unavailable
            totals["failed"] += failed

            if aborted:
                # Every failed lookup is listed as pending, so the rerun refetches
                # exactly those and nothing else.
                write_checkpoint(sid, {
                    "entries": len(todo),
                    "updated": updated,
                    "unavailable": unavailable,
                    "failed": failed,
                    "completed": False,
                    "pending": unresolved,
                })
                break

            if not args.dry_run:
                write_checkpoint(sid, {
                    "entries": len(todo),
                    "updated": updated,
                    "unavailable": unavailable,
                    "failed": failed,
                    "completed": not unresolved,
                    "pending": unresolved,
                })

    print(f"\n{'source':<24} {'lookups':>9} {'updated':>8} {'404/451':>8} "
          f"{'failed':>7} {'skipped':>8}")
    print("-" * 68)
    for sid, planned, upd, unavail, fail, skip in rows:
        print(f"{sid:<24} {planned:>9,} {upd:>8,} {unavail:>8,} {fail:>7,} {skip:>8,}")
    print("-" * 68)
    print(f"updated {totals['updated']:,}   unavailable {totals['unavailable']:,}   "
          f"left untouched {totals['failed']:,}   skipped (checkpointed) {totals['skipped']:,}")
    print(f"skipped {in_repo} in-repo paths (directories, not repositories); "
          f"{len(repos):,} of {len(data['entries']):,} entries are distinct repositories")

    changed = bool(totals["updated"] or totals["unavailable"])
    if args.dry_run:
        print("\ndry run: nothing written")
    elif args.offline:
        print("\noffline: nothing written")
    else:
        print(f"\nwrote {OUT.relative_to(ROOT)}")
        print(f"checkpoints in {CKPT_DIR.relative_to(ROOT)}/")

    print("CHANGED=1" if changed else "CHANGED=0")
    return 1 if aborted else 0


if __name__ == "__main__":
    sys.exit(main())