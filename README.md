# awesomes

**Live:** [awesome.rairahulr1.com](https://awesome.rairahulr1.com) · **Source:** this repo

A searchable index of curated `awesome-*` lists on GitHub. One page per source list: the original
description preserved verbatim, a nest-level breakdown of what that list actually contains, a
star count snapshotted from GitHub, a direct link to the source, and its own comment thread.

Nothing is mirrored. Every entry is an index entry, not a fork.

## Why this exists

`awesome-*` lists already exist and are well-maintained. What they lack is a way to *compare* them —
there is no single page that says "here are the 10 lists worth knowing, here's what each one
covers, here's which are still alive". This repo is that page.

## Structure

```
awesomes/
├── .github/workflows/deploy.yml   # build → force-push dist to gh-pages
├── docs/
│   ├── .vitepress/
│   │   ├── config.mjs             # reads entries, emits index + SEO meta
│   │   ├── components/            # RepoIndex.vue, Comments.vue
│   │   └── theme/index.js
│   ├── public/                    # favicon.svg, og.png, CNAME
│   ├── index.md                   # search + filter UI
│   └── repos/                     # one page per indexed list
│       └── <name>.md
└── tools/make_og.py               # regenerates the Open Graph card
```

## Adding an entry

Create `docs/repos/<name>.md` with this frontmatter:

```yaml
---
title: awesome-thing
url: https://github.com/owner/awesome-thing   # required — also the dedupe key
stars: 12300
stars_as_of: 2026-10-09
stars_source: github-repo-page-badge
type: libraries                                # libraries | apps | agents | skills | tools | servers | plugins | resources
categories: [php, backend]                     # shown as chips, filterable
tags: [php, composer]                          # searchable, not shown
description: The upstream description, verbatim.
license: MIT
---
```

Body: an H1, the description as a blockquote, a source line, a breakdown of the source's own
section structure, and `<Comments />`.

Nothing else needs editing — the sidebar, the category and type filters, the all-lists table and the
count are all derived from the frontmatter at build time.

## How it works

| Concern | Approach |
|---|---|
| Entry list | Parsed from `docs/repos/*.md` at config time and passed via `themeConfig.repos` |
| Why not `useData().pages` | It is empty during SSR, which silently renders an empty page |
| Dedupe | Canonical `owner/repo` from `url`; first occurrence wins |
| Search | VitePress local search (client-side index, no backend) |
| Filtering | Category and type dropdowns over the same array |
| Comments | Utterances, one GitHub issue per page path |
| SEO | Per-page canonical, Open Graph, Twitter cards and `SoftwareSourceCode` JSON-LD |
| Hosting | GitHub Pages served from `gh-pages`, custom domain via `docs/public/CNAME` |

### Deployment

`main` pushes build the site and force-push `docs/.vitepress/dist` to `gh-pages`. This is plain
`git`, not `actions/deploy-pages` — that action returned `404 Cannot find any run with
github.run_id` on every attempt for this repo. A `.nojekyll` in the published tree stops Pages from
running Jekyll over the output.

### Star counts are snapshots

`stars` and `stars_as_of` are read off the GitHub repo page at the time of writing and **will
drift**. They are display metadata, not a live figure; the source link is authoritative. There is no
refresh job — see the open question below.

## Local development

```bash
npm ci
npm run dev      # http://localhost:5173
npm run build    # → docs/.vitepress/dist
npm run serve    # preview the built site
```

## Open questions

- **Star freshness.** Should a scheduled job refresh counts, or should `stars` be dropped in favour
  of a live shields.io badge at render time?
- **Depth.** Pages currently carry the source's own top-level section structure. Where a source is
  deeper, that should be expanded too — but only where it was actually read, never inferred.
- **Contribution flow.** Currently direct commits to `main`. If this takes outside contributors,
  the entry format above is the natural PR contract.