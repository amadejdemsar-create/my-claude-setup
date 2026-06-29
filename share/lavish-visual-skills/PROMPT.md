# Copy-paste prompt (give this to the recipient)

Paste everything between the lines into a fresh Claude Code session.

---

Set up the Lavish Editor and the `visual-plan` / `visual-recap` skills in my Claude Code.

Do this, in order:

1. Check that Node.js >= 22 is installed (`node -v`). If it is missing or older than 22, STOP and tell me to install Node.js >= 22 from https://nodejs.org first, then I'll re-run this.

2. Download this installer, show me a short summary of what it does, then run it:
   ```
   curl -fsSL https://raw.githubusercontent.com/amadejdemsar-create/my-claude-setup/main/share/lavish-visual-skills/install.sh -o /tmp/lavish-install.sh
   ```
   It only: (a) installs the public npm package `lavish-axi`, (b) copies the `visual-plan` and `visual-recap` skills into `~/.claude/skills/`, and (c) appends a SessionStart hook to `~/.claude/settings.json` (merging, not overwriting). Once I confirm, run:
   ```
   bash /tmp/lavish-install.sh
   ```

3. After it finishes, tell me to restart Claude Code so the SessionStart hook loads.

4. Verify and report back: the `lavish-axi` version (`lavish-axi --version`, or `npx -y lavish-axi --version`), and that `~/.claude/skills/visual-plan` and `~/.claude/skills/visual-recap` both exist.

For context: Lavish renders rich HTML artifacts as an interactive review surface in the browser. `/visual-plan` turns a task into a visual plan I approve before work starts; `/visual-recap` summarizes a completed work unit. Both render through `lavish-axi`.

---
