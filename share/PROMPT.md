# Copy-paste prompt (give this to the recipient)

Paste everything between the lines into a fresh Claude Code session.

---

Install Amadej Demšar's Claude Code setup (skills, agents, commands, and the Lavish editor) on my machine.

Do this, in order:

1. Check that Node.js >= 22 is installed (`node -v`) and `git` exists. If Node is missing or older than 22, STOP and tell me to install Node.js >= 22 from https://nodejs.org first, then I'll re-run this.

2. Download this installer, give me a one-paragraph summary of what it does, then run it once I confirm:
   ```
   curl -fsSL https://raw.githubusercontent.com/amadejdemsar-create/my-claude-setup/main/install.sh -o /tmp/claude-setup-install.sh
   ```
   It: (a) installs the public npm package `lavish-axi`, (b) copies every skill into `~/.claude/skills/`, every agent into `~/.claude/agents/`, and every command into `~/.claude/commands/`, and (c) appends a SessionStart hook to `~/.claude/settings.json` (merging, never overwriting existing hooks). It is idempotent and never deletes my other skills/agents. Then run:
   ```
   bash /tmp/claude-setup-install.sh
   ```

3. After it finishes, tell me to restart Claude Code so the SessionStart hook and the new skills/agents load.

4. Verify and report back: the `lavish-axi` version, and the counts of skills/agents/commands now under `~/.claude/` (e.g. `ls ~/.claude/skills ~/.claude/agents ~/.claude/commands`). Confirm `/visual-plan` and `/visual-recap` are present.

For context: this is a curated, public-safe Claude Code setup. Lavish renders rich HTML artifacts as an interactive browser review surface; `/visual-plan` and `/visual-recap` are built on it. The other skills/agents/commands cover research, design, writing, finance, and ops workflows.

---
