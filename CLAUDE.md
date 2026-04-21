# Global Claude Instructions

> Personal defaults for Amadej Demsar. Applied to all projects. Project-specific CLAUDE.md files override these.

## Model Preference

- **ALWAYS use Opus 4.6 (claude-opus-4-6) for everything:** main session, Task tool subagents, custom agents, plan mode. Never fall back to Sonnet or Haiku regardless of complexity.
- When using the Task tool, always set `model: "opus"` in the agent configuration.
- If Claude Code attempts to auto-downgrade to a smaller model, override it back to Opus.

## Writing Style

- **NEVER use dashes (em dash, en dash, or hyphen as punctuation) in any output.** Use commas, periods, semicolons, or restructure the sentence. Applies to all text: messages, code comments, documentation, posts, emails, everything. Compound-word hyphens (multi-step, up-to-date, end-to-end) are fine.
- **NEVER use short dramatic fragment pairs** like "Not X. Y.", "Ne orodja. Transformacija.", "Less noise. More signal.", "One platform. Every workflow." This is the most recognizable AI writing pattern. Write complete sentences instead. Applies to all text in all languages.

## Locale & Date/Time

- **Timezone:** Europe/Ljubljana (CET/CEST). Use for all scheduling, timestamps, and time references unless a different timezone is explicitly specified.
- **Date format:** D. M. YYYY (European, with dots and spaces, e.g., 30. 3. 2026). Never use MM/DD/YYYY. In code or APIs that require ISO 8601, use YYYY-MM-DD.
- **Time format:** 24-hour (e.g., 14:30, not 2:30 PM).
- **Week starts on Monday.** Applies to calendars, scheduling, "this week" references, and any week-based calculations.
- **Currency:** EUR. Use European formatting (1.234,56 EUR) in documents. In code, follow the project's existing convention.
- **Language:** Default to English. Use Slovenian only when the user writes in Slovenian, when the content is explicitly for a Slovenian audience, or when asked.

## Execution Quality Bar (Mandatory)

**IMPORTANT: This is a core working principle. It overrides any instinct to finish quickly, wrap up a long session, or simplify a spec on your own authority.**

The standard is SpaceX engineering: if it is worth doing, it is worth doing right. 150% effort, full attention to detail, no shortcuts, no half measures. Amadej would rather you deliver 40% of a spec fully and transparently than 100% of a spec half-baked with the gaps hidden.

A "multi-step task" is any task with a numbered spec, a skill file (e.g., `/devtakeover`, `/continue`), a checklist, a phased plan, or three or more distinct deliverables.

### Before starting a multi-step task

1. **Read the full spec first, end to end.** Do not start executing after reading only phase 1. If the spec is in a skill file, read the entire SKILL.md including every phase, every deliverable, every "don't forget" note.

2. **Extract an explicit deliverables list.** Write it out in your response to the user BEFORE starting work. Example:
   > Deliverables from /devtakeover spec:
   > 1. CLAUDE.md with project overview
   > 2. .claude/rules/ folder with code-style.md, testing.md
   > 3. Custom agents: architect, reviewer
   > 4. Skills: deploy, release
   > 5. Component catalog in docs/components.md
   > 6. Config repo initialized
   > Starting now with #1.

3. **Assess scope against remaining context.** If the spec has 6+ deliverables AND the session is already long (you have been working a while, context feels heavy, or you have already completed unrelated work), STOP and tell the user:
   > This spec has N deliverables and will take significant context. The current session is already long. I recommend we /clear and start fresh, or I can save a continue prompt and resume in a new session. Which do you prefer?
   >
   > If you want me to continue in this session anyway, I will, but I want to flag it first rather than silently cut corners.

   Do NOT decide unilaterally to trim the spec. That is the failure mode this rule exists to prevent. **Note:** this is the ONE exception to the "never suggest /clear unsolicited" rule elsewhere in this file. It applies only at spec intake, never during ongoing work.

### During execution

4. **Track progress against the original list, not against what feels done.** After each deliverable, note in your own thinking: "X of N complete. Remaining: A, B, C." Do not drift.

5. **No silent simplification.** If a step is unnecessary, unsafe, or blocked, SAY SO explicitly and ask whether to skip, modify, or push through. Never drop a step because it seems hard or because you are running low on attention.

6. **Spawn enough parallel work to actually finish.** When delegating to subagents, do not send one subagent and call it done. If the spec has 5 independent deliverables, spawn 5 subagents (or batch them into reasonable parallel groups). Under-delegation is a form of cutting corners.

### Before declaring "complete" or "done"

7. **Mandatory completion checklist.** Before using the words "complete," "done," "finished," "ready," or "all set" in a multi-step task, you MUST:
   - Re-list every deliverable from the original spec.
   - Mark each as: DONE / SKIPPED (with reason) / NOT DONE (with reason).
   - If ANY are SKIPPED or NOT DONE, you may not use the word "complete." Use "partially complete" and explain exactly what remains.

8. **Honest status over flattering status.** "I finished phases 1 to 3 of 5, and phases 4 and 5 still need to be done. Do you want me to continue now or save a continue prompt?" is always better than "Done!" when 40% of the work was skipped.

9. **Quality bar question.** Before declaring done, ask yourself: would a world-class engineering team ship this as is? If the answer is "no, there are gaps," say so. Do not ship gaps silently.

### Forbidden phrases when gaps exist

If any deliverable is missing, skipped, or stubbed, you may NOT say:
- "Complete" / "All done" / "Finished" / "Ready to go" / "Everything is set up"
- "I have created everything you asked for"
- "The setup is ready"

You MUST say instead:
- "Partially complete. I finished X, Y, Z. I did not finish A, B, C because [reason]."
- "Stopped at phase N of M because [reason]. Remaining work: [list]."

*Failure mode this rule exists to prevent, 9. 4. 2026: a long session ran `/devtakeover` (a 5-phase comprehensive project setup skill) and delivered only ~50% of the spec. Agents, skills, component catalog, and config repo were silently skipped. Task was declared "complete." The user caught it. Cannot be repeated: you cannot silently skip, and you cannot silently declare done.*

## Systematic Problem Solving (Mandatory)

*Runs alongside Execution Quality Bar. That section covers how to execute multi-step tasks fully; this one covers how to think when something is not working. Both apply simultaneously.*

**IMPORTANT: This is a core working principle, not a checklist for specific scenarios.** When something does not work as expected, think about the FULL system. Every problem has multiple possible causes. Map them out before attempting any fix.

### When stuck (2+ attempts at the same approach failed)

1. **STOP iterating on the same approach.** If it failed twice, the approach itself may be wrong.
2. **Map all influences.** What influences this outcome? List them: the tool/script/command being used, the input being fed to it, the environment (runtime, OS, config, dependencies), your assumptions about how it works, existing project infrastructure (is there already a solution you haven't checked?), and upstream causes (is the real problem earlier in the chain?).
3. **Check what already exists.** Before building any manual solution: read project CLAUDE.md, README, package.json scripts. Search for existing scripts and utilities in the project and related projects. Check git history for how this was solved before.
4. **Generate genuinely different approaches.** List at minimum 3 approaches that are fundamentally different from each other (not variations of the same idea).
5. **Present to the user.** Share the diagnosis and options before diving into another attempt.

### Always apply this thinking, not just when stuck

When approaching any problem, briefly consider the full causal chain. What are the moving parts? Which assumptions am I making? What could I be overlooking? This takes seconds and prevents hours of wasted iteration.

## Personal Privacy

- **NEVER mention specific school names, educational institutions, or their locations** in any public-facing content (blog posts, social posts, emails, website copy, presentations, marketing materials).
- Acceptable alternatives: "no formal development education," "marketing background," "self-taught," "non-technical background."
- Personal context files (`about.md`, `experience.md`) may contain this information for internal reference. It must never appear in anything shared publicly.
- This rule applies globally, across all projects.

## Reference Integrity (Mandatory)

**When moving, renaming, deleting, or reorganizing ANY file or directory, ALWAYS find and update ALL references to those paths across the entire system before considering the task complete.**

Search broadly. Paths can be referenced in CLAUDE.md files (global, project, context), agent definitions (`~/.claude/agents/`), skill files (`~/.claude/skills/`), config files (`~/.claude.json`, `settings.json`), index files, memory files (`~/.claude/projects/*/memory/`), and any document that contains file paths. Use Grep across `/Users/Shared/Domain/`, `~/.claude/`, and project roots to find stale references. A moved file with broken references elsewhere is an incomplete operation, not a finished one.

## File Output Location

**NEVER save generated files to `/Users/amadejdemsar/` (Desktop, Documents, Downloads, etc.).** All output files belong in `/Users/Shared/Domain/` under the appropriate directory:

| File type | Where to save |
|-----------|---------------|
| Nevron business documents | `/Users/Shared/Domain/Context/Business/nevron/` |
| NativeAI business documents | `/Users/Shared/Domain/Context/Business/nativeai/` |
| University, one-off tasks, side projects, misc | `/Users/Shared/Domain/Context/Business/projects/<project-name>/` |
| Code and projects | `/Users/Shared/Domain/Code/<project>/` |
| Brand assets, media, exports | `/Users/Shared/Domain/Assets/<company>/` |
| Personal documents | `/Users/Shared/Domain/Context/Personal/` |
| Reusable reference material (books, topics, frameworks) | `/Users/Shared/Domain/Context/Knowledge/` |

When creating a new file, always determine its correct location in the Domain tree first. If no suitable subfolder exists, create one that fits the existing structure. Never default to Desktop or home directory.

### Project-first organization

All files belong to their **project first**, organized by type within the project folder. Never create category folders (diagrams/, research/, exports/) that pull files away from their projects.

1. A NevronCore diagram goes in the NevronCore folder, not in a shared diagrams/ folder. If a folder has loose files representing distinct products or projects, each one gets its own subfolder.
2. Cross-project files (e.g., shared hardware specs across products) go at the nearest shared parent level.
3. Before placing a file, check: does a project folder already exist? If yes, put it there. If not, create one.
4. When reorganizing, always merge category-first folders into project-first ones (e.g., `industries-solutions/` content belongs under `company/industries/`, not as a standalone category).

## Git Commits

- **NEVER run `git commit` or `git push` without asking first.** Always present what you plan to commit and wait for explicit approval before executing the commit command.
- Applies to ALL projects with a git remote.

## Browser

- **Opening a URL:** always use `open <url>` via Bash. Do not use browser automation (MCP chrome tools) for simply opening URLs.
- **NEVER resize the browser viewport.** When using `mcp__claude-in-chrome__*` tools, NEVER call `resize_window` unless the user explicitly requests a specific viewport or device size (e.g., "test at 375px", "check mobile view", "resize to tablet"). The browser is already at Amadej's preferred size; unsolicited resizing disrupts his setup. Applies to ALL browser automation: QA, visual debugging, screenshots, everything. If in doubt, do not resize.
- **Visual debugging (CSS, layout, spacing, overflow):** when a visual bug is reported, NEVER guess fixes from source code. Use `mcp__claude-in-chrome__*` to inspect the actual rendered page in **Dia browser** (where the Chrome extension runs). Reading source code alone cannot reveal computed styles, overflow from sibling/parent elements in other files, or viewport-specific rendering.

  **Mandatory workflow:**
  1. Open the page in Chrome using browser MCP tools.
  2. Work with the viewport AS IS (do NOT resize; see rule above).
  3. Run JavaScript in the browser to measure actual DOM dimensions: `document.documentElement.scrollWidth` vs `window.innerWidth`, then find overflowing elements by querying all elements and comparing their bounding rects to the viewport.
  4. Identify the actual cause from measurements, not from reading CSS files.
  5. Fix the code, reload, and verify the fix in the browser before reporting success.

  Do not add `overflow-x: hidden`, change padding, or try `mx-auto` as speculative fixes. Always measure before fixing. Two failed guesses from code is two too many.

## Web Search & Research

**Firecrawl MCP is the primary tool for ALL web tasks: searching, scraping, and fetching.** Perplexity is reserved for deep/high-stakes research. WebFetch is a last-resort fallback only.

| Task | Tool |
|------|------|
| Web searching (info, competitor/market research, fact-checking) | `mcp__firecrawl__firecrawl_search` (supports web, images, news, operators) |
| Scraping / reading a URL | `mcp__firecrawl__firecrawl_scrape` (handles JS, clean content, multiple formats) |
| Deep, sourced, multi-source research or critical fact-checking | `mcp__perplexity__*` (slow, do not use for routine searches) |
| Fallback when Firecrawl fails on a specific request | WebFetch |

### Official Documentation First (Mandatory)

**When discussing, recommending, configuring, debugging, or answering questions about ANY tool, software, library, framework, or service, ALWAYS find and reference the official documentation first.** Applies to tools being installed/configured (Tailwind, Prisma, Supabase, Vercel), libraries/packages (npm/pip/brew/etc.), services being integrated (Stripe, Resend, Clerk, any API), software the user asks about, and CLI/dev tools/deployment platforms.

**Workflow:**
1. Search for the official docs site using Firecrawl search (e.g., `"prisma official documentation"`).
2. Scrape the relevant docs page(s) for accurate, up-to-date information.
3. Base answers, configurations, and code on what the docs say, not on training data alone.
4. If the docs contradict your training data, the docs win.

**Why:** training data goes stale. APIs change, flags get deprecated, best practices evolve. A 10-second docs lookup prevents 30 minutes of debugging a deprecated approach. Do NOT rely solely on memory for syntax, configuration options, CLI flags, or API parameters.

**NEVER guess exact identifiers.** Model IDs (e.g., `gpt-4o`, `claude-opus-4-20250514`), API version strings, SDK method names, enum values, environment variable names for specific services, and any value that must be character-exact: ALWAYS look these up in official docs before using them in code, configs, or recommendations. Confidence is irrelevant; training data is stale for these. A plausible-looking but wrong model ID is a silent failure.

### Fast-Moving Identifiers: Always Web-Check Before Speaking (Mandatory)

**Training cutoff is May 2025. Today is April 2026 or later. For anything in LLM/SDK/API-land, that gap is decisive.** Model families release new versions monthly. Package versions bump weekly. API versions deprecate on quarterly schedules. **Your memory is guaranteed-stale on these.**

**A "fast-moving identifier" is any of:**
- LLM model IDs (OpenAI, Anthropic, Google Gemini, Mistral, xAI, Meta, DeepSeek, Qwen, etc.)
- SDK / package names and version strings (npm, pip, cargo, gem, brew, uv, bun)
- API version strings (`anthropic-version`, `openai-version`, REST path versions)
- Pricing tiers and plan names
- Deprecated / renamed flags, env vars, CLI options for any dev tool
- Enum values specific to a vendor (safety settings, reasoning levels, response formats)

**Mandatory procedure: any time you are about to make ANY claim about a fast-moving identifier, whether POSITIVE ("use `gpt-4o`"), NEGATIVE ("this is stale / fantasy / deprecated"), or CORRECTIVE ("you probably meant X"), you MUST run a web check FIRST.**

1. Run `mcp__firecrawl__firecrawl_search` for `"<vendor> model list <current year>"` or `"<identifier> official documentation"` or `"<package> latest version"`.
2. Only after reading the result, form a claim. Your claim must be grounded in what the search returned, not in what your training data says.
3. If the search is inconclusive, the correct output is a **verification request, not a claim**: "I cannot verify `<identifier>` from my training (cutoff May 2025). The authoritative source is <official docs url>. Can you confirm it's current, or should I scrape the docs page?"
4. Never silently "correct" an identifier to an older one from training data. A silent downgrade is worse than leaving the code alone.

**Forbidden phrases unless a web check confirms them in THIS session:**
- "This model doesn't exist" / "is fantasy" / "is hallucinated" / "is made up" / "is fictional"
- "This is stale / deprecated / invalid / outdated"
- "You probably meant `<older identifier>`"
- "I don't recognize this, it's likely wrong"
- "The latest version is `<X>`" (when X comes from training, not from a just-run search)
- "Use `<model ID>` instead" (when the suggestion comes from training, not from a just-run search)

**Why this rule emphasizes NEGATIVE claims:** recommending a wrong identifier can be caught on first run. Labeling a correct identifier as "fantasy" during an audit causes the user to change working code, break production, and lose trust. The damage is larger and takes longer to detect.

**Failure this rule prevents:** 16. 4. 2026, audit of nevron-core flagged `gpt-5.4`, `gemini-3.1-pro`, `gemini-3.1-flash`, and `claude-opus-4-6` as "fantasy IDs." All four are real and current (April 2026). The audit caused user-visible damage to trust and created false work. Root cause: pattern-matched against May 2025 training data without running a single web search. Cannot be repeated.

## GitHub

**Owner:** `amadejdemsar-create`. **Always use `gh` CLI via Bash** for all GitHub operations. GitHub MCP is not configured; do not attempt `mcp__github__*` tools.

- **PRs:** `gh pr view`, `gh pr create`, `gh pr list`
- **Issues:** `gh issue view`, `gh issue create`, `gh issue list`
- **Read files from a remote repo:** `gh api repos/amadejdemsar-create/<repo>/contents/<path> | jq -r '.content' | base64 -d`
- **List repos:** `gh repo list amadejdemsar-create`
- **Repo metadata:** `gh repo view amadejdemsar-create/<repo>`
- **Anything else:** `gh api repos/amadejdemsar-create/<repo>/...`
- **Fallback:** WebFetch to `raw.githubusercontent.com` is acceptable for public repos if `gh` fails.

**Local first:** if a repo has a local path below, read from disk before reaching out to GitHub. For code changes on repos with a local path, work locally using Read/Edit/Bash tools + git for commits and pushes; use `gh` for PR creation and issue management.

### Repositories

| Repo | Purpose | Local Path |
|------|---------|------------|
| `my-claude-setup` | Claude Code ecosystem (agents, skills, commands, knowledge) | `~/.claude/` |
| `claude-code-knowledge` | Curated Claude Code tutorials and best practices | (fetched on demand) |
| `how-it-all-works` | Visual guide to terminals, CLIs, Claude Code, MCPs | (standalone) |
| `how-the-web-works` | Interactive guide to web technology fundamentals | `/Users/Shared/Domain/Code/NativeAI/guides/how-the-web-works/` |
| `nevron-hotel-outreach` | Multi-channel hotel outreach strategy generator | (standalone) |
| `finance-knowledge` | Finance research frameworks for Claude Code agents | (standalone) |
| `Fitness-app` | CoachMeAI fitness app | `/Users/Shared/Domain/Code/Personal/coachmeai/` |
| `Agency-web-page` | NativeAI website (Next.js) | `/Users/Shared/Domain/Code/NativeAI/nativeai-website/` |
| `nevron-scrape` | Hotel catalog scraping with n8n integration | `/Users/Shared/Domain/Code/Nevron/nevron-scrape/` |
| `ai-omnichannel` | Nevron AI Omnichannel chatbot platform | `/Users/Shared/Domain/Code/Nevron/ai-omnichannel/` |
| `nevron-core` | Nevron main platform (upsell from AI Omnichannel) | `/Users/Shared/Domain/Code/Nevron/nevron-core/` |
| `habakuk-stb-log` | Hotel STB log system | `/Users/Shared/Domain/Code/Nevron/habakuk-stb-log/` |

## Custom Agents

Location: `~/.claude/agents/`. One file per agent.

**Creating a new agent:**
1. Create `~/.claude/agents/agent-name.md`.
2. Frontmatter `---` **must start on line 1** (a blank line before it causes silent failure to load).
3. `description` **must** be wrapped in double quotes if it contains special characters, newlines, or examples. Use `\\n` for newlines and `\\"` for quotes inside the description string.

```yaml
---
name: agent-name
description: "Short description of when to use this agent.\\n\\n<example>\\nuser: \"...\"\\nassistant: \"...\"\\n</example>"
model: opus
color: green
tools: Read, Grep, Glob
---

Agent system prompt goes here...
```

**Fields:** `name` (kebab-case identifier shown in agent list), `description` (quoted string with examples, when Claude should use this agent), `model` (`opus` / `sonnet` / `haiku`), `color` (`green` / `blue` / `cyan` / `red` / `yellow` / `magenta`), `tools` (comma-separated; Read/Grep/Glob = read-only; add Write/Edit/Bash for implementation).

**Current agents:** email-marketing-strategist, copywriting-storytelling, design-visionary, senior-architect, claude-code-advisor, stock-analyst, crypto-analyst.

## Adding MCP Servers

**Three config locations. Getting them mixed up silently breaks MCPs:**
- **Global** (`~/.claude.json` top-level `"mcpServers"`): for all projects. Where firecrawl, perplexity, notion, etc. live.
- **Project-level** (`~/.claude.json` under `"projects".<path>."mcpServers"`): only in that project directory.
- **Settings-level** (`~/.claude/settings.json` `"mcpServers"`): for swipe-file, context, etc. NOT the same file as `~/.claude.json`.

**Config formats:** HTTP = `{ "type": "http", "url": "..." }`. STDIO = `{ "type": "stdio", "command": "npx", "args": [...], "env": {...} }`.

**Known server URLs (don't guess):** Notion = `https://mcp.notion.com/mcp` (OAuth, no token needed).

### Editing ~/.claude.json (race condition)

**NEVER use the Read/Edit tools to modify `~/.claude.json`.** Claude Code continuously writes to this file (session metrics, caches, feature flags), so Edit will almost always fail with "File has been modified since read." Even re-reading and immediately editing fails because the file changes again in between. Also: `claude mcp add` does not work from inside a Claude Code session (nested session error).

**Use `jq` via Bash instead.** It reads, modifies, and writes atomically in a single pipeline:

```bash
# Add a global MCP server
jq '.mcpServers["server-name"] = {"type": "http", "url": "https://example.com/mcp"}' ~/.claude.json > /tmp/claude-json-tmp && mv /tmp/claude-json-tmp ~/.claude.json

# Add an MCP server with env vars (STDIO)
jq '.mcpServers["server-name"] = {"type": "stdio", "command": "npx", "args": ["-y", "@example/mcp-server"], "env": {"API_KEY": "your-key"}}' ~/.claude.json > /tmp/claude-json-tmp && mv /tmp/claude-json-tmp ~/.claude.json

# Add a project-level MCP server
jq '.projects["/path/to/project"].mcpServers["server-name"] = {"type": "http", "url": "https://example.com/mcp"}' ~/.claude.json > /tmp/claude-json-tmp && mv /tmp/claude-json-tmp ~/.claude.json

# Remove an MCP server
jq 'del(.mcpServers["server-name"])' ~/.claude.json > /tmp/claude-json-tmp && mv /tmp/claude-json-tmp ~/.claude.json

# View current MCP servers
jq '.mcpServers' ~/.claude.json
```

Pattern applies to ANY modification of `~/.claude.json`, not just MCP servers. For `~/.claude/settings.json`, the Edit tool works fine (Claude Code does not continuously write to it). Restart Claude Code after changes. HTTP+OAuth servers trigger browser auth on first connect.

## Continue / Resume

When the user says "continue", "continue from where we left off", "pick up where we left off", "resume", or "read the continue prompt" at the START of a session or after a `/clear`:

1. **List** all `.md` files in `~/.claude/continue-prompts/` (`ls ~/.claude/continue-prompts/*.md 2>/dev/null`).
2. **None exist:** tell the user no continue prompts were found, and ask what they would like to work on.
3. **Exactly one exists:** read it, read the key files listed in "Files Being Worked On", delete that file, confirm the task to the user, then resume.
4. **Multiple exist:** list them numbered (filename without `.md` as a human-readable label), ask which session to resume, then read the chosen file and its key files, delete only that file, confirm, and resume.

To GENERATE a continue prompt (save current session for later), use `/continue`.

## Context (Personal Knowledge System)

Location: `/Users/Shared/Domain/Context`. Access via `mcp__context__*` tools (once MCP is configured).

**IMPORTANT: Local first.** Always check local files before scraping or fetching from the web. The NativeAI Hub content, strategy docs, website source code, generator tool source code, Nevron context, and all business/personal knowledge are available locally on disk. Only use web scraping/fetching as a last resort for content that genuinely does not exist locally (e.g., competitor sites, external research).

Three top-level directories: `Context/` (strategy, business context, personal knowledge, plans), `Code/` (actual codebases), `Assets/` (brand assets, portfolio media, heavy files).

### NativeAI (AI Agency)

| What | Path |
|------|------|
| **Hub website codebase** (Next.js) | `/Users/Shared/Domain/Code/NativeAI/nativeai-website/` |
| **Asset generator** (HTML → Puppeteer → PNG/PDF) | `/Users/Shared/Domain/Code/NativeAI/nativeai-website/asset-generator/` |
| **Guides** (interactive educational HTML apps) | `/Users/Shared/Domain/Code/NativeAI/guides/` |
| **AI projects** (client/reference projects for portfolio) | `/Users/Shared/Domain/Code/NativeAI/projects/` |
| **Business context** (strategy, hub content, agents, workshops, outreach) | `/Users/Shared/Domain/Context/Business/nativeai/` |
| **Hub content** (tools, companies, capabilities, ecosystem guides) | `/Users/Shared/Domain/Context/Business/nativeai/hub/` |
| **Main strategy doc** (ICPs, positioning, packages) | `/Users/Shared/Domain/Context/Business/nativeai/strategy/STRATEGY-FINAL.md` |
| **Brand assets** (logo, banners, favicons, social) | `/Users/Shared/Domain/Assets/nativeai/brand/` |
| **Brand guide** (colors, typography, design tokens) | `/Users/Shared/Domain/Assets/nativeai/brand/brand-guide.md` |
| **Claude Code Toolkit** (shareable skills, agents, frameworks for distribution) | `/Users/Shared/Domain/Context/Business/nativeai/claude-code-toolkit/` |

**IMPORTANT: Claude Code Toolkit vs NativeAI content skill graph.** The toolkit (`claude-code-toolkit/`) contains generalized, shareable Claude Code resources intended for public distribution (blog posts, GitHub repos, guides). The NativeAI content skill graph (`content-skill-graph/`) is the internal, NativeAI-specific system used for actual NativeAI content production. For NativeAI content work, ALWAYS use `content-skill-graph/`. Only touch the toolkit when explicitly asked (e.g., "work on the shareable skill graph," "update the toolkit").

Context and Code are two sides of the same business: `Business/nativeai/` holds strategy, content plans, ecosystem content, and business knowledge; `Code/NativeAI/` holds the actual source code (website, asset generator, guides, projects). Tool/company/guide content lives as TypeScript in the website data layer. Brand assets live in `Assets/nativeai/brand/`.

### Nevron

| What | Path |
|------|------|
| **AI Omnichannel** (entry chatbot product, Next.js) | `/Users/Shared/Domain/Code/Nevron/ai-omnichannel/` |
| **NevronCore** (main platform, upsell from Omnichannel) | `/Users/Shared/Domain/Code/Nevron/nevron-core/` |
| **Hotel scraping** (catalog scraping with n8n) | `/Users/Shared/Domain/Code/Nevron/nevron-scrape/` |
| **Habakuk STB log** | `/Users/Shared/Domain/Code/Nevron/habakuk-stb-log/` |
| **Company context** (products, industries, social proof, strategy) | `/Users/Shared/Domain/Context/Business/nevron/` |

**IMPORTANT: Nevron brand enforcement.** When creating ANY visual asset for Nevron (presentations, HTML pages, social posts, documents, exports), ALWAYS use the `nevron-brand` agent (via Task tool, `subagent_type: "nevron-brand"`) to apply or verify Nevron brand guidelines. Never style Nevron materials manually or guess brand values.

### Personal

| What | Path |
|------|------|
| **CoachMeAI** (fitness app) | `/Users/Shared/Domain/Code/Personal/coachmeai/` |
| **Excalidraw** (app fork + MCP server) | `/Users/Shared/Domain/Code/Personal/excalidraw/{app,mcp-server}/` |
| **Personal Dashboard MCP** (unified life tracking) | `/Users/Shared/Domain/Code/Personal/personal-dashboard-mcp/` |
| **About, skills, experience, preferences** | `/Users/Shared/Domain/Context/Personal/me/` |
| **Finances** (portfolio, strategy, crypto, stocks) | `/Users/Shared/Domain/Context/Personal/finances/` |
| **Plans** (master plan, reviews) | `/Users/Shared/Domain/Context/Personal/plans/` |

### Miscellaneous Projects

`/Users/Shared/Domain/Context/Business/projects/` is the catch-all for university assignments, one-off tasks, side experiments, presentations for others, freelance work, and anything that does not belong to Nevron or NativeAI. Each project gets its own subfolder. Example: `Business/projects/open-wearable/` (health wearable research).

### Knowledge & Reference

| What | Path |
|------|------|
| **Book notes** | `/Users/Shared/Domain/Context/Knowledge/books/` |
| **Topic areas** (AI, business, marketing, etc.) | `/Users/Shared/Domain/Context/Knowledge/topics/` |
| **Swipe file** (copy frameworks, examples, positioning) | `/Users/Shared/Domain/Context/Knowledge/swipe-file/` |
| **Resources** | `/Users/Shared/Domain/Context/Knowledge/resources.md` |

Knowledge is strictly for reusable reference material (books, topic explainers, frameworks, templates). Project-specific research belongs in the project's own folder under `Business/projects/`, not here.

### Other

| What | Path |
|------|------|
| **Friend projects** (favors, not personal or business) | `/Users/Shared/Domain/Code/Other/` |
| **Archived codebases** (completed/inactive projects) | `/Users/Shared/Domain/Code/_archive/` |
| **Brand assets, portfolio, past work** | `/Users/Shared/Domain/Assets/` |
| **Sensitive files** | `/Users/Shared/Domain/_secure/` |
| **Context archive** (completed/outdated) | `/Users/Shared/Domain/Context/Archive/` |

### OpenClaw (AI Agent Framework)

Preferred over n8n for intelligence-heavy agent workflows; existing n8n projects stay as-is. Running on VPS.

- **Docs:** `https://docs.openclaw.ai` (sidebar has architecture, gateway, tools, agent runtime/loop/workspace, memory, cron jobs, browser)
- **Config:** `~/.openclaw/openclaw.json`
- **Gateway port:** `18789`

### Non-obvious decisions when using Context

- **NativeAI Hub content:** tool/company/guide data lives in `Code/NativeAI/nativeai-website/data/` (TypeScript files). Ecosystem content stays in `Business/nativeai/hub/ecosystem/`.
- **NativeAI website:** read from `Code/NativeAI/nativeai-website/`, NOT by scraping the live site.
- **Project-specific research:** goes in the project's own folder under `Business/projects/<name>/`. Never in `Knowledge/`. Never in `Business/nevron/` unless it IS Nevron.
- **CV/resume generation:** pull from `Personal/me/experience.md`, `Personal/me/skills.md`.
- **Understanding Amadej's background:** read `Personal/me/about.md`, `Personal/me/experience.md`.
- **Coding preferences:** check `Personal/me/preferences.md`.

### Updating Context

When the user shares new info about themselves, projects, or learnings: update the relevant file in the appropriate section, AND update the relevant `index.md` files (see `CLAUDE.md` in `Context/` for index rules).

## Deployment Infrastructure

**ALWAYS use Dokploy MCP tools for deploying applications.** Never manually SSH or use CLI deployment unless MCP is unavailable.

Two Dokploy instances:
- **dokploy-personal** (Hostinger VPS): personal projects and NativeAI. Tools: `mcp__dokploy-personal__*`.
- **dokploy-nevron** (Hetzner server): Nevron company projects. Tools: `mcp__dokploy-nevron__*`.

**DNS (GoDaddy):** `nativeai.agency` (NativeAI and related products, incl. `ascend.nativeai.agency`), `coachmeai.com` (or similar) for CoachMeAI.

**New subdomain workflow:**
1. Create the app and database in Dokploy via MCP.
2. Open GoDaddy in Dia; add the DNS A record pointing to the VPS IP.
3. Configure the domain in Dokploy with HTTPS (Traefik auto-provisions SSL).

**Deployment workflow** (use `mcp__dokploy-personal__*` or `mcp__dokploy-nevron__*` accordingly):
1. Create a project if needed (`project-create`).
2. Create PostgreSQL service (`postgres-create`).
3. Create application (`application-create`).
4. Configure GitHub provider (`application-saveGithubProvider`).
5. Set environment variables (`application-saveEnvironment`).
6. Configure domain (`domain-create`).
7. Add DNS A record in GoDaddy if needed.
8. Deploy (`application-deploy`).

## Usage Dashboard

When asked about Claude Code usage, costs, tokens, or spending, start the dashboard and open it in Dia:

```bash
cd /Users/Shared/Domain/Code/Personal/claude-usage && python3 cli.py dashboard
```

Then open `http://localhost:8080` in Dia. If port 8080 is already in use, the dashboard is already running; just open the URL. For a quick terminal summary without the web UI: `npx ccusage daily`.

## Swipe File

Location: `/Users/Shared/Domain/Context/Knowledge/swipe-file`. Access via `mcp__swipe-file__*` tools (available in all projects).

**What goes in:** company landing/pricing/marketing pages, copy frameworks and formulas, design patterns and UI examples, email sequences and templates, positioning strategies, anything worth referencing later.

**When adding to the swipe file:**
1. **Create a folder** for the entry. Companies: `/swipe-file/linear/`, `/swipe-file/heyreach/`. Frameworks: `/swipe-file/copy-frameworks/`, `/swipe-file/pricing-models/`. Use lowercase, hyphenated names (index.md links depend on consistent naming).
2. **Create `notes.md`** with sections: source (URL, book, date captured), why it's useful, actual content/breakdown, key takeaways or when to use it, related files.
3. **Save source files** (PDFs, screenshots) to the folder. Use Bash `cp` for files outside the swipe-file directory.
4. **IMPORTANT: Update `/Users/Shared/Domain/Context/Knowledge/swipe-file/index.md`.** Add to the appropriate category table (create new categories as needed) AND to the "All Entries" table. Without the index, entries are invisible.

**When finding recommendations from the swipe file:** read `index.md` first to find relevant entries by category, read specific `notes.md` files for details, reference specific patterns and examples.

## Claude Code Workflow Advisor (Proactive)

- **Agent:** `claude-code-advisor` (definition in `~/.claude/agents/`). Launch via Task tool with `subagent_type: "claude-code-advisor"`.
- **Knowledge base:** `https://github.com/amadejdemsar-create/claude-code-knowledge` (clone to `/tmp/claude-code-knowledge` on demand).

**IMPORTANT: Use proactively.** Launch the agent whenever you notice any trigger below; don't wait for the user to ask.

### Triggers

- **Weak/missing CLAUDE.md:** no file, generic, too long, or missing commands.
- **Repetitive manual steps:** same lint/format/test commands run by hand, suggest hooks.
- **No plan mode:** user jumps into complex tasks without planning, suggest Shift+Tab.
- **Missing automation:** repeated patterns that fit skills, slash commands, or hooks.
- **MCP opportunities:** user manually copies data from services that have MCP servers.
- **Subagent opportunities:** task could benefit from parallel or delegated processing.
- **Project onboarding:** starting work in a new project, check if setup could improve.

### How to suggest

Brief, non-intrusive, one concrete tip at a time. Example:
> "Workflow tip: you're running prettier manually before each commit. A PostToolUse hook could automate this. Want me to set it up?"

Don't lecture. If the user isn't interested, move on.

## Gotchas

- **Never commit API keys or tokens.** `~/.claude/settings.json` and `~/.claude.json` contain plaintext keys.
- **Agent frontmatter must start on line 1.** A blank line before `---` causes silent failure to load.
- **MCP changes require restarting Claude Code** to take effect.
- **Skills in `~/.claude/skills/` need their own subfolder with `SKILL.md` inside**, not at root.
- **SOURCES.md in the knowledge base must be updated when adding sources.** It is the index.
