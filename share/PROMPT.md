# Copy-paste prompt (give this to the recipient)

Paste everything between the lines into a fresh Claude Code session.

---

Install the Lavish bundle in my Claude Code: the Lavish editor plus the /visual-plan and /visual-recap skills and their CLAUDE.md guidance.

Do this, in order:

1. Check that Node.js >= 22 is installed (`node -v`) and `git` exists. If Node is missing or older than 22, STOP and tell me to install Node.js >= 22 from https://nodejs.org first, then I'll re-run this.

2. Download this installer, give me a one-paragraph summary of what it does, then run it once I confirm:
   ```
   curl -fsSL https://raw.githubusercontent.com/amadejdemsar-create/my-claude-setup/main/install.sh -o /tmp/lavish-install.sh
   ```
   It: (a) installs the public npm package `lavish-axi`, (b) copies the `visual-plan` and `visual-recap` skills into `~/.claude/skills/`, (c) adds a short Lavish section to `~/.claude/CLAUDE.md` (creating the file if absent, appending a marked block, never overwriting), and (d) appends a SessionStart hook to `~/.claude/settings.json` (merging, never overwriting). It is idempotent and never deletes my other skills. Then run:
   ```
   bash /tmp/lavish-install.sh
   ```

3. After it finishes, tell me to restart Claude Code so everything loads.

4. Verify and report back: the `lavish-axi` version, that `~/.claude/skills/visual-plan` and `~/.claude/skills/visual-recap` exist, and that the Lavish section is present in `~/.claude/CLAUDE.md`.

For context: Lavish renders rich HTML artifacts as an interactive browser review surface. `/visual-plan` turns a task into a visual plan I approve before work starts; `/visual-recap` summarizes a completed work unit. Both render through `lavish-axi`.

---
