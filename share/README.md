# Share this Claude Code setup

A one-paste way to give anyone the full setup in this repo: the **Lavish Editor**
plus **every skill, agent, and command** here.

## The easy way: paste the prompt

Open [`PROMPT.md`](./PROMPT.md), copy the whole block, paste it into a fresh
Claude Code session. The recipient's agent fetches the installer, shows what it
does, runs it, and verifies.

## The manual way: run the installer

```bash
curl -fsSL https://raw.githubusercontent.com/amadejdemsar-create/my-claude-setup/main/install.sh | bash
```

Or clone the repo and run `bash install.sh` from the checkout.

## What it installs

| Piece | Destination |
|---|---|
| `lavish-axi` (public npm pkg) + SessionStart hook | global + `~/.claude/settings.json` |
| every skill in `skills/` | `~/.claude/skills/` |
| every agent in `agents/` | `~/.claude/agents/` |
| every command in `commands/` | `~/.claude/commands/` |

## Requirements

- **Node.js >= 22** (npm ships with it) — <https://nodejs.org>
- `git`

## Guarantees

- **Idempotent**: re-running never duplicates the SessionStart hook.
- **Non-destructive**: it overwrites only same-named items it ships; it never
  deletes the recipient's other skills/agents/commands, and it merges into any
  existing `SessionStart` hooks rather than replacing them.
- **No secrets**: only the public, curated contents of this repo are installed;
  the installer fetches from this public repo, not from any private machine.

## Adding more to the share

The installer loops over `skills/`, `agents/`, and `commands/`, so anything added
to those folders here is automatically included next time someone installs.
