# Lavish + visual-plan / visual-recap (shareable setup)

A one-paste setup that gives any Claude Code user the **Lavish Editor** plus the
**`/visual-plan`** and **`/visual-recap`** skills built on top of it.

## What it installs

| Piece | What it does |
|---|---|
| `lavish-axi` (npm) | Renders rich HTML artifacts as an interactive browser review surface (annotate elements, queue prompts, send feedback back to the agent). Public, MIT-licensed. |
| SessionStart hook | Runs `lavish-axi` at session start so the skill context auto-loads every session. |
| `visual-plan` skill | Turns a task into an interactive visual plan you approve in the browser **before** work starts. |
| `visual-recap` skill | Summarizes a completed work unit as a visual recap surface **after** the work. |

Both skills render their HTML through `lavish-axi`. They use `npx -y lavish-axi`
as a fallback, so they work even if the global install does not land on PATH.

## Requirements

- **Node.js >= 22** (npm ships with it). Install from <https://nodejs.org> if missing.
- `git` (to fetch the skills).

## The easy way: paste the prompt

Open [`PROMPT.md`](./PROMPT.md), copy the whole block, and paste it into Claude
Code. The agent fetches this installer, shows you what it does, runs it, and
verifies the result.

## The manual way: run the installer

```bash
curl -fsSL https://raw.githubusercontent.com/amadejdemsar-create/my-claude-setup/main/share/lavish-visual-skills/install.sh | bash
```

Or download `install.sh`, read it, then `bash install.sh`. It is idempotent:
re-running it never duplicates the hook and never touches unrelated skills.

After it finishes, **restart Claude Code** so the SessionStart hook loads.

## Verify

```bash
lavish-axi --version                 # or: npx -y lavish-axi --version
ls ~/.claude/skills/visual-plan ~/.claude/skills/visual-recap
echo '<h1>hi</h1>' > /tmp/lavish-test.html && lavish-axi /tmp/lavish-test.html
```

## Notes

- The installer appends a `SessionStart` hook to `~/.claude/settings.json`,
  merging into any existing hooks rather than overwriting them.
- If the global npm install needs elevated permissions on your system Node, the
  installer falls back to `npx -y lavish-axi` for the hook (first run downloads
  the package, hence the longer hook timeout).
- `grill-me-live` (another Lavish-based skill) is intentionally **not** included
  here: it ships a macOS-specific Chrome-profile script that is not portable.
