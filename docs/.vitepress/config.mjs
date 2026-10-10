import fs from 'node:fs'
import path from 'node:path'
import { defineConfig } from 'vitepress'

const SITE = 'https://awesome.rairahulr1.com'
// __dirname is docs/.vitepress (VitePress root is docs/), so entry pages are one level up.
const REPO_DOCS = path.resolve(__dirname, '..', 'repos')

// Minimal frontmatter reader — the format here is ours and deliberately flat, so this avoids
// pulling in a YAML dependency for four scalar keys and one inline array.
function parseFrontmatter(raw) {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (!m) return {}
  const fm = {}
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/)
    if (!kv) continue
    const [, key, rawValue] = kv
    let value = rawValue.trim()
    if (value.startsWith('[') && value.endsWith(']')) {
      fm[key] = value
        .slice(1, -1)
        .split(',')
        .map((s) => s.trim().replace(/^["']|["']$/g, ''))
        .filter(Boolean)
    } else if (/^-?\d+$/.test(value)) {
      fm[key] = Number(value)
    } else {
      fm[key] = value.replace(/^["']|["']$/g, '')
    }
  }
  return fm
}

// Read every entry page from disk. Doing this at config time (rather than via useData().pages)
// keeps it available during SSR, which useData().pages is not.
const repoFiles = fs.readdirSync(REPO_DOCS).filter((f) => f.endsWith('.md'))

// The generated repository index. This file is tracked, so its absence is a real error rather
// than a tolerable degraded state: building without it silently publishes an empty repository
// index that looks healthy and renders 200. Fail the build instead.
const ENTRIES_JSON = path.resolve(__dirname, '..', '..', 'data', 'entries.json')
if (!fs.existsSync(ENTRIES_JSON)) {
  throw new Error(
    `data/entries.json is missing. Run: python3 tools/extract_links.py\n` +
      `Refusing to build an empty repository index — a missing input must fail loudly.`,
  )
}
const parsedEntries = JSON.parse(fs.readFileSync(ENTRIES_JSON, 'utf8'))
const entryIndex = {
  generated_at: parsedEntries.generated_at ?? null,
  source_counts: parsedEntries.source_counts ?? {},
  unresolved: parsedEntries.unresolved ?? [],
  entries: parsedEntries.entries ?? [],
}
if (!entryIndex.entries.length) {
  throw new Error('data/entries.json contains no entries — refusing to publish an empty index.')
}

// Per-source entry counts, for display on the sources index.
const sourceMeta = (() => {
  const registryPath = path.resolve(__dirname, '..', '..', 'sources.json')
  if (!fs.existsSync(registryPath)) return []
  const { sources } = JSON.parse(fs.readFileSync(registryPath, 'utf8'))
  return sources.map((s) => ({
    ...s,
    entryCount: entryIndex.source_counts[s.id] ?? 0,
    page: `/repos/${s.id}`,
  }))
})()

// Dedupe on canonical owner/repo so the same source can never be indexed twice.
const slugOf = (url) => url.replace(/^https?:\/\/(www\.)?github\.com\//i, '').replace(/\/+$/, '').toLowerCase()

const seen = new Set()
const repos = repoFiles
  .map((file) => {
    const slug = file.replace(/\.md$/, '')
    if (slug === 'index') return null
    const fm = parseFrontmatter(fs.readFileSync(path.join(REPO_DOCS, file), 'utf8'))
    if (!fm.url) return null
    const key = slugOf(fm.url)
    if (seen.has(key)) return null
    seen.add(key)
    return {
      slug,
      path: `/repos/${slug}`,
      title: fm.title ?? slug,
      url: fm.url,
      stars: fm.stars ?? 0,
      starsAsOf: fm.stars_as_of ?? null,
      type: fm.type ?? 'list',
      categories: fm.categories ?? [],
      tags: fm.tags ?? [],
      description: fm.description ?? '',
      license: fm.license ?? 'unspecified',
    }
  })
  .filter(Boolean)
  .sort((a, b) => b.stars - a.stars)

const repoSlugs = repos.map((r) => r.slug)

export default defineConfig({
  title: 'awesomes',
  description:
    'A searchable, deduplicated index of curated awesome GitHub repositories — original descriptions preserved, source links direct.',
  cleanUrls: true,
  lastUpdated: true,

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#0d1117' }],
    ['meta', { property: 'og:site_name', content: 'awesomes' }],
    ['meta', { property: 'og:image', content: `${SITE}/og.png` }],
    ['meta', { property: 'og:image:width', content: '1200' }],
    ['meta', { property: 'og:image:height', content: '630' }],
    ['meta', { name: 'twitter:image', content: `${SITE}/og.png` }],
  ],

  // SEO: every page gets canonical + Open Graph/Twitter tags from its own frontmatter.
  // Reddit reads og:* for its link preview, so this is what makes a shared link render.
  transformPageData(pageData) {
    const fm = pageData.frontmatter ?? {}
    const head = (fm.head ??= [])

    // Canonical is the *site* URL for this page — never the GitHub URL it points at.
    const slug = pageData.relativePath.replace(/(^|\/)index\.md$/, '$1').replace(/\.md$/, '')
    const canonical = `${SITE}/${slug}`.replace(/\/$/, '/')
    const title = fm.title ? `${fm.title} · awesomes` : 'awesomes'
    const description = fm.description ?? 'A searchable index of curated awesome GitHub repositories.'

    head.push(['link', { rel: 'canonical', href: canonical }])
    head.push(['meta', { name: 'description', content: description }])
    head.push(['meta', { property: 'og:type', content: 'article' }])
    head.push(['meta', { property: 'og:title', content: title }])
    head.push(['meta', { property: 'og:description', content: description }])
    head.push(['meta', { property: 'og:url', content: canonical }])
    head.push(['meta', { name: 'twitter:card', content: 'summary' }])
    head.push(['meta', { name: 'twitter:title', content: title }])
    head.push(['meta', { name: 'twitter:description', content: description }])

    if (fm.url && fm.stars != null) {
      head.push([
        'script',
        { type: 'application/ld+json' },
        JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'SoftwareSourceCode',
          name: fm.title,
          description,
          codeRepository: fm.url,
          ...(fm.license ? { license: fm.license } : {}),
          ...(fm.stars != null ? { interactionStatistic: { '@type': 'InteractionCounter', interactionType: 'https://schema.org/LikeAction', userInteractionCount: fm.stars } } : {}),
        }),
      ])
    }
  },

  themeConfig: {
    // Consumed by the index pages via useData().theme — available during SSR.
    repos,
    sources: sourceMeta,
    entryIndex,
    nav: [
      { text: 'Index', link: '/' },
      { text: 'Sources', link: '/sources/' },
      { text: 'Repositories', link: '/repositories/' },
    ],
    sidebar: {
      '/repos/': [
        {
          text: 'Indexed lists',
          items: repoSlugs.map((s) => ({ text: s, link: `/repos/${s}` })),
        },
      ],
    },
    search: {
      provider: 'local',
      options: {
        detailedView: true,
      },
    },
    outline: 'deep',
    socialLinks: [{ icon: 'github', link: 'https://github.com/rairahulr1/awesomes' }],
    editLink: {
      pattern: 'https://github.com/rairahulr1/awesomes/edit/main/docs/:path',
      text: 'Suggest an edit to this entry',
    },
    footer: {
      message: 'Source lists are credited and linked; original descriptions are preserved verbatim.',
      copyright: 'awesomes',
    },
  },
})