---
name: continue-setup
description: |
  Setup instructions for the continue/resume skill.
  Required: add the resume rule to your global CLAUDE.md.
---

# Continue Skill Setup

This skill has two parts that work together:

1. **`/continue` slash command** (this SKILL.md) generates a continue prompt file
2. **CLAUDE.md rule** (below) handles resuming when you say "continue" in a new session

## Why both are needed

Skills with `user_invocable: true` are only triggered deterministically by `/skill-name`. Natural language like "continue" relies on probabilistic description matching, which is unreliable after `/clear` or in a fresh session. The CLAUDE.md rule makes the resume path deterministic.

## Supports multiple sessions

You can run `/continue` in multiple sessions. Each generates a uniquely named file in `~/.claude/continue-prompts/`. When you say "continue" later, Claude lists all saved sessions and lets you pick which one to resume.

## Required: Add to your global CLAUDE.md

Copy the following section into your `~/.claude/CLAUDE.md` file:

```markdown
## Continue / Resume

When the user says "continue", "continue from where we left off", "pick up where we left off", "resume", or "read the continue prompt" at the START of a session or after a /clear:

1. **List** all `.md` files in `~/.claude/continue-prompts/` (use Bash: `ls ~/.claude/continue-prompts/*.md 2>/dev/null`)
2. **If none exist:** Tell the user no continue prompts were found, and ask what they would like to work on
3. **If exactly one exists:** Read it, read the key files listed in "Files Being Worked On", delete that file, confirm to the user what the task is, and resume working
4. **If multiple exist:** List them with numbers (show the filename without `.md` as a human readable label), ask the user which session they want to resume, then read the chosen file, read the key files, delete only that file, confirm, and resume working

To GENERATE a continue prompt (save current session for later), use `/continue`.
```

## How it works

| Action | Trigger | Mechanism |
|--------|---------|-----------|
| Save session for later | `/continue` | Skill slash command (deterministic) |
| Resume saved session | "continue" (natural language) | CLAUDE.md rule (deterministic) |

Without the CLAUDE.md rule, saying "continue" in a fresh session may not trigger the skill, and your saved session context will not be loaded.
