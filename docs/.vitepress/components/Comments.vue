<script setup>
import { onMounted, ref } from 'vue'

const host = ref(null)

onMounted(() => {
  const s = document.createElement('script')
  s.src = 'https://utteranc.es/client.js'
  s.setAttribute('repo', 'rairahulr1/awesomes')
  // One GitHub issue per page path, so each repo entry gets its own thread.
  s.setAttribute('issue-term', 'pathname')
  s.setAttribute('theme', 'preferred-color-scheme')
  s.setAttribute('crossorigin', 'anonymous')
  s.async = true
  host.value.appendChild(s)
})
</script>

<template>
  <section class="comments">
    <h2>Comments</h2>
    <p class="comments__hint">
      Comments open in a GitHub Issue on
      <a href="https://github.com/rairahulr1/awesomes/issues" target="_blank" rel="noopener">rairahulr1/awesomes</a>.
      First comment on this page creates its thread.
    </p>
    <div ref="host" />
  </section>
</template>

<style scoped>
.comments {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--vp-c-divider);
}
.comments__hint {
  font-size: 0.875rem;
  color: var(--vp-c-text-2);
}
</style>