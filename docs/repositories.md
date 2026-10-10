---
title: Repositories
description: Every GitHub repository mentioned by the ten indexed awesome lists, deduplicated and searchable.
layout: page
---

<script setup>
import { computed, ref, watch } from 'vue'
import { useData } from 'vitepress'
import { decodeRecords, SSR_PAGE, CHUNK_DIR } from '../tools/entry_chunks.mjs'
// Written by docs/.vitepress/config.mjs on every config load. Carries the first page of records —
// the rows the static HTML below already rendered — so SSR and hydration agree on the markup
// without a fetch, plus everything needed to decode and filter them. The remaining rows arrive as
// static JSON under /repo-index/, fetched only once a reader filters or searches.
import bootstrap from './.vitepress/generated/repo-page.json'

const { theme } = useData()
const sourceMeta = theme.value.sources

const cap = SSR_PAGE
const sourceIds = bootstrap.sourceIds
const stats = bootstrap.stats

const q = ref('')
const source = ref('all')

const CHUNK_BASE = `${import.meta.env.BASE_URL}${CHUNK_DIR}/`

// What the static HTML rendered, plus whatever has been fetched since.
const rows = decodeRecords(bootstrap.entries, sourceIds)
const byIndex = new Map(rows.map((e) => [e.i, e]))
const entries = ref(rows)

const manifest = ref(null)
const covered = ref([])
const failed = ref(false)

const sourceNames = computed(() => sourceMeta.map((s) => s.id))

// Distribution. awesome-mcp-servers is the large majority of the corpus, so a plain
// "N results" count would misrepresent any single-source view of it. Counts come from the build's
// own aggregate rather than from the loaded rows, so the chips are correct before anything loads.
const distribution = computed(() =>
  bootstrap.sources
    .map((s) => ({ id: s.id, page: s.page, count: s.count }))
    .filter((s) => s.count > 0)
    .sort((a, b) => b.count - a.count)
)

// Which chunks the current filter actually needs. Unfiltered, the answer is the total the build
// already recorded; a source filter needs that source's chunks; a text query needs every chunk,
// because it matches on description and not just on name.
//
// The `page` chunk is excluded from all three: those records arrived in this page's JS bundle, so
// fetching page.json again would be a 70 KB request for bytes already in memory.
const wanted = computed(() => {
  if (!manifest.value) return []
  const list = manifest.value.chunks.filter((c) => !c.page)
  return source.value === 'all'
    ? list.map((c) => c.key)
    : list.filter((c) => c.source === source.value).map((c) => c.key)
})

const filtering = computed(() => q.value.trim() !== '' || source.value !== 'all')

// True when the loaded rows are a superset of what the current filter needs. Until then any match
// count would be a partial count presented as a total, so the page says it is still loading.
const settled = computed(
  () => !filtering.value || wanted.value.every((k) => covered.value.includes(k))
)

const results = computed(() => {
  const needle = q.value.trim().toLowerCase()
  return entries.value.filter((e) => {
    if (source.value !== 'all' && !e.sources.includes(source.value)) return false
    if (!needle) return true
    return (
      e.name.toLowerCase().includes(needle) ||
      e.repo.toLowerCase().includes(needle) ||
      (e.description || '').toLowerCase().includes(needle)
    )
  })
})

// Exact when the dataset covers the filter, otherwise the known corpus total — which is the
// correct count for the default unfiltered view, and the only honest thing to show mid-load.
const matchCount = computed(() => (filtering.value && settled.value ? results.value.length : stats.total))

const shown = computed(() => results.value.slice(0, cap))

let loading = false
async function loadChunks() {
  if (loading) return
  loading = true
  failed.value = false
  try {
    for (;;) {
      if (!manifest.value) {
        const res = await fetch(`${CHUNK_BASE}manifest.json`)
        if (!res.ok) throw new Error(`manifest.json ${res.status}`)
        manifest.value = await res.json()
      }
      const want = wanted.value.filter((k) => !covered.value.includes(k))
      if (!want.length) break
      const bodies = await Promise.all(
        want.map((k) =>
          fetch(`${CHUNK_BASE}${k}.json`).then((res) => {
            if (!res.ok) throw new Error(`${k}.json ${res.status}`)
            return res.json()
          }),
        ),
      )
      // Rows arrive in whatever chunk order the fetches settle in; `i` is the index the extractor
      // assigned, so sorting by it restores the corpus order the 300-row cap is defined against.
      bodies.forEach((body, n) => {
        for (const e of decodeRecords(body.e, manifest.value.sourceIds)) {
          if (!byIndex.has(e.i)) byIndex.set(e.i, e)
        }
        if (!covered.value.includes(want[n])) covered.value.push(want[n])
      })
      entries.value = [...byIndex.values()].sort((a, b) => a.i - b.i)
    }
  } catch (err) {
    failed.value = true
    console.error('[repositories] could not load entry chunks:', err)
  } finally {
    loading = false
  }
}

watch([q, source], () => {
  loadChunks()
})

function reset() {
  q.value = ''
  source.value = 'all'
}
</script>

<div class="ri">
  <header class="ri__hero">
    <h1>Repositories</h1>
    <p class="ri__lede">
      Every GitHub repository mentioned by the ten <a href="/sources">indexed lists</a>,
      deduplicated on <code>owner/repo</code>. Descriptions are the source list curator's wording —
      this site has not verified that any of these repositories are maintained, safe, or good.
    </p>
    <p v-if="bootstrap.generated_at" class="ri__stamp">
      Generated {{ bootstrap.generated_at.slice(0, 10) }} from {{ sourceMeta.length }} sources ·
      {{ stats.total.toLocaleString() }} unique ·
      {{ stats.multi }} listed in more than one source ·
      {{ stats.described.toLocaleString() }} carry a description
    </p>
  </header>

  <div class="ri__controls">
    <input
      v-model="q"
      class="ri__search"
      type="search"
      placeholder="Search repository names and descriptions…"
      aria-label="Search repositories"
    />
    <select v-model="source" aria-label="Filter by source list">
      <option value="all">All sources</option>
      <option v-for="id in sourceNames" :key="id" :value="id">{{ id }}</option>
    </select>
  </div>

  <p class="ri__count" aria-live="polite">
    <template v-if="!settled">Searching {{ stats.total.toLocaleString() }} entries…</template>
    <template v-else>
      {{ matchCount.toLocaleString() }} match<template v-if="matchCount !== 1">es</template>
      <template v-if="matchCount > cap"> · showing first {{ cap }}</template>
    </template>
    <template v-if="failed">
      · could not load the full index.
      <button class="ri__reset" @click="loadChunks">Retry</button>
    </template>
  </p>

  <section class="ri__dist" aria-label="Share by source list">
    <span class="ri__distlabel">Share by source:</span>
    <button
      v-for="d in distribution"
      :key="d.id"
      class="ri__distchip"
      :class="{ 'ri__distchip--on': source === d.id }"
      @click="source = source === d.id ? 'all' : d.id"
    >
      {{ d.id }} <em>{{ d.count.toLocaleString() }}</em>
    </button>
  </section>

  <p v-if="!results.length && settled" class="ri__empty">
    Nothing matches. <button class="ri__reset" @click="reset">Clear filters</button>
  </p>

  <ul class="ri__list">
    <li v-for="e in shown" :key="e.url" class="ri__row">
      <div class="ri__rowhead">
        <a class="ri__name" :href="e.url" target="_blank" rel="noopener">
          {{ e.owner }}/{{ e.repo }} ↗
        </a>
        <span v-if="e.in_repo" class="ri__inrepo" title="Lives inside the source repository">in-source</span>
        <span class="ri__sources">
          <a v-for="s in e.sources" :key="s" :href="`/repos/${s}`" class="ri__srctag">{{ s }}</a>
        </span>
      </div>
      <p v-if="e.description" class="ri__desc">{{ e.description }}</p>
    </li>
  </ul>

  <p v-if="matchCount > cap" class="ri__more">
    Narrow the search to see more of the remaining
    {{ (matchCount - cap).toLocaleString() }}.
  </p>
</div>

<style scoped>
.ri { max-width: 980px; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }
.ri__hero h1 { font-size: 2.25rem; margin: 0 0 0.5rem; letter-spacing: -0.02em; }
.ri__lede { color: var(--vp-c-text-2); max-width: 64ch; }
.ri__stamp { font-size: 0.85rem; color: var(--vp-c-text-3); }

.ri__controls { display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 1.5rem 0 0.6rem; }
.ri__search {
  flex: 1 1 320px; padding: 0.6rem 0.85rem; font-size: 0.95rem;
  border: 1px solid var(--vp-c-divider); border-radius: 8px;
  background: var(--vp-c-bg-soft); color: var(--vp-c-text-1);
}
.ri__controls select {
  padding: 0.6rem 0.75rem; font-size: 0.9rem;
  border: 1px solid var(--vp-c-divider); border-radius: 8px;
  background: var(--vp-c-bg-soft); color: var(--vp-c-text-1);
}
.ri__count { font-size: 0.82rem; color: var(--vp-c-text-3); margin: 0 0 1rem; }

.ri__dist { display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: center; margin-bottom: 1.25rem; }
.ri__distlabel { font-size: 0.78rem; color: var(--vp-c-text-3); margin-right: 0.25rem; }
.ri__distchip {
  font-size: 0.74rem; padding: 0.2rem 0.5rem; cursor: pointer;
  border: 1px solid var(--vp-c-divider); border-radius: 999px;
  background: transparent; color: var(--vp-c-text-2);
}
.ri__distchip em { font-style: normal; color: var(--vp-c-text-3); margin-left: 0.2rem; }
.ri__distchip--on { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }

.ri__list { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.6rem; }
.ri__row {
  padding: 0.8rem 1rem; border: 1px solid var(--vp-c-divider);
  border-radius: 8px; background: var(--vp-c-bg-soft);
}
.ri__rowhead { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: baseline; }
.ri__name { font-weight: 600; font-size: 0.92rem; color: var(--vp-c-brand-1); text-decoration: none; }
.ri__name:hover { text-decoration: underline; }
.ri__inrepo {
  font-size: 0.65rem; padding: 0.1rem 0.35rem; border-radius: 999px;
  border: 1px solid var(--vp-c-divider); color: var(--vp-c-text-3);
}
.ri__sources { margin-left: auto; display: flex; gap: 0.3rem; flex-wrap: wrap; }
.ri__srctag {
  font-size: 0.68rem; color: var(--vp-c-text-3); text-decoration: none;
  border: 1px solid var(--vp-c-divider); border-radius: 999px; padding: 0.1rem 0.4rem;
}
.ri__srctag:hover { color: var(--vp-c-brand-1); border-color: var(--vp-c-brand-1); }
.ri__desc { margin: 0.35rem 0 0; font-size: 0.85rem; line-height: 1.5; color: var(--vp-c-text-2); }

.ri__empty { padding: 2rem 0; color: var(--vp-c-text-2); }
.ri__reset {
  border: 1px solid var(--vp-c-divider); background: transparent;
  color: var(--vp-c-brand-1); border-radius: 6px; padding: 0.2rem 0.5rem; cursor: pointer;
}
.ri__more { margin-top: 1.5rem; font-size: 0.85rem; color: var(--vp-c-text-3); text-align: center; }
</style>
