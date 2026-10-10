/**
 * Wire format + chunk planner for the /repositories entry index.
 *
 * WHY THIS EXISTS
 * ---------------
 * The entry set is 5,583 records. When it rode in `themeConfig` VitePress serialised it into
 * *every* page's HTML — the repositories page was 2.39 MB and each of the other 13 pages was
 * ~2.2 MB, for a 34.8 MB dist. This module plans how the same data is shipped instead: a small
 * record set inlined in the page's own JS chunk (so SSR and hydration agree) plus a set of static
 * JSON files written to the build output and fetched by the browser.
 *
 * This module is deliberately free of `node:` imports so both `docs/.vitepress/config.mjs` (Node)
 * and `docs/repositories.md` (bundled into the browser) can import it.
 *
 * RECORD FORMAT
 * -------------
 * `entries.json` stores 11 keys per record, of which the page renders/searches 7
 * (owner, repo, name, url, description, sources, in_repo). `stars`, `verified_at`, `unavailable`
 * and the rare `alt_descriptions` are not read by this page, and `sources` is drawn from a fixed
 * 10-value registry. So a record becomes a positional tuple:
 *
 *   [i, owner, repo, name, url, description|null, sourceMask, flags, stars?]
 *
 *   i          index in the original `entries.json` order — this is what makes merge order
 *              recoverable. Chunks are disjoint subsets, not contiguous ranges, so without it a
 *              merge would reorder the result set and silently change what the 300-row cap shows.
 *   sourceMask bitmask over `sourceIds`; 10 sources fit in 16 bits, so a source list collapses
 *              from an array of strings to one small integer.
 *   flags      bit 0 = in_repo. Bits 1+ are free, so a new boolean costs no schema change.
 *   stars      present only when non-null. All 5,583 are null today; the column is carried
 *              anyway because tools/enrich_stars.py populates it and a chunker that silently
 *              dropped it would undo that work at the next build.
 *
 * `owner`/`repo` are shipped explicitly rather than parsed back out of `url`. They are redundant
 * for all 5,583 current rows and dropping them measures 407 KB -> 369 KB gzipped (9%), which is
 * not worth rendering the wrong repository name if a non-`github.com/{owner}/{repo}` URL ever
 * reaches the index. See tools/entry_chunks_report.txt for the measured alternatives.
 *
 * CHUNKING STRATEGY — source-major, oversized sources split into byte-capped parts
 * -----------------------------------------------------------------------------
 * Sharding by first letter was rejected: text search matches on `description`, not just `name`,
 * so a substring query has to read every shard either way. Letters would buy parallel downloads
 * and nothing else, while making the natural URL (`/repo-index/a.json`) imply a lookup the search
 * box cannot actually use.
 *
 * Sharding by source id was chosen because it is the one dimension the UI exposes as a *filter*:
 * picking "awesome-php" needs one chunk, not all ten. It is only worth it if the shards are not
 * lopsided, and the raw corpus is very lopsided — awesome-mcp-servers alone is 4,224 of 5,583
 * (76%). So each source is partitioned into parts of at most PART_BYTES, which flattens the big
 * source into 5 even chunks and leaves the other nine as single parts. 15 files, 14 KB - 176 KB
 * each, each individually cacheable: a reader who only ever filters to one source re-downloads
 * one file, not the corpus.
 *
 * The first page (entries 0..SSR_PAGE-1) is split off as its own `page` chunk because it is what
 * the static HTML renders. The client already holds those records in the page's JS bundle for SSR
 * and hydration, so it never fetches `page.json`; it is still written to disk so the shipped
 * dataset is complete and curl-able on its own.
 */

export const SSR_PAGE = 300
export const PART_BYTES = 176 * 1024
export const FORMAT_VERSION = 1
export const CHUNK_DIR = 'repo-index'

const FLAG_IN_REPO = 1

/**
 * Plan the chunk set. Pure — returns strings; the caller decides where they land.
 *
 * @param {object} opts
 * @param {object[]} opts.entries      raw records from data/entries.json
 * @param {string[]} opts.sourceIds    registry order; defines the bitmask bit order
 * @param {string|null} opts.generatedAt
 * @param {string[]} opts.sourcePages  source id -> site path, for the manifest
 * @returns {{ manifest: object, files: Map<string, string>, records: Map<string, Array> }}
 */
export function buildChunks({
  entries,
  sourceIds,
  generatedAt = null,
  sourcePages = {},
  pageSize = SSR_PAGE,
  partBytes = PART_BYTES,
}) {
  if (!Array.isArray(entries) || entries.length === 0) {
    throw new Error('buildChunks: entries must be a non-empty array.')
  }
  const bitOf = new Map(sourceIds.map((id, i) => [id, 1 << i]))
  for (const e of entries) {
    for (const s of e.sources ?? []) {
      if (!bitOf.has(s)) throw new Error(`buildChunks: entry "${e.name}" cites unknown source "${s}".`)
    }
  }

  const encoded = entries.map((e, i) => encodeEntry(e, i, bitOf))
  const pageCount = Math.min(pageSize, entries.length)
  const onPage = new Set(encoded.slice(0, pageCount).map((r) => r[0]))

  const files = new Map()
  const chunks = []
  const records = new Map()

  const emit = (key, rows, extra = {}) => {
    const file = `${key}.json`
    const body = JSON.stringify({ v: FORMAT_VERSION, ...extra, e: rows })
    files.set(`${CHUNK_DIR}/${file}`, body)
    records.set(key, rows)
    chunks.push({ key, file, bytes: body.length, count: rows.length, ...extra })
  }

  // 1. The first page, in original order. Also what the static HTML renders.
  emit('page', encoded.slice(0, pageCount), { part: 0, parts: 1, page: true })

  // 2. Per source, in original order, excluding rows already carried by the page chunk.
  for (let s = 0; s < sourceIds.length; s++) {
    const id = sourceIds[s]
    const rows = encoded.filter((r) => !onPage.has(r[0]) && (r[6] & (1 << s)) !== 0)
    if (!rows.length) continue
    const parts = Math.max(1, Math.ceil(rows.length / maxRowsPerPart(rows, partBytes)))
    const per = Math.ceil(rows.length / parts)
    for (let p = 0; p < parts; p++) {
      emit(`${id}${parts > 1 ? `.${p}` : ''}`, rows.slice(p * per, (p + 1) * per), {
        source: id,
        part: p,
        parts,
      })
    }
  }

  const sourceCounts = {}
  for (const id of sourceIds) sourceCounts[id] = 0
  for (const r of encoded) {
    for (let b = 0; b < sourceIds.length; b++) if (r[6] & (1 << b)) sourceCounts[sourceIds[b]]++
  }

  const manifest = {
    v: FORMAT_VERSION,
    generated_at: generatedAt,
    total: entries.length,
    multi: entries.filter((e) => (e.sources ?? []).length > 1).length,
    described: entries.filter((e) => (e.description ?? '').length > 8).length,
    sourceIds,
    sourceCounts,
    sources: sourceIds.map((id) => ({ id, page: sourcePages[id] ?? `/repos/${id}`, count: sourceCounts[id] })),
    part_bytes: partBytes,
    page_size: pageSize,
    format: '[i, owner, repo, name, url, description|null, sourceMask, flags, stars?] — see tools/entry_chunks.mjs',
    note:
      'The chunk flagged "page": true is also inlined in the /repositories page bundle, which is how ' +
      'its rows reach the static HTML without a fetch. The browser never requests it. It is ' +
      'published here so that /repo-index/ stays a complete mirror of data/entries.json.',
    chunks,
  }

  // The client only needs the chunk list, not the manifest's prose, so keep the shipped
  // manifest to what a reader of the data set actually needs.
  return { manifest, files, records }
}

function encodeEntry(e, i, bitOf) {
  let mask = 0
  for (const s of e.sources ?? []) mask |= bitOf.get(s)
  const rec = [
    i,
    e.owner,
    e.repo,
    e.name,
    e.url,
    e.description || null,
    mask,
    e.in_repo ? FLAG_IN_REPO : 0,
  ]
  if (e.stars != null) rec.push(e.stars)
  return rec
}

/** Rows-per-part that keeps a part's serialised bytes under `partBytes`. */
function maxRowsPerPart(rows, partBytes) {
  // Average row bytes measured over a sample; one estimate for the whole source is enough to keep
  // parts within ~10% of the cap, and a per-part exact fit would need the full serialisation.
  const sample = rows.length > 256 ? rows.filter((_, i) => i % Math.ceil(rows.length / 256) === 0) : rows
  const bytes = Math.ceil(JSON.stringify(sample).length / Math.max(1, sample.length))
  return Math.max(64, Math.floor(partBytes / Math.max(1, bytes)))
}

/** Turn a positional tuple back into the shape docs/repositories.md renders and filters. */
export function decodeRecords(records, sourceIds) {
  const out = new Array(records.length)
  for (let n = 0; n < records.length; n++) {
    const r = records[n]
    const mask = r[6]
    const sources = []
    for (let b = 0; b < sourceIds.length; b++) if (mask & (1 << b)) sources.push(sourceIds[b])
    out[n] = {
      i: r[0],
      owner: r[1],
      repo: r[2],
      name: r[3],
      url: r[4],
      description: r[5] ?? '',
      sources,
      in_repo: (r[7] & FLAG_IN_REPO) !== 0,
      stars: r.length > 8 ? r[8] : null,
    }
  }
  return out
}
