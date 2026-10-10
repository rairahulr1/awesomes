---
title: awesome-ai-apps
url: https://github.com/Arindam200/awesome-ai-apps
stars: 16098
stars_as_of: 2026-10-10
stars_source: github-rest-api
type: apps
categories: [ai, agents, rag, mcp]
tags: [agents, ai, hacktoberfest, llm, mcp, awesome-ai-apps]
description: A collection of projects showcasing RAG, agents, workflows, and other AI use cases
license: MIT
---

# awesome-ai-apps

> A collection of projects showcasing RAG, agents, workflows, and other AI use cases.

**Source:** [github.com/Arindam200/awesome-ai-apps](https://github.com/Arindam200/awesome-ai-apps)
· ★ 16.1k · MIT · 132 projects · three named maintainers

The most honest of the AI app lists: every entry is a real directory with a README and a
`requirements.txt`, not a link to a landing page. Overlaps heavily with `awesome-llm-apps` but is
smaller and more uniformly runnable.

## What's inside

- **Starter agents** (21 projects) — AutoGen tool-calling, AWS Strands, CAMEL benchmark, coding harness (plan → approval-gated edits → fixed tests → bounded review), CrewAI research crew, Docker cagent, DSPy optimisation, Google ADK, Hacker News trend analyst (Agno), Hugging Face smolagents, KAOS (Kubernetes-native multi-agent with MCP), LangChain tool-calling, LangGraph ReAct, Letta stateful memory, LlamaIndex task manager, Mastra, Microsoft Agent Framework, OpenAI Agents SDK, PydanticAI weather bot, realtime voice (Sayna), Semantic Kernel
- **Simple agents** (19) — Agno examples + UI, agent registry explorer (NANDA/MCP/Virtuals/A2A/ERC-8004), expense tracker, Cal.com calendar assistant, cost-aware router (RouteLLM), email-to-calendar, financial reasoning, human-in-the-loop, LangChain ops collection (incident/support/vendor risk/data quality), macro event briefs, Mastra weather, NL→DB (GibsonAI), NL→SQL with LangGraph, chat UI, newsletter generator (Firecrawl), stock market agent, portfolio analyst (Agno), travel planner, browser automation
- **Voice agents** (9) — pitch coach (Gradium), customer support (LiveKit), Gemini realtime (LiveKit), healthcare contact centre (Pipecat), multilingual (Pipecat + Sarvam), RSVP confirmation (outbound calling), speed-to-lead sales, VoxCode (Deepgram + Cursor SDK), web-search voice agent
- **MCP agents** (14) — Couchbase LangGraph agent, Couchbase MCP server, custom MCP server, docs Q&A, docs RAG server, GibsonAI database agent, GitHub MCP agent, GitHub repo analyser starter, hotel finder, sandboxed code execution (Docker + E2B), secure database agent (MCP Toolbox — per-user access, least-privilege roles), secure MCP access (ScaleKit + Exa), self-healing text-to-SQL (Okahu traces), Taskade MCP agent
- **Memory agents** (13) — AI consultant (Memori v3 + Exa), arXiv researcher (Memori), AWS Strands with memory, blog writer, brand reputation monitor, customer support (Memori + Firecrawl), engineering content agent (HN demand vs DEV.to supply, Weaviate Engram), job search agent, persistent memory (Agno), product launch agent, social media agent, study coach (multi-step verification), YouTube trend agent
- **RAG applications** (18) — agentic RAG (Agno + GPT-5), typed agentic RAG (LlamaIndex) with deterministic refusal on weak evidence, codebase Q&A, enterprise contextual RAG, Gemma 3 OCR, GraphRAG with Neo4j + Cypher, invoice auditor (OCR + bounding boxes + LLM math-error audit), LlamaIndex starter, WFGY 16-problem debugger, multi-PDF analyser, basic RAG starter, NVIDIA Nemotron OCR, production PDF RAG (Qdrand hybrid + reranking + streaming + clickable citations), Qwen3 PDF RAG, resume optimiser, trustworthy RAG (citation verification + hallucination scoring), video Q&A with timestamp citations, web-augmented agentic RAG
- **Advanced agents** (35) — AI hedge fund, trend research (Google ADK), candidate profile analyser, car finder, clinical early-warning (NEWS2/qSOFA), conference proposal/talk generators, contract review crew (CrewAI redlines), Cosmos arena debate council (LangGraph + NVIDIA Cosmos), support resolution, deep research + writing workshop, deep research workflow, due diligence (AG2 + TinyFish), financial document OS, financial market service (FastAPI), research agent (AgentField), GitHub/LinkedIn job finder (Bright Data), social research (Jev + local socai), local file-editing prototype, maintainer intelligence brief, meeting assistant, multi-agent coding harness (LangGraph + E2B sandbox), autonomous pipeline optimiser, pre-meeting intel (Tavily), price monitoring, prompt format benchmark (XML/JSON/Markdown), sandboxed browser game generator (PydanticAI + GLM-5.2), SEO content team (Agno + SerpAPI), shark-tank practice, software engineering model arena, go-to-market strategy, startup idea validator, Temporal agents, temporal transaction eval (OpenTelemetry + Okahu), web intelligence (Mastra + Olostep + Nemotron), workflow audit trail (Next.js + n8n + Velt)
- **Fine-tuning** (6) — customer support (Data Lab distillation), insurance claims (LoRA + Gradio), legal tech self-hosted (Gemma on UK legislation + vLLM + FastAPI), legal tech managed (Token Factory), open-source LoRA on Colab, standalone support fine-tuning
- **Tutorials & videos** — 8-lesson AWS Strands course, voice agents playlist, AI agents/MCP playlist, agent build playlist

## Notes

- Sponsor wall is heavy (Bright Data, Nebius, ScrapeGraphAI, Memori, CopilotKit, ScaleKit, Okahu,
  AgentField, Byteful) and many entries reference those vendors. Judge them as reference
  implementations rather than neutral recommendations.
- Requires Python 3.10+ (3.11+ for newer projects) and API keys for most projects — this is not a
  zero-config collection.

<Comments />