import { defineConfig } from 'vitepress'
import { defaultTheme } from 'vitepress'

export default defineConfig({
  title: 'awesome - curated repo index',
  description: 'A curated index of awesome GitHub repos organized by category',
  lastUpdated: true,
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Repos', link: '/repos/' },
      { text: 'Search', link: '/search/' },
    ],
    sidebar: {
      '/repos/': [
        {
          text: 'Awesome Repos',
          items: [
            { text: 'awesome-opencode', link: 'awesome-opencode' },
            { text: 'awesome-php', link: 'awesome-php' },
            { text: 'awesome-laravel', link: 'awesome-laravel' },
            { text: 'awesome-llm-apps', link: 'awesome-llm-apps' },
            { text: 'awesome-mcp-servers', link: 'awesome-mcp-servers' },
            { text: 'awesome-ai-engineering', link: 'awesome-ai-engineering' },
            { text: 'awesome-ai-agents', link: 'awesome-ai-agents' },
            { text: 'awesome-claude-skills', link: 'awesome-claude-skills' },
            { text: 'awesome-ai-apps', link: 'awesome-ai-apps' },
            { text: 'awesome-ai-tools', link: 'awesome-ai-tools' },
          ],
        },
      ],
    },
    search: {
      provider: 'local',
    },
    outline: 'deep',
    docFooter: {
      prev: 'Previous page',
      next: 'Next page',
    },
    lastUpdated: {
      text: 'Last updated',
      format: date => `Last updated on ${date}`,
    },
  },
  cleanUrls: true,
})