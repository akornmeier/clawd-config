# Skill Inventory

Generated: 2026-03-05  
Scanner: skill-scanner agent

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total SKILL.md files | 130 |
| Total lines of skill content | 82,224 |
| Unique skill names | 127 |
| Duplicate names across sources | 3 |
| Mirrored skills (claude-code-plugins = claude-plugins-official) | 9 |
| Skills with examples/code blocks | 128 |
| Skills with file references | 122 |
| Skills with allowed-tools declared | 13 |
| Template files (excluded) | 1 |

### Skills per Source

| Source | Count | Total Lines | Avg Lines |
|--------|-------|-------------|-----------|
| local | 9 | 1,603 | 178 |
| claude-skills | 93 | 69,702 | 749 |
| claude-code-plugins | 10 | 4,702 | 470 |
| claude-plugins-official | 14 | 5,707 | 407 |
| claude-plugins-official/external | 1 | 31 | 31 |
| mcp-use | 3 | 479 | 159 |
| **Total** | **130** | **82,224** | **632** |

---

## 1. Local Skills

**Path**: `~/.claude/skills/*/SKILL.md`  
**Note**: Some directories are symlinks (convex, convex-best-practices, find-skills, remotion-best-practices, shadcn-ui, simplify).

| # | Name | Description | Lines | Ex | Ref | Allowed Tools |
|---|------|-------------|-------|----|-----|---------------|
| 1 | **convex** | Umbrella skill for all Convex development patterns. Routes to specific skills li | 63 | n | n | - |
| 2 | **convex-best-practices** | Guidelines for building production-ready Convex apps covering function organizat | 370 | y | y | - |
| 3 | **Create New Skills** | Creates new Agent Skills for Claude Code following best practices and documentat | 438 | y | y | - |
| 4 | **create-worktree-skill** | Use when the user explicitly asks for a SKILL to create a worktree. If the user  | 103 | y | n | SlashCommand, Bash, Read, Write, Edit, Glob, Grep |
| 5 | **find-skills** | Helps users discover and install agent skills when they ask questions like "how  | 134 | y | y | - |
| 6 | **remotion-best-practices** | Best practices for Remotion - Video creation in React | 49 | y | y | - |
| 7 | **shadcn-ui** | Expert guidance for integrating and building applications with shadcn/ui compone | 327 | y | y | shadcn*:*, mcp_shadcn*, Read, Write, Bash, web_fetch |
| 8 | **simplify** | Review changed code for reuse, quality, and efficiency, then fix any issues foun | 39 | n | n | - |
| 9 | **worktree-manager-skill** | Comprehensive git worktree management. Use when the user wants to create, remove | 80 | y | y | SlashCommand, Bash, Read, Write, Edit, Glob, Grep |

---

## 2. Claude Skills Marketplace

**Path**: `~/.claude/plugins/marketplaces/claude-skills/skills/*/SKILL.md`  
**Count**: 93 skills | **Largest marketplace by far**

| # | Name | Description | Lines | Ex | Ref | Tools |
|---|------|-------------|-------|----|-----|-------|
| 1 | **accessibility** | Build WCAG 2.1 AA compliant websites with semantic HTML, proper ARIA, focus mana | 883 | y | y | - |
| 2 | **agent-development** | Design and build custom Claude Code agents with effective descriptions, tool acc | 332 | y | y | - |
| 3 | **ai-sdk-core** | Build backend AI with Vercel AI SDK v6 stable. Covers Output API (replaces gener | 1357 | y | y | - |
| 4 | **ai-sdk-ui** | Build React chat interfaces with Vercel AI SDK v6. Covers useChat/useCompletion/ | 558 | y | y | - |
| 5 | **auto-animate** | Zero-config animations for React, Vue, Solid, Svelte, Preact with @formkit/auto- | 355 | y | y | - |
| 6 | **azure-auth** | Microsoft Entra ID (Azure AD) authentication for React SPAs with MSAL.js and Clo | 623 | y | y | - |
| 7 | **better-auth** | Self-hosted auth for TypeScript/Cloudflare Workers with social auth, 2FA, passke | 2147 | y | y | y |
| 8 | **claude-agent-sdk** | Build autonomous AI agents with Claude Agent SDK. Structured outputs guarantee J | 955 | y | y | - |
| 9 | **claude-api** | Build with Claude Messages API using structured outputs for guaranteed JSON sche | 679 | y | n | - |
| 10 | **clerk-auth** | Clerk auth with API Keys beta (Dec 2025), Next.js 16 proxy.ts (March 2025 CVE co | 702 | y | y | - |
| 11 | **cloudflare-agents** | Build AI agents with Cloudflare Agents SDK on Workers + Durable Objects. Provide | 1688 | y | y | - |
| 12 | **cloudflare-browser-rendering** | Add headless Chrome automation with Puppeteer/Playwright on Cloudflare Workers.  | 877 | y | y | - |
| 13 | **cloudflare-d1** | Build with D1 serverless SQLite database on Cloudflare's edge. Use when: creatin | 734 | y | y | - |
| 14 | **cloudflare-durable-objects** | Build stateful Durable Objects for real-time apps, WebSocket servers, coordinati | 839 | y | y | - |
| 15 | **cloudflare-hyperdrive** | Connect Workers to PostgreSQL/MySQL with Hyperdrive's global pooling and caching | 815 | y | y | - |
| 16 | **cloudflare-images** | Store and transform images with Cloudflare Images API and transformations. Use w | 717 | y | y | - |
| 17 | **cloudflare-kv** | Store key-value data globally with Cloudflare KV's edge network. Use when: cachi | 589 | y | y | - |
| 18 | **cloudflare-mcp-server** | Build MCP servers on Cloudflare Workers - the only platform with official remote | 1284 | y | y | y |
| 19 | **cloudflare-python-workers** | Build Python APIs on Cloudflare Workers using pywrangler CLI and WorkerEntrypoin | 739 | y | y | - |
| 20 | **cloudflare-queues** | Build async message queues with Cloudflare Queues for background processing. Use | 937 | y | y | - |
| 21 | **cloudflare-r2** | Store objects with R2's S3-compatible storage on Cloudflare's edge. Use when: up | 683 | y | y | - |
| 22 | **cloudflare-turnstile** | Add bot protection with Turnstile (CAPTCHA alternative). Use when: protecting fo | 539 | y | y | - |
| 23 | **cloudflare-vectorize** | Build semantic search with Cloudflare Vectorize V2. Covers async mutations, 5M v | 744 | y | y | - |
| 24 | **cloudflare-worker-base** | Set up Cloudflare Workers with Hono routing, Vite plugin, and Static Assets. Pre | 417 | y | y | - |
| 25 | **cloudflare-workers-ai** | Run LLMs and AI models on Cloudflare's GPU network with Workers AI. Includes Lla | 579 | y | y | - |
| 26 | **cloudflare-workflows** | Build durable workflows with Cloudflare Workflows (GA April 2025). Features step | 868 | y | y | - |
| 27 | **color-palette** | Generate complete, accessible color palettes from a single brand hex. Creates 11 | 275 | y | y | - |
| 28 | **developer-toolbox** | Essential development workflow agents for code review, debugging, testing, docum | 148 | y | y | - |
| 29 | **django-cloud-sql-postgres** | Deploy Django on Google App Engine Standard with Cloud SQL PostgreSQL. Covers Un | 922 | y | y | - |
| 30 | **docs-workflow** | Four slash commands for documentation lifecycle: /docs, /docs-init, /docs-update | 203 | y | y | - |
| 31 | **drizzle-orm-d1** | Build type-safe D1 databases with Drizzle ORM. Includes schema definition, migra | 756 | y | y | - |
| 32 | **elevenlabs-agents** | Build conversational AI voice agents with ElevenLabs Platform. Configure agents, | 1165 | y | y | - |
| 33 | **email-gateway** | Multi-provider email sending for Cloudflare Workers and Node.js applications. | 1405 | y | y | - |
| 34 | **fastapi** | Build Python APIs with FastAPI, Pydantic v2, and SQLAlchemy 2.0 async. Covers pr | 960 | y | y | - |
| 35 | **fastmcp** | Build MCP servers in Python with FastMCP to expose tools, resources, and prompts | 897 | y | y | - |
| 36 | **favicon-gen** | Generate custom favicons from logos, text, or brand colors - prevents launching  | 615 | y | y | - |
| 37 | **firebase-auth** | Build with Firebase Authentication - email/password, OAuth providers, phone auth | 735 | y | y | - |
| 38 | **firebase-firestore** | Build with Firestore NoSQL database - real-time sync, offline support, and scala | 732 | y | y | - |
| 39 | **firebase-storage** | Build with Firebase Cloud Storage - file uploads, downloads, and secure access.  | 794 | y | y | - |
| 40 | **firecrawl-scraper** | Convert websites into LLM-ready data with Firecrawl API. Features: scrape, crawl | 937 | y | y | - |
| 41 | **flask** | Build Python web apps with Flask using application factory pattern, Blueprints,  | 854 | y | y | - |
| 42 | **google-app-engine** | Deploy Python applications to Google App Engine Standard/Flexible. Covers app.ya | 638 | y | y | - |
| 43 | **google-chat-api** | Build Google Chat bots and webhooks with Cards v2, interactive forms, and Cloudf | 943 | y | y | - |
| 44 | **google-gemini-api** | Integrate Gemini API with @google/genai SDK (NOT deprecated @google/generative-a | 2601 | y | y | - |
| 45 | **google-gemini-embeddings** | Build RAG systems and semantic search with Gemini embeddings (gemini-embedding-0 | 932 | y | y | - |
| 46 | **google-gemini-file-search** | Build document Q&A with Gemini File Search - fully managed RAG with automatic ch | 1257 | y | y | y |
| 47 | **google-spaces-updates** | Post team updates to Google Chat Spaces via webhook. Deployment notifications, b | 242 | y | y | - |
| 48 | **google-workspace** | Build integrations with Google Workspace APIs (Gmail, Calendar, Drive, Sheets, D | 386 | y | y | - |
| 49 | **hono-routing** | Build type-safe APIs with Hono for Cloudflare Workers, Deno, Bun, Node.js. Routi | 1423 | y | y | - |
| 50 | **icon-design** | Select semantically appropriate icons for websites using Lucide, Heroicons, or P | 114 | y | y | - |
| 51 | **image-gen** | Generate website images with Gemini 3 Native Image Generation. Covers hero banne | 245 | y | y | - |
| 52 | **jquery-4** | Migrate jQuery 3.x to 4.0.0 safely in WordPress and legacy web projects. Covers  | 502 | y | y | - |
| 53 | **MCP OAuth Cloudflare** | Add OAuth authentication to MCP servers on Cloudflare Workers. Uses @cloudflare/ | 897 | y | y | - |
| 54 | **mcp-cli-scripts** | Build CLI scripts alongside MCP servers for terminal environments. File I/O, bat | 257 | y | y | - |
| 55 | **motion** | Build React animations with Motion (Framer Motion) - gestures (drag, hover, tap) | 856 | y | y | - |
| 56 | **neon-vercel-postgres** | Set up serverless Postgres with Neon or Vercel Postgres for Cloudflare Workers/E | 1181 | y | y | - |
| 57 | **nextjs** | Build Next.js 16 apps with App Router, Server Components/Actions, Cache Componen | 1746 | y | y | y |
| 58 | **oauth-integrations** | Implement OAuth 2.0 authentication with GitHub and Microsoft Entra (Azure AD) in | 170 | y | y | - |
| 59 | **office** | Generate Office documents (DOCX, XLSX, PDF, PPTX) with TypeScript. Pure JS libra | 903 | y | y | - |
| 60 | **open-source-contributions** | Create maintainer-friendly pull requests with clean code and professional commun | 458 | y | y | - |
| 61 | **OpenAI Apps MCP** | Build ChatGPT apps with MCP servers on Cloudflare Workers. Extend ChatGPT with c | 510 | y | y | y |
| 62 | **openai-agents** | Build AI applications with OpenAI Agents SDK - text agents, voice agents, multi- | 443 | y | y | - |
| 63 | **openai-api** | Build with OpenAI stateless APIs - Chat Completions (GPT-5.2, o3), Realtime voic | 1138 | y | y | - |
| 64 | **openai-assistants** | Build stateful chatbots with OpenAI Assistants API v2 - Code Interpreter, File S | 410 | y | y | - |
| 65 | **openai-responses** | Build agentic AI with OpenAI Responses API - stateful conversations with preserv | 548 | y | y | - |
| 66 | **playwright-local** | Build browser automation and web scraping with Playwright on your local machine. | 1343 | y | y | - |
| 67 | **project-planning** | Generate structured planning docs for web projects with context-safe phases, ver | 1123 | y | y | - |
| 68 | **project-session-management** | Track progress across sessions using SESSION.md with git checkpoints and concret | 244 | y | y | - |
| 69 | **project-workflow** | Nine integrated slash commands for complete project lifecycle: /explore-idea, /p | 259 | y | y | - |
| 70 | **react-hook-form-zod** | Build type-safe validated forms using React Hook Form v7 and Zod v4. Single sche | 413 | y | y | - |
| 71 | **react-native-expo** | Build React Native 0.76+ apps with Expo SDK 52-54. Covers mandatory New Architec | 1078 | y | y | - |
| 72 | **responsive-images** | Implement performant responsive images with srcset, sizes, lazy loading, and mod | 413 | y | n | - |
| 73 | **seo-meta** | Generate complete SEO meta tags for every page. Covers title patterns, meta desc | 488 | y | n | - |
| 74 | **skill-creator** | Design effective Claude Code skills with optimal descriptions, progressive discl | 361 | y | y | - |
| 75 | **skill-review** | Audit claude-skills with systematic 9-phase review: standards compliance, offici | 109 | y | y | y |
| 76 | **snowflake-platform** | Build on Snowflake's AI Data Cloud with snow CLI, Cortex AI (COMPLETE, SUMMARIZE | 823 | y | y | - |
| 77 | **streamlit-snowflake** | Build and deploy Streamlit apps natively in Snowflake. Covers snowflake.yml scaf | 393 | y | y | - |
| 78 | **sub-agent-patterns** | Comprehensive guide to sub-agents in Claude Code: built-in agents (Explore, Plan | 1089 | y | y | - |
| 79 | **sveltia-cms** | Set up Sveltia CMS - lightweight Git-backed CMS successor to Decap/Netlify CMS ( | 992 | y | y | y |
| 80 | **tailwind-patterns** | Production-ready Tailwind CSS patterns for common website components: responsive | 509 | y | y | - |
| 81 | **tailwind-v4-shadcn** | Set up Tailwind v4 with shadcn/ui using @theme inline pattern and CSS variable a | 666 | y | y | - |
| 82 | **TanStack Router** | Build type-safe, file-based React routing with TanStack Router. Supports client- | 664 | y | y | - |
| 83 | **TanStack Start** | Build full-stack React apps with TanStack Start on Cloudflare Workers. Type-safe | 782 | y | y | y |
| 84 | **TanStack Table** | Build headless data tables with TanStack Table v8. Server-side pagination, filte | 574 | y | y | - |
| 85 | **tanstack-query** | Manage server state in React with TanStack Query v5. Covers useMutationState, si | 1059 | y | y | - |
| 86 | **tinacms** | Build content-heavy sites with Git-backed TinaCMS. Provides visual editing for b | 623 | y | y | y |
| 87 | **tiptap** | Build rich text editors with Tiptap - headless editor framework with React and T | 693 | y | y | - |
| 88 | **ts-agent-sdk** | Generate typed TypeScript SDKs for AI agents to interact with MCP servers. Conve | 197 | y | y | - |
| 89 | **typescript-mcp** | Build MCP servers with TypeScript on Cloudflare Workers. Covers tools, resources | 632 | y | y | y |
| 90 | **vercel-blob** | Integrate Vercel Blob for file uploads and CDN-delivered assets in Next.js. Supp | 368 | y | y | - |
| 91 | **vercel-kv** | Integrate Redis-compatible Vercel KV for caching, session management, and rate l | 416 | y | y | - |
| 92 | **wordpress-plugin-core** | Build secure WordPress plugins with hooks, database interactions, Settings API,  | 1090 | y | y | - |
| 93 | **zustand-state-management** | Build type-safe global state in React with Zustand. Supports TypeScript, persist | 463 | y | y | - |

---

## 3. Claude Code Plugins Marketplace

**Path**: `~/.claude/plugins/marketplaces/claude-code-plugins/plugins/*/skills/*/SKILL.md`

| # | Name | Plugin | Description | Lines | Ex | Ref |
|---|------|--------|-------------|-------|----|-----|
| 1 | **Agent Development** | plugin-dev | This skill should be used when the user asks to "create an agent" | 416 | y | y |
| 2 | **claude-opus-4-5-migration** | claude-opus-4-5-migration | Migrate prompts and code from Claude Sonnet 4.0, Sonnet 4.5, or O | 106 | y | y |
| 3 | **Command Development** | plugin-dev | This skill should be used when the user asks to "create a slash c | 835 | y | y |
| 4 | **frontend-design** | frontend-design | Create distinctive, production-grade frontend interfaces with hig | 42 | y | n |
| 5 | **Hook Development** | plugin-dev | This skill should be used when the user asks to "create a hook",  | 713 | y | y |
| 6 | **MCP Integration** | plugin-dev | This skill should be used when the user asks to "add MCP server", | 555 | y | y |
| 7 | **Plugin Settings** | plugin-dev | This skill should be used when the user asks about "plugin settin | 545 | y | y |
| 8 | **Plugin Structure** | plugin-dev | This skill should be used when the user asks to "create a plugin" | 477 | y | y |
| 9 | **Skill Development** | plugin-dev | This skill should be used when the user wants to "create a skill" | 638 | y | y |
| 10 | **Writing Hookify Rules** | hookify | This skill should be used when the user asks to "create a hookify | 375 | y | y |

---

## 4. Claude Plugins Official Marketplace

**Path**: `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/*/skills/*/SKILL.md`

| # | Name | Plugin | Description | Lines | Ex | Ref |
|---|------|--------|-------------|-------|----|-----|
| 1 | **agent-development** | plugin-dev | This skill should be used when the user asks to "create an agent" | 416 | y | y |
| 2 | **claude-automation-recommender** | claude-code-setup | Analyze a codebase and recommend Claude Code automations (hooks,  | 289 | y | y |
| 3 | **claude-md-improver** | claude-md-management | Audit and improve CLAUDE.md files in repositories. Use when user  | 180 | y | y |
| 4 | **command-development** | plugin-dev | This skill should be used when the user asks to "create a slash c | 835 | y | y |
| 5 | **example-skill** | example-plugin | This skill should be used when the user asks to "demonstrate skil | 85 | y | y |
| 6 | **frontend-design** | frontend-design | Create distinctive, production-grade frontend interfaces with hig | 42 | y | n |
| 7 | **hook-development** | plugin-dev | This skill should be used when the user asks to "create a hook",  | 713 | y | y |
| 8 | **mcp-integration** | plugin-dev | This skill should be used when the user asks to "add MCP server", | 555 | y | y |
| 9 | **playground** | playground | Creates interactive HTML playgrounds — self-contained single-file | 77 | y | y |
| 10 | **plugin-settings** | plugin-dev | This skill should be used when the user asks about "plugin settin | 545 | y | y |
| 11 | **plugin-structure** | plugin-dev | This skill should be used when the user asks to "create a plugin" | 477 | y | y |
| 12 | **skill-creator** | skill-creator | Create new skills, modify and improve existing skills, and measur | 480 | y | y |
| 13 | **skill-development** | plugin-dev | This skill should be used when the user wants to "create a skill" | 638 | y | y |
| 14 | **writing-hookify-rules** | hookify | This skill should be used when the user asks to "create a hookify | 375 | y | y |

### External Plugins

**Path**: `~/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/*/skills/*/SKILL.md`

| # | Name | Plugin | Description | Lines | Ex | Ref |
|---|------|--------|-------------|-------|----|-----|
| 1 | **stripe-best-practices** | stripe | Best practices for building Stripe integrations. Use when impleme | 31 | y | y |

---

## 5. MCP-Use Marketplace

**Path**: `~/.claude/plugins/marketplaces/mcp-use/skills/*/SKILL.md`

| # | Name | Description | Lines | Ex | Ref |
|---|------|-------------|-------|----|-----|
| 1 | **chatgpt-app-builder** | DEPRECATED: This skill has been replaced by `mcp-app-builder`. | 56 | y | y |
| 2 | **mcp-apps-builder** | **MANDATORY for ALL MCP server work** - mcp-use framework best practices and pat | 352 | y | y |
| 3 | **mcp-builder** | DEPRECATED: This skill has been replaced by `mcp-app-builder`. | 71 | y | y |

---

## 6. Superpowers Marketplace

**Path**: `~/.claude/plugins/marketplaces/superpowers-marketplace/`  
No SKILL.md files found in this marketplace.

---

## Duplicates and Overlaps

### Mirrored Skills (Identical Content)

The following skills exist in both `claude-code-plugins` and `claude-plugins-official` with identical line counts,
indicating they are the same content maintained in two repositories:

| Skill Name | Lines | In claude-code-plugins | In claude-plugins-official |
|------------|-------|------------------------|---------------------------|
| Agent Development / agent-development | 416 | Yes | Yes |
| Command Development / command-development | 835 | Yes | Yes |
| Hook Development / hook-development | 713 | Yes | Yes |
| MCP Integration / mcp-integration | 555 | Yes | Yes |
| Plugin Settings / plugin-settings | 545 | Yes | Yes |
| Plugin Structure / plugin-structure | 477 | Yes | Yes |
| Skill Development / skill-development | 638 | Yes | Yes |
| frontend-design | 42 | Yes | Yes |
| Writing Hookify Rules / writing-hookify-rules | 375 | Yes | Yes |

**Total mirrored**: 9 skills, 4596 lines duplicated

### Name Duplicates with Different Content

These skills share a name but differ in content across sources:

| Name | Source | Lines | Description |
|------|--------|-------|-------------|
| **agent-development** | claude-plugins-official | 416 | This skill should be used when the user asks to "create an a |
| **agent-development** | claude-skills | 332 | Design and build custom Claude Code agents with effective de |
| **skill-creator** | claude-plugins-official | 480 | Create new skills, modify and improve existing skills, and m |
| **skill-creator** | claude-skills | 361 | Design effective Claude Code skills with optimal description |

### Functional Overlap Categories

Skills covering similar domains (may complement or overlap):

**Authentication & Authorization** (6 skills) -- 6 different auth approaches; each targets a specific provider/pattern

- `azure-auth` (claude-skills, 623 lines)
- `better-auth` (claude-skills, 2147 lines)
- `clerk-auth` (claude-skills, 702 lines)
- `firebase-auth` (claude-skills, 735 lines)
- `MCP OAuth Cloudflare` (claude-skills, 897 lines)
- `oauth-integrations` (claude-skills, 170 lines)

**Cloudflare Platform Services** (17 skills) -- Comprehensive Cloudflare coverage; each targets a distinct service

- `cloudflare-agents` (claude-skills, 1688 lines)
- `cloudflare-browser-rendering` (claude-skills, 877 lines)
- `cloudflare-d1` (claude-skills, 734 lines)
- `cloudflare-durable-objects` (claude-skills, 839 lines)
- `cloudflare-hyperdrive` (claude-skills, 815 lines)
- `cloudflare-images` (claude-skills, 717 lines)
- `cloudflare-kv` (claude-skills, 589 lines)
- `cloudflare-mcp-server` (claude-skills, 1284 lines)
- `cloudflare-python-workers` (claude-skills, 739 lines)
- `cloudflare-queues` (claude-skills, 937 lines)
- `cloudflare-r2` (claude-skills, 683 lines)
- `cloudflare-turnstile` (claude-skills, 539 lines)
- `cloudflare-vectorize` (claude-skills, 744 lines)
- `cloudflare-worker-base` (claude-skills, 417 lines)
- `cloudflare-workers-ai` (claude-skills, 579 lines)
- `cloudflare-workflows` (claude-skills, 868 lines)
- `MCP OAuth Cloudflare` (claude-skills, 897 lines)

**OpenAI APIs** (5 skills) -- Each covers a different OpenAI API surface (stateless, stateful, agents, responses)

- `OpenAI Apps MCP` (claude-skills, 510 lines)
- `openai-agents` (claude-skills, 443 lines)
- `openai-api` (claude-skills, 1138 lines)
- `openai-assistants` (claude-skills, 410 lines)
- `openai-responses` (claude-skills, 548 lines)

**Google / Gemini** (7 skills) -- Google Cloud + Gemini AI; each targets distinct product

- `google-app-engine` (claude-skills, 638 lines)
- `google-chat-api` (claude-skills, 943 lines)
- `google-gemini-api` (claude-skills, 2601 lines)
- `google-gemini-embeddings` (claude-skills, 932 lines)
- `google-gemini-file-search` (claude-skills, 1257 lines)
- `google-spaces-updates` (claude-skills, 242 lines)
- `google-workspace` (claude-skills, 386 lines)

**Firebase** (3 skills) -- Each covers a different Firebase service

- `firebase-auth` (claude-skills, 735 lines)
- `firebase-firestore` (claude-skills, 732 lines)
- `firebase-storage` (claude-skills, 794 lines)

**MCP Server Development** (8 skills) -- Potential overlap between fastmcp, typescript-mcp, cloudflare-mcp-server, mcp-apps-builder

- `cloudflare-mcp-server` (claude-skills, 1284 lines)
- `fastmcp` (claude-skills, 897 lines)
- `MCP OAuth Cloudflare` (claude-skills, 897 lines)
- `mcp-apps-builder` (mcp-use, 352 lines)
- `mcp-builder` (mcp-use, 71 lines)
- `mcp-cli-scripts` (claude-skills, 257 lines)
- `OpenAI Apps MCP` (claude-skills, 510 lines)
- `typescript-mcp` (claude-skills, 632 lines)

**Skill / Agent / Plugin Authoring** (8 skills) -- Multiple approaches to creating skills/agents; some are near-duplicates

- `agent-development` (claude-plugins-official, 416 lines)
- `agent-development` (claude-skills, 332 lines)
- `Create New Skills` (local, 438 lines)
- `skill-creator` (claude-plugins-official, 480 lines)
- `skill-creator` (claude-skills, 361 lines)
- `skill-development` (claude-plugins-official, 638 lines)
- `skill-review` (claude-skills, 109 lines)
- `sub-agent-patterns` (claude-skills, 1089 lines)

**Worktree Management** (2 skills) -- create-worktree-skill is subset of worktree-manager-skill; consider consolidating

- `create-worktree-skill` (local, 103 lines)
- `worktree-manager-skill` (local, 80 lines)

**TanStack Ecosystem** (4 skills) -- Each covers a different TanStack library; complementary, no overlap

- `TanStack Router` (claude-skills, 664 lines)
- `TanStack Start` (claude-skills, 782 lines)
- `TanStack Table` (claude-skills, 574 lines)
- `tanstack-query` (claude-skills, 1059 lines)

**AI SDK / Agent SDK** (4 skills) -- Distinct SDK targets but some conceptual overlap

- `ai-sdk-core` (claude-skills, 1357 lines)
- `ai-sdk-ui` (claude-skills, 558 lines)
- `claude-agent-sdk` (claude-skills, 955 lines)
- `ts-agent-sdk` (claude-skills, 197 lines)

**Project Workflow / Planning** (3 skills) -- Overlapping project management approaches; project-workflow includes slash commands

- `project-planning` (claude-skills, 1123 lines)
- `project-session-management` (claude-skills, 244 lines)
- `project-workflow` (claude-skills, 259 lines)

**Animation** (3 skills) -- Different animation libraries: Motion (Framer), AutoAnimate, Remotion (video)

- `auto-animate` (claude-skills, 355 lines)
- `motion` (claude-skills, 856 lines)
- `remotion-best-practices` (local, 49 lines)

**CMS** (3 skills) -- Different CMS platforms; no overlap

- `sveltia-cms` (claude-skills, 992 lines)
- `tinacms` (claude-skills, 623 lines)
- `wordpress-plugin-core` (claude-skills, 1090 lines)

---

## Skills with Allowed Tools

| Name | Source | Allowed Tools |
|------|--------|---------------|
| **better-auth** | claude-skills | Read, Write, Edit, Bash, Glob, Grep |
| **cloudflare-mcp-server** | claude-skills | Read, Write, Edit, Bash, Glob, Grep |
| **create-worktree-skill** | local | SlashCommand, Bash, Read, Write, Edit, Glob, Grep |
| **google-gemini-file-search** | claude-skills | Bash, Read, Write, Glob, Grep, WebFetch |
| **nextjs** | claude-skills | Read, Write, Edit, Bash, Glob, Grep |
| **OpenAI Apps MCP** | claude-skills | Read, Write, Edit, Bash, Glob, Grep |
| **shadcn-ui** | local | shadcn*:*, mcp_shadcn*, Read, Write, Bash, web_fetch |
| **skill-review** | claude-skills | Read, Bash, Glob, Grep, WebFetch, WebSearch, Edit, Write |
| **sveltia-cms** | claude-skills | Read, Write, Edit, Bash, Glob, Grep |
| **TanStack Start** | claude-skills | Bash, Read, Write, Edit |
| **tinacms** | claude-skills | Read, Write, Edit, Bash, Glob, Grep |
| **typescript-mcp** | claude-skills | Read, Write, Edit, Bash, Grep, Glob |
| **worktree-manager-skill** | local | SlashCommand, Bash, Read, Write, Edit, Glob, Grep |

---

## Top 20 Largest Skills

| # | Name | Source | Lines |
|---|------|--------|-------|
| 1 | **google-gemini-api** | claude-skills | 2,601 |
| 2 | **better-auth** | claude-skills | 2,147 |
| 3 | **nextjs** | claude-skills | 1,746 |
| 4 | **cloudflare-agents** | claude-skills | 1,688 |
| 5 | **hono-routing** | claude-skills | 1,423 |
| 6 | **email-gateway** | claude-skills | 1,405 |
| 7 | **ai-sdk-core** | claude-skills | 1,357 |
| 8 | **playwright-local** | claude-skills | 1,343 |
| 9 | **cloudflare-mcp-server** | claude-skills | 1,284 |
| 10 | **google-gemini-file-search** | claude-skills | 1,257 |
| 11 | **neon-vercel-postgres** | claude-skills | 1,181 |
| 12 | **elevenlabs-agents** | claude-skills | 1,165 |
| 13 | **openai-api** | claude-skills | 1,138 |
| 14 | **project-planning** | claude-skills | 1,123 |
| 15 | **wordpress-plugin-core** | claude-skills | 1,090 |
| 16 | **sub-agent-patterns** | claude-skills | 1,089 |
| 17 | **react-native-expo** | claude-skills | 1,078 |
| 18 | **tanstack-query** | claude-skills | 1,059 |
| 19 | **sveltia-cms** | claude-skills | 992 |
| 20 | **fastapi** | claude-skills | 960 |

---

## Top 10 Smallest Skills

| # | Name | Source | Lines |
|---|------|--------|-------|
| 1 | **stripe-best-practices** | claude-plugins-official/external | 31 |
| 2 | **simplify** | local | 39 |
| 3 | **frontend-design** | claude-code-plugins | 42 |
| 4 | **frontend-design** | claude-plugins-official | 42 |
| 5 | **remotion-best-practices** | local | 49 |
| 6 | **chatgpt-app-builder** | mcp-use | 56 |
| 7 | **convex** | local | 63 |
| 8 | **mcp-builder** | mcp-use | 71 |
| 9 | **playground** | claude-plugins-official | 77 |
| 10 | **worktree-manager-skill** | local | 80 |

---

## Full Path Index

All 130 SKILL.md files, sorted by path (relative to `~/.claude/`):

```
plugins/marketplaces/claude-code-plugins/plugins/claude-opus-4-5-migration/skills/claude-opus-4-5-migration/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/frontend-design/skills/frontend-design/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/hookify/skills/writing-rules/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/plugin-dev/skills/agent-development/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/plugin-dev/skills/command-development/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/plugin-dev/skills/hook-development/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/plugin-dev/skills/mcp-integration/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/plugin-dev/skills/plugin-settings/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/plugin-dev/skills/plugin-structure/SKILL.md
plugins/marketplaces/claude-code-plugins/plugins/plugin-dev/skills/skill-development/SKILL.md
plugins/marketplaces/claude-plugins-official/external_plugins/stripe/skills/stripe-best-practices/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/claude-md-management/skills/claude-md-improver/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/example-plugin/skills/example-skill/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/hookify/skills/writing-rules/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/playground/skills/playground/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/agent-development/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/command-development/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/hook-development/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/mcp-integration/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/plugin-settings/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/plugin-structure/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/skill-development/SKILL.md
plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/SKILL.md
plugins/marketplaces/claude-skills/skills/accessibility/SKILL.md
plugins/marketplaces/claude-skills/skills/agent-development/SKILL.md
plugins/marketplaces/claude-skills/skills/ai-sdk-core/SKILL.md
plugins/marketplaces/claude-skills/skills/ai-sdk-ui/SKILL.md
plugins/marketplaces/claude-skills/skills/auto-animate/SKILL.md
plugins/marketplaces/claude-skills/skills/azure-auth/SKILL.md
plugins/marketplaces/claude-skills/skills/better-auth/SKILL.md
plugins/marketplaces/claude-skills/skills/claude-agent-sdk/SKILL.md
plugins/marketplaces/claude-skills/skills/claude-api/SKILL.md
plugins/marketplaces/claude-skills/skills/clerk-auth/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-agents/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-browser-rendering/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-d1/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-durable-objects/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-hyperdrive/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-images/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-kv/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-mcp-server/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-python-workers/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-queues/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-r2/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-turnstile/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-vectorize/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-worker-base/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-workers-ai/SKILL.md
plugins/marketplaces/claude-skills/skills/cloudflare-workflows/SKILL.md
plugins/marketplaces/claude-skills/skills/color-palette/SKILL.md
plugins/marketplaces/claude-skills/skills/developer-toolbox/SKILL.md
plugins/marketplaces/claude-skills/skills/django-cloud-sql-postgres/SKILL.md
plugins/marketplaces/claude-skills/skills/docs-workflow/SKILL.md
plugins/marketplaces/claude-skills/skills/drizzle-orm-d1/SKILL.md
plugins/marketplaces/claude-skills/skills/elevenlabs-agents/SKILL.md
plugins/marketplaces/claude-skills/skills/email-gateway/SKILL.md
plugins/marketplaces/claude-skills/skills/fastapi/SKILL.md
plugins/marketplaces/claude-skills/skills/fastmcp/SKILL.md
plugins/marketplaces/claude-skills/skills/favicon-gen/SKILL.md
plugins/marketplaces/claude-skills/skills/firebase-auth/SKILL.md
plugins/marketplaces/claude-skills/skills/firebase-firestore/SKILL.md
plugins/marketplaces/claude-skills/skills/firebase-storage/SKILL.md
plugins/marketplaces/claude-skills/skills/firecrawl-scraper/SKILL.md
plugins/marketplaces/claude-skills/skills/flask/SKILL.md
plugins/marketplaces/claude-skills/skills/google-app-engine/SKILL.md
plugins/marketplaces/claude-skills/skills/google-chat-api/SKILL.md
plugins/marketplaces/claude-skills/skills/google-gemini-api/SKILL.md
plugins/marketplaces/claude-skills/skills/google-gemini-embeddings/SKILL.md
plugins/marketplaces/claude-skills/skills/google-gemini-file-search/SKILL.md
plugins/marketplaces/claude-skills/skills/google-spaces-updates/SKILL.md
plugins/marketplaces/claude-skills/skills/google-workspace/SKILL.md
plugins/marketplaces/claude-skills/skills/hono-routing/SKILL.md
plugins/marketplaces/claude-skills/skills/icon-design/SKILL.md
plugins/marketplaces/claude-skills/skills/image-gen/SKILL.md
plugins/marketplaces/claude-skills/skills/jquery-4/SKILL.md
plugins/marketplaces/claude-skills/skills/mcp-cli-scripts/SKILL.md
plugins/marketplaces/claude-skills/skills/mcp-oauth-cloudflare/SKILL.md
plugins/marketplaces/claude-skills/skills/motion/SKILL.md
plugins/marketplaces/claude-skills/skills/neon-vercel-postgres/SKILL.md
plugins/marketplaces/claude-skills/skills/nextjs/SKILL.md
plugins/marketplaces/claude-skills/skills/oauth-integrations/SKILL.md
plugins/marketplaces/claude-skills/skills/office/SKILL.md
plugins/marketplaces/claude-skills/skills/open-source-contributions/SKILL.md
plugins/marketplaces/claude-skills/skills/openai-agents/SKILL.md
plugins/marketplaces/claude-skills/skills/openai-api/SKILL.md
plugins/marketplaces/claude-skills/skills/openai-apps-mcp/SKILL.md
plugins/marketplaces/claude-skills/skills/openai-assistants/SKILL.md
plugins/marketplaces/claude-skills/skills/openai-responses/SKILL.md
plugins/marketplaces/claude-skills/skills/playwright-local/SKILL.md
plugins/marketplaces/claude-skills/skills/project-planning/SKILL.md
plugins/marketplaces/claude-skills/skills/project-session-management/SKILL.md
plugins/marketplaces/claude-skills/skills/project-workflow/SKILL.md
plugins/marketplaces/claude-skills/skills/react-hook-form-zod/SKILL.md
plugins/marketplaces/claude-skills/skills/react-native-expo/SKILL.md
plugins/marketplaces/claude-skills/skills/responsive-images/SKILL.md
plugins/marketplaces/claude-skills/skills/seo-meta/SKILL.md
plugins/marketplaces/claude-skills/skills/skill-creator/SKILL.md
plugins/marketplaces/claude-skills/skills/skill-review/SKILL.md
plugins/marketplaces/claude-skills/skills/snowflake-platform/SKILL.md
plugins/marketplaces/claude-skills/skills/streamlit-snowflake/SKILL.md
plugins/marketplaces/claude-skills/skills/sub-agent-patterns/SKILL.md
plugins/marketplaces/claude-skills/skills/sveltia-cms/SKILL.md
plugins/marketplaces/claude-skills/skills/tailwind-patterns/SKILL.md
plugins/marketplaces/claude-skills/skills/tailwind-v4-shadcn/SKILL.md
plugins/marketplaces/claude-skills/skills/tanstack-query/SKILL.md
plugins/marketplaces/claude-skills/skills/tanstack-router/SKILL.md
plugins/marketplaces/claude-skills/skills/tanstack-start/SKILL.md
plugins/marketplaces/claude-skills/skills/tanstack-table/SKILL.md
plugins/marketplaces/claude-skills/skills/tinacms/SKILL.md
plugins/marketplaces/claude-skills/skills/tiptap/SKILL.md
plugins/marketplaces/claude-skills/skills/ts-agent-sdk/SKILL.md
plugins/marketplaces/claude-skills/skills/typescript-mcp/SKILL.md
plugins/marketplaces/claude-skills/skills/vercel-blob/SKILL.md
plugins/marketplaces/claude-skills/skills/vercel-kv/SKILL.md
plugins/marketplaces/claude-skills/skills/wordpress-plugin-core/SKILL.md
plugins/marketplaces/claude-skills/skills/zustand-state-management/SKILL.md
plugins/marketplaces/mcp-use/skills/chatgpt-app-builder/SKILL.md
plugins/marketplaces/mcp-use/skills/mcp-apps-builder/SKILL.md
plugins/marketplaces/mcp-use/skills/mcp-builder/SKILL.md
skills/convex-best-practices/SKILL.md
skills/convex/SKILL.md
skills/create-worktree-skill/SKILL.md
skills/find-skills/SKILL.md
skills/meta-skill/SKILL.md
skills/remotion-best-practices/SKILL.md
skills/shadcn-ui/SKILL.md
skills/simplify/SKILL.md
skills/worktree-manager-skill/SKILL.md
```
