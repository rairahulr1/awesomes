<script setup>
import { computed, ref } from 'vue'
import { useData } from 'vitepress'

// The entry list is resolved at config time and handed over through themeConfig, because
// useData().pages is empty during SSR and a static index page must render at build time.
// `theme` is a Ref, hence `.value`.
const repos = useData().theme.value.repos

const types = computed(() => [...new Set(repos.map((r) => r.type))].sort())
const cats = computed(() => [...new Set(repos.flatMap((r) => r.categories))].sort())

const q = ref('')
const cat = ref('all')
const type = ref('all')

const filtered = computed(() => {
  const needle = q.value.trim().toLowerCase()
  return repos.filter((r) => {
    if (cat.value !== 'all' && !r.categories.includes(cat.value)) return false
    if (type.value !== 'all' && r.type !== type.value) return false
    if (!needle) return true
    return [r.title, r.description, r.license, ...r.categories, ...r.tags]
      .join(' ')
      .toLowerCase()
      .includes(needle)
  })
})

const fmtStars = (n) =>
  n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k` : String(n)

function reset() {
  q.value = ''
  cat.value = 'all'
  type.value = 'all'
}
</script>

<template>
  <div class="idx">
    <header class="idx__hero">
      <h1>awesomes</h1>
      <p class="idx__lede">
        A searchable, deduplicated index of curated <strong>awesome</strong> lists on GitHub.
        Original descriptions are preserved verbatim; every entry links straight to its source.
      </p>
      <p class="idx__stats">
        <strong>{{ repos.length }}</strong> indexed · deduplicated on canonical owner/repo
      </p>
    </header>

    <div class="idx__controls">
      <input
        v-model="q"
        class="idx__search"
        type="search"
        placeholder="Search titles, descriptions, tags, licences…"
        aria-label="Search indexed lists"
      />
      <select v-model="cat" aria-label="Filter by category">
        <option value="all">All categories</option>
        <option v-for="c in cats" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="type" aria-label="Filter by type">
        <option value="all">All types</option>
        <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
      </select>
    </div>

    <p class="idx__resultcount">
      {{ filtered.length }} of {{ repos.length }} shown · sorted by stars
    </p>

    <ul class="idx__grid">
      <li v-for="r in filtered" :key="r.url" class="card">
        <a class="card__title" :href="r.path">{{ r.title }}</a>
        <span class="card__stars" :title="r.starsAsOf ? `stars as of ${r.starsAsOf}` : 'stars'">
          ★ {{ fmtStars(r.stars) }}
        </span>
        <p class="card__desc">{{ r.description }}</p>
        <div class="card__meta">
          <span class="chip chip--type">{{ r.type }}</span>
          <span v-for="c in r.categories" :key="c" class="chip">{{ c }}</span>
          <span class="card__licence">{{ r.license }}</span>
        </div>
        <a class="card__src" :href="r.url" target="_blank" rel="noopener">source ↗</a>
      </li>
    </ul>

    <p v-if="!filtered.length" class="idx__empty">
      Nothing matches. <button class="idx__reset" @click="reset">Clear filters</button>
    </p>

    <section class="idx__about">
      <h2>About this index</h2>
      <p>
        These lists already exist on GitHub. This site indexes them: one page per list, the
        description exactly as the maintainer wrote it, a star count snapshotted from GitHub, and a
        link to the original. Nothing is mirrored.
      </p>
      <p>
        Each page carries its own comment thread. Star counts are point-in-time and will drift — the
        source link is authoritative.
      </p>
    </section>
  </div>
</template>

<style scoped>
.idx {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 1.25rem 4rem;
}
.idx__hero h1 {
  font-size: 2.5rem;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.idx__lede {
  font-size: 1.05rem;
  color: var(--vp-c-text-2);
  max-width: 60ch;
}
.idx__stats {
  font-size: 0.9rem;
  color: var(--vp-c-text-3);
}

.idx__controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin: 1.75rem 0 0.75rem;
}
.idx__search {
  flex: 1 1 320px;
  padding: 0.6rem 0.85rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font-size: 0.95rem;
}
.idx__controls select {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font-size: 0.9rem;
}

.idx__resultcount {
  font-size: 0.82rem;
  color: var(--vp-c-text-3);
  margin: 0 0 1rem;
}

.idx__grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 1rem;
}

.card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem 1.1rem 1.15rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
}
.card__title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--vp-c-brand-1);
  text-decoration: none;
}
.card__stars {
  position: absolute;
  top: 1rem;
  right: 1.1rem;
  font-size: 0.8rem;
  color: var(--vp-c-text-3);
}
.card__desc {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--vp-c-text-2);
}
.card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
}
.chip {
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-2);
}
.chip--type {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}
.card__licence {
  margin-left: auto;
  font-size: 0.72rem;
  color: var(--vp-c-text-3);
}
.card__src {
  font-size: 0.78rem;
  color: var(--vp-c-text-3);
  text-decoration: none;
}
.card__src:hover {
  color: var(--vp-c-brand-1);
}

.idx__empty {
  padding: 2rem 0;
  color: var(--vp-c-text-2);
}
.idx__reset {
  border: 1px solid var(--vp-c-divider);
  background: transparent;
  color: var(--vp-c-brand-1);
  border-radius: 6px;
  padding: 0.2rem 0.5rem;
  cursor: pointer;
}

.idx__about {
  margin-top: 3.5rem;
  padding-top: 2rem;
  border-top: 1px solid var(--vp-c-divider);
  max-width: 68ch;
  font-size: 0.92rem;
  color: var(--vp-c-text-2);
}
</style>