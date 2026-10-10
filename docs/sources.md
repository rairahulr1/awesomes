---
title: Sources
description: The ten curated awesome lists this index is built from, with how many repository entries each contributes.
layout: page
---

<script setup>
import { computed } from 'vue'
import { useData } from 'vitepress'

const { theme } = useData()
const sources = theme.value.sources
const entryIndex = theme.value.entryIndex

const total = computed(() => sources.reduce((n, s) => n + s.entryCount, 0))
const fmt = (n) => (n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n))
const share = (n) => (total.value ? `${((n / total.value) * 100).toFixed(1)}%` : '—')
</script>

<div class="src">
  <header class="src__hero">
    <h1>Sources</h1>
    <p class="src__lede">
      Ten curated <code>awesome-*</code> lists. Everything in the repository index comes from these
      files — nothing is invented here, and each one is credited on every entry it produced.
    </p>
    <p class="src__stats">
      <strong>{{ sources.length }}</strong> sources ·
      <strong>{{ total.toLocaleString() }}</strong> entry references extracted
      <template v-if="entryIndex.generated_at">
        · generated {{ entryIndex.generated_at.slice(0, 10) }}
      </template>
    </p>
  </header>

  <ul class="src__list">
    <li v-for="s in sources" :key="s.id" class="src__item">
      <div class="src__head">
        <a class="src__name" :href="s.page">{{ s.id }}</a>
        <span class="src__count" :title="`${s.entryCount.toLocaleString()} entries`">
          {{ fmt(s.entryCount) }} entries · {{ share(s.entryCount) }}
        </span>
      </div>
      <div class="src__meta">
        <a class="src__src" :href="`https://github.com/${s.owner}/${s.repo}`" target="_blank" rel="noopener">
          {{ s.owner }}/{{ s.repo }} ↗
        </a>
        <span class="src__fmt" v-for="f in s.formats" :key="f">{{ f }}</span>
      </div>
      <p v-if="s.notes" class="src__notes">{{ s.notes }}</p>
    </li>
  </ul>

  <section class="src__about">
    <h2>How these are read</h2>
    <p>
      Each source's README is parsed with a parser chosen from its declared formats — a source
      listing more than one is read with more than one. Formats are declared in
      <code>sources.json</code> rather than guessed, so a source using an unrecognised layout fails
      loudly instead of quietly contributing nothing.
    </p>
    <p>
      The formats in use are <code>bullet_separator</code>, <code>table_row</code>,
      <code>repo_relative</code>, <code>project_prose</code> and <code>html_details</code>.
    </p>
  </section>
</div>

<style scoped>
.src { max-width: 900px; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }
.src__hero h1 { font-size: 2.25rem; margin: 0 0 0.5rem; letter-spacing: -0.02em; }
.src__lede { color: var(--vp-c-text-2); max-width: 62ch; }
.src__stats { font-size: 0.9rem; color: var(--vp-c-text-3); }

.src__list { list-style: none; margin: 2rem 0 0; padding: 0; display: grid; gap: 0.75rem; }
.src__item {
  padding: 1rem 1.1rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
}
.src__head { display: flex; align-items: baseline; gap: 0.75rem; flex-wrap: wrap; }
.src__name { font-weight: 600; color: var(--vp-c-brand-1); text-decoration: none; }
.src__count { margin-left: auto; font-size: 0.82rem; color: var(--vp-c-text-3); }
.src__meta { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; margin-top: 0.4rem; }
.src__src { font-size: 0.78rem; color: var(--vp-c-text-3); text-decoration: none; }
.src__src:hover { color: var(--vp-c-brand-1); }
.src__fmt {
  font-size: 0.68rem; padding: 0.12rem 0.42rem; border-radius: 999px;
  border: 1px solid var(--vp-c-divider); color: var(--vp-c-text-3);
}
.src__notes { margin: 0.5rem 0 0; font-size: 0.82rem; color: var(--vp-c-text-3); line-height: 1.5; }

.src__about {
  margin-top: 3rem; padding-top: 1.75rem; border-top: 1px solid var(--vp-c-divider);
  max-width: 68ch; font-size: 0.92rem; color: var(--vp-c-text-2);
}
</style>