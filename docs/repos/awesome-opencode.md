---
title: awesome-opencode
url: https://github.com/awesome-opencode/awesome-opencode
stars: 10533
stars_as_of: 2026-10-10
stars_source: github-rest-api
type: plugins
categories: [ai, agents, devtools]
tags: [opencode, plugins, themes, agents, projects, resources, awesome-opencode]
description: A curated list of plugins, themes, agents, projects, and resources for OpenCode.
license: CC0-1.0
---

# awesome-opencode

> A curated list of plugins, themes, agents, projects, and resources for OpenCode — the AI coding
> agent for the terminal, built by the team at Anomaly.

**Source:** [github.com/awesome-opencode/awesome-opencode](https://github.com/awesome-opencode/awesome-opencode)
· ★ 10.5k · CC0-1.0 · 504 commits · 961 forks

CC0 is the right licence for a list like this — no attribution friction when you fork it.

## What's inside

- **Official repositories** — `opencode` plus official JS/TS, Go and Python SDKs
- **Plugins** — the bulk of the list, and the reason to bookmark this. Notable clusters:
  - *Context & memory* — Harness Memory (claims 73% fewer tokens than CLAUDE.md, with human review), Honcho, oc-mnemoria (shared hive-mind memory across agents), OpenCode Claude Memory, kibi-opencode (repo-local, branch-scoped knowledge), Lemma, AEIOU, oc-mnemoria
  - *Auth providers* — Antigravity (models + multi-account), Gemini, OpenAI Codex (ChatGPT Plus/Pro OAuth), OmniRoute, Kilo Gateway, VS Code Copilot
  - *Workflow & orchestration* — CrewBee (task-specific agent teams), OpenCode Ensemble (parallel teams), Open Conclave (multi-agent debate to consensus), Open Dynamic Workflows, Multi-Model Pipeline, FlowDeck, FRP
  - *Token optimisation* — Dynamic Context Pruning, Context Analysis, Magic Context, Harnage, lnk
  - *Safety* — CC Safety Net (catches destructive commands)
  - *Task runners & automation* — Ralph Loop, ForLoop Planner, Background, Sweep, Graveyard, OpenSpec, oh-my-opencode, ralph
  - *Skills & memory management* — Agent Skills (JDT dynamic loader), Manage Skills, OMC, Skill (dee), Skills Manager, Schemer, Tutti, ic
  - *GitHub & release automation* — GitHub Release, Phased PRs
  - *Session hygiene* — Backroll, Clippy, Log Sanitizer, OpenPlan Annotator, MimeType Guard, Wild, Punch
  - *Analysis* — Sweep, Prompt Tracer, Coitus, Crawlberg
  - *UI* — OpenCanvas, OpenTui, Agent Deck, Card, OpenCode Monitor, Open Console, VS Code, LiteLLM, Checkpoint, Devcontainers, Spectre, Hydra, Agent Deck
  - *Integrations* — Composio, Google Search, Exa, Chrome DevTools, Figma, ccusage, Zeabur, Fathom, Hypux, Parallel, autoflake, Playwright MCP, Task Master, oh-my-opencode
  - *Misc* — Directory as Project, Effortless, Opencode Go, Opencode Wise, Plugin Indexer, OpenHub, Slidev, Context Engine, Context Engine Lite, Onboard, Infinite, oHMyPi, Baseband, OMO
- **Themes** — Kanagawa, Catppuccin, Tokyo Night, Everforest, Ayu, One Dark, Gruvbox, Nord, Vitesse Dark
- **Agents** — sub-agents for sub-tasks, each with its own context window
- **Projects** — end-to-end apps built with OpenCode
- **Resources** — documentation and learning material

## Notes

- **Plugin quality is highly uneven.** The list is community-submitted with 413 open PRs; several
  entries duplicate a badge URL (`plugin-indexer`, `crawlberg`, `html-to-markdown` share one
  shields.io path), which suggests a copying error in the source README rather than three
  distinct plugins.
- Some entries are thinly described. "Fast, lossless HTML to Markdown conversion" tells you
  nothing about maintenance or licensing.
- Plugin *names* frequently shadow official features (auth, memory, context). Check the official
  docs before assuming a plugin is needed.

<Comments />