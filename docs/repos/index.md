---
title: All indexed lists
description: Every awesome list tracked in this index, sorted by GitHub stars.
---

<script setup>
import { useData } from 'vitepress'

// Resolved at config time and passed through themeConfig — useData().pages is empty during SSR.
// `theme` is a Ref, hence `.value`.
const rows = useData().theme.value.repos

const fmt = (n) => (n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k` : String(n ?? '—'))
</script>

<table class="all-repos">
  <thead>
    <tr><th>List</th><th>Type</th><th>Categories</th><th>Licence</th><th>Stars</th></tr>
  </thead>
  <tbody>
    <tr v-for="r in rows" :key="r.url">
      <td><a :href="r.path">{{ r.title }}</a></td>
      <td>{{ r.type }}</td>
      <td>{{ (r.categories || []).join(', ') }}</td>
      <td>{{ r.license }}</td>
      <td>{{ fmt(r.stars) }}</td>
    </tr>
  </tbody>
</table>

<style scoped>
.all-repos { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.all-repos th { text-align: left; border-bottom: 1px solid var(--vp-c-divider); padding: 0.5rem 0.6rem; }
.all-repos td { padding: 0.55rem 0.6rem; border-bottom: 1px solid var(--vp-c-divider); vertical-align: top; }
</style>