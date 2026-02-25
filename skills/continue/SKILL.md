---
name: continue
description: "Generate a continue prompt file so work can be resumed in a new session when context window is running low. Also handles resuming from a previous continue prompt.\n\n<example>\nuser: \"/continue\"\nassistant: Creates a continue prompt file summarizing current state\n</example>\n\n<example>\nuser: \"continue from where we left off\"\nassistant: Reads the continue prompt, resumes work, then deletes the file\n</example>"
user_invocable: true
---

# Continue Prompt Skill

You are generating a continuation prompt so work can be seamlessly resumed in a new Claude Code session.

## File Location

Always write the continue prompt to: `~/.claude/continue-prompt.md`

## When `/continue` is invoked (GENERATING a continue prompt)

Analyze the full conversation history and create a comprehensive continue prompt file. The file must contain everything the next session needs to pick up exactly where this one left off.

### Structure of the continue prompt file:

```markdown
# Continue Prompt

> **INSTRUCTIONS FOR NEW SESSION:** Read this file carefully, then resume the work described below. After you have fully read and understood this file, DELETE it (`rm ~/.claude/continue-prompt.md`). Confirm to the user that you've loaded the context and are ready to continue.

## Task Description
[What the user originally asked for / the overall goal]

## Current Status
[What has been completed so far, with specifics]

## Files Modified
[List every file that was created, modified, or deleted with brief description of changes]

## Files Being Worked On
[Key files the next session should read to understand the current state]

## What Remains To Do
[Specific next steps, in order of priority]

## Key Decisions Made
[Any architectural choices, user preferences, or decisions that were made during the session that the next session needs to know about]

## Context & Gotchas
[Anything non-obvious: bugs encountered, workarounds applied, things that didn't work, user preferences expressed during the session]
```

### Guidelines for writing the continue prompt:

1. **Be specific, not vague.** Instead of "working on the auth system", write "implementing JWT refresh token rotation in `src/auth/tokens.ts`, the access token generation is done but refresh token storage in Redis is not yet implemented."

2. **Include file paths.** Always use absolute paths so the next session can find everything immediately.

3. **Capture user preferences.** If the user expressed any preferences during the session (naming conventions, library choices, approaches), record them.

4. **List exact next steps.** The next session should be able to start working immediately without needing to re-analyze what to do.

5. **Keep it concise but complete.** Don't pad with filler. Every line should carry information.

After writing the file, tell the user:
- The continue prompt has been saved to `~/.claude/continue-prompt.md`
- In their next session, they just need to say: **"continue from where we left off"** or **"read ~/.claude/continue-prompt.md and continue"**

## When user wants to RESUME from a continue prompt

If the user says anything like "continue from where we left off", "pick up where we left off", "resume", or "read the continue prompt":

1. **Read** `~/.claude/continue-prompt.md`
2. **Read the key files** listed in the "Files Being Worked On" section to load current state
3. **Delete** the continue prompt file: `rm ~/.claude/continue-prompt.md`
4. **Confirm** to the user: briefly state what the task is and what you're about to do next
5. **Continue working** on the remaining tasks
