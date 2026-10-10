# Proposal

## Why

The site indexes ten `awesome-*` lists but stops at their front doors. Everything those lists
contain — 5,186 distinct repositories, measured by extracting all ten READMEs on 2026-10-09 — is
only reachable by opening the source. That is worst exactly where it matters most:
`awesome-mcp-servers` alone carries 4,153 entries inside a 1.4 MB README, and the two
`awesome-ai-apps`-style lists link to 259 projects via paths that resolve to nothing unless a tool
knows the base URL.

Meanwhile the duplication is real but invisible: 21 repositories are listed by more than one source
list, and there is no single place that says so. Every reader repeats the same work — pick a list,
open a huge README, search it, repeat.

## What Changes

- Add a generated flat index of every repository mentioned by the ten indexed lists, deduplicated
  on canonical `owner/repo`.
- Add extraction tooling that parses each source README into entries. The ten lists use at least
  five incompatible link formats, so each format gets its own parser with fixture tests.
- Resolve repo-relative links against the source list's base URL, so entries that live inside the
  source repository become visible instead of being silently dropped.
- Record, per entry: link, description, the source list(s) that mention it, star count, and when
  this site last verified it.
- Take descriptions from the source list curator's wording, attributed to them — never restated as
  a claim this site makes about the repository.
- Render entries as filterable, searchable views (query, category, source) rather than as 5,186
  standalone URLs.
- Add a scheduled, resumable enrichment job that refreshes star counts and writes only the
  generated data file.

No existing page changes. The ten hand-written entry pages under `docs/repos/` keep their content,
their URLs and their canonical status.

## Capabilities

### New Capabilities

- `entry-extraction`: Turning the ten source READMEs into structured entries — link parsing across
  five markdown formats, resolution of repo-relative links, description capture, attribution to the
  source list, and deduplication on canonical `owner/repo`.
- `entry-metadata`: Volatile per-entry facts — star counts, when this site last verified a link,
  and the upstream list's last commit — including how a scheduled refresh updates them and how it
  behaves when the GitHub API fails.
- `entry-index`: How entries are presented and found — filterable and searchable views, display of
  source attribution, and the canonical-URL and SEO treatment that keeps per-list pages authoritative.

### Modified Capabilities

None. This is the first change; the project has no existing specs.

## Impact

**New:** `tools/extract_links.py`, `tools/enrich_stars.py`, `tools/build_entries.py`, a generated
`data/entries.json`, a daily GitHub Actions workflow, and filterable entry views.

**Unchanged:** the ten pages in `docs/repos/`, the VitePress site build, the deploy workflow, and
the custom domain.

**Dependencies:** the GitHub REST API. Entry-level enrichment needs roughly 5,200 requests — about
86 hours unauthenticated against 60/hour, about 1 hour with `GITHUB_TOKEN` at 5,000/hour. The token
is a hard requirement, not an optimisation.

**Risks:**

- The five README formats are the main engineering risk. A parser that silently matches nothing
  produces a smaller index and no error, which is the failure mode most likely to go unnoticed.
- Corpus quality is dominated by one list. `awesome-mcp-servers` is ~80% of all entries and is
  community-submitted, so its entries skew the whole index and none of them are verified as
  maintained or safe.

## Out of scope

- **Verifying entry quality.** Nothing in this change checks that a listed repository is
  maintained, safe, or good. Entries stay claims made by named curators.
- **A standalone page per entry.** 5,186 auto-generated pages is thin content; entries render as
  filterable views instead, and per-list pages stay canonical.
- **Hand-editing entries.** The index is generated. Curation stays at the list level.
- **Sources beyond the current ten.** Adding a source list is configuration, but no eleventh
  source is being added here.
- **Non-GitHub links.** Entries are GitHub repositories. Documentation sites, blogs, conference
  links and package registries inside these lists are not indexed.
- **A refresh mechanism for `awesome-mcp-servers` entry counts per category.** The category
  structure is descriptive, not a facet in this change.