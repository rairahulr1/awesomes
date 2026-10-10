---
title: awesome-claude-skills
url: https://github.com/ComposioHQ/awesome-claude-skills
stars: 76700
stars_as_of: 2026-10-09
stars_source: github-repo-page-badge
type: skills
categories: [ai, skills, agents, mcp]
tags: [agent-skills, claude, claude-code, codex, cursor, gemini-cli, mcp, automation, saas]
description: A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows
license: Apache-2.0
---

# awesome-claude-skills

> A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows.

**Source:** [github.com/ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
· ★ 76.7k · Apache-2.0 · the only 77-commit repo in this index with 1.5k open PRs

## What a skill is (from the source)

Claude Skills are reusable instruction packages that teach an agent how to handle a class of tasks.
Each skill is a folder with a `SKILL.md` (YAML frontmatter + markdown), optionally bundled with
scripts, references and assets. Anthropic introduced the format in October 2025 and open-sourced it
in December 2025; it now works across Claude Code, Claude.ai, the Claude API, OpenAI Codex, Cursor,
Gemini CLI, Antigravity and Windsurf.

Skills load **progressively**: at session start the agent sees only each skill's name and
description (~100 tokens each). The body loads only when the agent judges it relevant. That is what
lets one agent host hundreds of skills without blowing its context window.

Skills are not MCP servers and not tools. MCP handles connection (auth, transport, discovery),
tools are the individual functions invoked, skills define the workflow and guardrails. In
production all three layers run together.

## What's inside

- **Document processing** — Anthropic's own `docx`, `pdf`, `pptx`, `xlsx` skills; Markdown→EPUB; a legal-team skill pack (NDA triage, multi-party diff, citation verifier) built from Anthropic's public webinar dataset
- **Development & code tools** — artifacts-builder, AWS CDK skills, blog generator (Next.js + Sanity, SEO/i18n intake → spec → generator), changelog generator, Chrome Relay (drives your *real* logged-in Chrome, not Playwright), terminal titles, D3.js viz, FFUF fuzzing, `finishing-a-development-branch`, full-page screenshot, `great_cto` (7 subagents, 11 archetypes, 13 compliance frameworks), iOS Simulator, Jules delegation, LangSmith fetch, `lean-ctx` (90+ shell patterns, token reduction), MCP builder, code-quality checks, OpenWeb (calls sites' own APIs — 90+ sites), Playwright automation, prompt engineering, PICT combinatorial testing, reddit-fetch (works around WebFetch 403s), subagent-driven development, test-driven development, git worktrees, webapp testing
- **Data & analysis** — CSV summariser, deep research (Gemini DR agent), read-only Postgres with multi-connection + defence in depth, recursive PhD-level research with disk checkpoints, root-cause tracing
- **Business & marketing** — 59-skill brand library with an Ahrefs SEO audit suite, Anthropic brand guidelines, competitive ads extractor, domain name brainstormer, internal comms (3P updates, newsletters, FAQs), lead research assistant
- **Communication & writing** — article extractor, brainstorming, content research writer, family-history research, meeting insight analyser (conflict avoidance, speaking ratios, filler words), NotebookLM integration, Twitter algorithm optimiser
- **Creative & media** — design-system extractor (`design.md` portable to v0/Lovable/Cursor), canvas design, Imagen, image enhancer, Slack GIF creator, theme factory (10 presets), video downloader, YouTube transcript, SwiftUI design skill (anti-AI-slop rules, supports Claude Code/Cursor/Codex/OpenCode), Pixelbin media generation
- **Productivity & organisation** — file organiser (finds duplicates), invoice organiser, kaizen, n8n skills, raffle picker (CSPRNG), solo-skills (EN+中文, explicit "when NOT to use" sections), tailored resume generator, ship-learn-next, tapestry (documents → knowledge networks)
- **Collaboration & project management** — git-pushing, Google Workspace (Gmail/Calendar/Docs/Sheets/Slides/Drive), Mercury/Proton team cheatsheet, Outline, review-implementing, test-fixing, computer forensics (metadata extraction, file deletion), Sigma threat hunting
- **Security & systems** — computer forensics skills, threat hunting with Sigma rules
- **Assistive technology** — ASD/AuDHD/PAI skills, including persistent-demand-avoidance reframing
- **App automation via Composio (Rube MCP)** — pre-built workflow skills for **78 SaaS apps**, each with tool sequences, parameter guidance and known pitfalls
  - CRM & sales: Close, HubSpot, Pipedrive, Salesforce, Zoho
  - Project management: Asana, Basecamp, ClickUp, Jira, Linear, Monday, Notion, Todoist, Trello, Wrike
  - Communication: Discord, Intercom, Microsoft Teams, Slack, Telegram, WhatsApp
  - Email: Gmail, Outlook, Postmark, SendGrid
  - Code & DevOps: Bitbucket, CircleCI, Datadog, GitHub, GitLab, PagerDuty, Render, Sentry, Supabase, Vercel
  - Storage & files: Box, Dropbox, Google Drive, OneDrive
  - Spreadsheets & databases: Airtable, Coda

## Notes

- This is commercially motivated — the repo is the funnel for Composio's MCP Gateway. The skills
  themselves are genuine; the "give your skills real-world actions" section is the pitch.
- `connect-apps` is the load-bearing plugin: everything in the automation section depends on it.

<Comments />