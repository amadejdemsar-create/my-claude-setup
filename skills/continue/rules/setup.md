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

## Required: Add to your global CLAUDE.md

Copy the following section into your `~/.claude/CLAUDE.md` file:

```markdown
## Continue / Resume

When the user says "continue", "continue from where we left off", "pick up where we left off", "resume", or "read the continue prompt" at the START of a session or after a /clear:

1. **Check** if `~/.claude/continue-prompt.md` exists (use Bash: `test -f ~/.claude/continue-prompt.md && echo "EXISTS" || echo "NOT FOUND"`)
2. **If it exists:** Read the file, read the key files listed in "Files Being Worked On", delete the continue prompt file (`rm ~/.claude/continue-prompt.md`), confirm to the user what the task is, and resume working
3. **If it does not exist:** Tell the user no continue prompt was found, and ask what they would like to work on

To GENERATE a continue prompt (save current session for later), use `/continue`.
```

## How it works

| Action | Trigger | Mechanism |
|--------|---------|-----------|
| Save session for later | `/continue` | Skill slash command (deterministic) |
| Resume saved session | "continue" (natural language) | CLAUDE.md rule (deterministic) |

Without the CLAUDE.md rule, saying "continue" in a fresh session may not trigger the skill, and your saved session context will not be loaded.
