# NativeAI Claude Code toolkit: setup prompt

Paste everything below this line into Claude Code and let it run. Re-run the same prompt anytime to update everything to the latest versions.

---

You are setting up the NativeAI shared Claude Code toolkit on this machine. Execute the steps in order, verify at the end, and report exactly what was installed, updated, or needs manual action. The whole process is idempotent: existing copies get overwritten with the latest versions.

**Step 1: fetch the toolkit repo.** Remove `/tmp/nativeai-toolkit` if it exists, then:
`git clone --depth 1 https://github.com/amadejdemsar-create/my-claude-setup.git /tmp/nativeai-toolkit`

**Step 2: install/refresh skills.** Copy each of these folders from `/tmp/nativeai-toolkit/skills/` into `~/.claude/skills/` (replace existing folders entirely):
transcreate, grill-me, prompt-writer, reason-business, premortem, firecrawl, image-director, landing-page-builder, video-watch, animation-analyzer, visual-plan, visual-recap, visualize, brand-system, asset-studio

**Step 3: install/refresh agents.** Copy each of these files from `/tmp/nativeai-toolkit/agents/` into `~/.claude/agents/`:
native-transcreator.md, copywriting-storytelling.md, email-marketing-strategist.md, design-visionary.md, video-analyst.md, web-operator.md, claude-code-advisor.md

**Step 4: install third-party design skills from their original sources** (skip any already present in `~/.claude/skills/`):
- `npx skills add pbakaus/impeccable -g --agent claude-code --copy -y`
- `npx skills add nextlevelbuilder/ui-ux-pro-max-skill -g --agent claude-code --copy -y`
- `npx skills add Leonxlnx/taste-skill -g --agent claude-code --skill design-taste-frontend --skill minimalist-ui --skill industrial-brutalist-ui --skill high-end-visual-design --copy -y`
- `npx skills add emilkowalski/skills -g --agent claude-code --skill emil-design-eng --copy -y` (animation and interaction polish)

If `npx skills` fails, fall back to cloning each GitHub repo shallow and copying its skill folder(s) into `~/.claude/skills/` manually.

**Step 5: local dependencies for the video skills.** Ensure `yt-dlp` and `ffmpeg` are installed (`brew install yt-dlp ffmpeg` on macOS). Then open `~/.claude/skills/video-watch/SKILL.md` and follow its transcription setup section.

**Step 6: cleanup.** `rm -rf /tmp/nativeai-toolkit`

**Step 7: verify and report.** For every skill from Step 2 and 4: confirm the folder exists and its SKILL.md starts with a `---` YAML frontmatter block containing a description. For every agent from Step 3: confirm the file exists and starts with `---` on line 1. Print a checklist of DONE / MISSING items and list any errors verbatim.

**Manual one-time steps (tell the user):**
1. Firecrawl needs a personal API key: create one at firecrawl.dev and add `FIRECRAWL_API_KEY` to the shell environment. Needed for the firecrawl skill and the web-operator agent.
2. image-director renders through the Codex desktop app's built-in image tool: install the Codex app and sign in, otherwise image generation steps will fail.
3. Restart Claude Code after installation so the new skills and agents load.

**How to use it (short version for the user):**
- Any translation or localization: `/transcreate` (never raw machine translation).
- Any design work (pages, brand, banners, slides, premium polish): ask for design work naturally; the `design-visionary` agent is the single front door and routes to the right skill.
- Research and scraping: the firecrawl skill; heavier multi-step web work goes through the `web-operator` agent.
- Watch/transcribe/summarize a video: paste the link and ask; `video-watch` handles it.
- Before building anything non-trivial: `/grill-me` (requirements interview) and `/visual-plan` (interactive plan page, renders via `npx lavish-axi`, no install needed).
- Copy and content: the `copywriting-storytelling` and `email-marketing-strategist` agents.
- Second brain for decisions: `/reason-business` and `/premortem`.
