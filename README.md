# awesomes

A curated index of awesome GitHub repositories, organized by category for easy discovery and search.

**Live at:** [awesome.rairahulr1.com](https://awesome.rairahulr1.com)

This repository serves as a single source of awesome repos, with markdown entries for each repo that include:
- Title and GitHub link
- Star count
- Category classification
- Description summary
- Tag (repo name)
- SEO-friendly structure for Reddit sharing
- Comment section via Utterances

## 📁 Repository Structure

```
awesomes/
├── .github/workflows/deploy.yml    # GitHub Actions for auto-deploy
├── docs/
│   ├── .vitepress/config.mjs       # VitePress configuration
│   ├── index.md                    # Landing page with category grid
│   └── repos/                      # Individual repo entries
│       ├── awesome-opencode.md
│       ├── awesome-php.md
│       ├── awesome-laravel.md
│       ├── awesome-llm-apps.md
│       ├── awesome-mcp-servers.md
│       ├── awesome-ai-engineering.md
│       ├── awesome-ai-agents.md
│       ├── awesome-claude-skills.md
│       ├── awesome-ai-apps.md
│       └── awesome-ai-tools.md
└── README.md
```

## 🛠️ Adding a New Repo

1. Add a new markdown file in `docs/repos/` following the existing format
2. Include frontmatter with: `title`, `url`, `stars`, `category`, `tag`, `description`
3. Push — GitHub Actions will build and deploy automatically
4. Update the category grid in `docs/index.md` if needed

## 📦 Tech Stack

- **Static Site Generator:** [VitePress](https://vitepress.dev)
- **Hosting:** [GitHub Pages](https://pages.github.com) with custom domain `awesome.rairahulr1.com`
- **Search:** Built-in VitePress local search
- **Comments:** [Utterances](https://utterances.app/) (GitHub Issue-based)
- **CI/CD:** GitHub Actions auto-deploy on push to `main`

## 🏷️ Categories

| Category | Repos |
|----------|-------|
| **AI & LLM** | awesome-llm-apps, awesome-ai-engineering, awesome-ai-agents, awesome-claude-skills, awesome-ai-apps, awesome-ai-tools |
| **PHP** | awesome-php, awesome-laravel |
| **MCP** | awesome-mcp-servers |
| **Devtools** | awesome-opencode |

## 🔍 Search

Built-in VitePress local search indexes all repo titles, descriptions, and categories. Search is client-side, no backend required.

## 💬 Comments

Each repo page includes Utterances comments, tied to a GitHub Issue. The issue path is derived from the repo name, so discussions are per-repo.

## 🚀 Development

```bash
# Install dependencies
npm ci

# Run dev server
npm run dev

# Build for production
npm run build
```

## 📄 License

MIT License - see LICENSE file for details.