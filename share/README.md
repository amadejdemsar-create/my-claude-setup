# Lavish bundle (shareable)

A one-paste way to give anyone the **Lavish Editor** plus the two skills built on
it, **`/visual-plan`** and **`/visual-recap`**, and the matching CLAUDE.md
guidance. This is a focused bundle, not the whole setup.

## The easy way: paste the prompt

Open [`PROMPT.md`](./PROMPT.md), copy the whole block, paste it into a fresh
Claude Code session. The recipient's agent fetches the installer, shows what it
does, runs it, and verifies. (The same button lives on the showcase site under
the Skills section: "Install the Lavish bundle".)

## The manual way: run the installer

```bash
curl -fsSL https://raw.githubusercontent.com/amadejdemsar-create/my-claude-setup/main/install.sh | bash
```

Or clone the repo and run `bash install.sh` from the checkout.

## What it installs

| Piece | Destination |
|---|---|
| `lavish-axi` (public npm pkg) + SessionStart hook | global + `~/.claude/settings.json` |
| `visual-plan` skill | `~/.claude/skills/visual-plan/` |
| `visual-recap` skill | `~/.claude/skills/visual-recap/` |
| Lavish guidance ([`CLAUDE-lavish.md`](./CLAUDE-lavish.md)) | appended to `~/.claude/CLAUDE.md` |

## Requirements

- **Node.js >= 22** (npm ships with it) — <https://nodejs.org>
- `git`

## Guarantees

- **Idempotent**: re-running never duplicates the SessionStart hook or the
  CLAUDE.md section.
- **Non-destructive**: it overwrites only the two skills it ships, never deletes
  the recipient's other skills, merges into existing `SessionStart` hooks, and
  appends to `~/.claude/CLAUDE.md` between markers (creating it only if absent)
  rather than overwriting it.
- **No secrets**: only the public, curated contents of this repo are installed.
