---
title: Repositories
description: Every GitHub repository mentioned by the ten indexed awesome lists, deduplicated and searchable.
layout: page
---

<script setup>
import { computed, ref } from 'vue'
import { useData } from 'vitepress'

const { theme } = useData()
const entryIndex = theme.value.entryIndex
const entries = entryIndex.entries
const sourceMeta = theme.value.sources

const q = ref('')
const source = ref('all')

const sourceNames = computed(() => sourceMeta.map((s) => s.id))

const results = computed(() => {
  const needle = q.value.trim().toLowerCase()
  return entries.filter((e) => {
    if (source.value !== 'all' && !e.sources.includes(source.value)) return false
    if (!needle) return true
    return (
      e.name.toLowerCase().includes(needle) ||
      e.repo.toLowerCase().includes(needle) ||
      (e.description || '').toLowerCase().includes(needle)
    )
  })
})

// Source distribution. awesome-mcp-servers is the large majority of the corpus, so a plain
// "N results" count would misrepresent any single-source view of it.
const distribution = computed(() =>
  sourceMeta
    .map((s) => ({
      id: s.id,
      page: s.page,
      count: entries.filter((e) => e.sources.includes(s.id)).length,
    }))
    .filter((s) => s.count > 0)
    .sort((a, b) => b.count - a.count)
)

const multi = computed(() => entries.filter((e) => e.sources.length > 1).length)
const described = computed(() => entries.filter((e) => (e.description || '').length > 8).length)
const cap = 300
const shown = computed(() => results.value.slice(0, cap))
</script>

<div class="ri">
  <header class="ri__hero">
    <h1>Repositories</h1>
    <p class="ri__lede">
      Every GitHub repository mentioned by the ten <a href="/sources">indexed lists</a>,
      deduplicated on <code>owner/repo</code>. Descriptions are the source list curator's wording —
      this site has not verified that any of these repositories are maintained, safe, or good.
    </p>
    <p v-if="entryIndex.generated_at" class="ri__stamp">
      Generated {{ entryIndex.generated_at.slice(0, 10) }} from {{ sourceMeta.length }} sources ·
      {{ entries.length.toLocaleString() }} unique ·
      {{ multi }} listed in more than one source ·
      {{ described.toLocaleString() }} carry a description
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

  <p class="ri__count">
    {{ results.length.toLocaleString() }} match<template v-if="results.length !== 1">es</template>
    <template v-if="results.length > cap"> · showing first {{ cap }}</template>
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

  <p v-if="!results.length" class="ri__empty">
    Nothing matches. <button class="ri__reset" @click="q = ''; source = 'all'">Clear filters</button>
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

  <p v-if="results.length > cap" class="ri__more">
    Narrow the search to see more of the remaining
    {{ (results.length - cap).toLocaleString() }}.
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