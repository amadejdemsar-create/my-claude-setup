# my-claude-setup Site Editing (Mandatory)

**When adding ANY new agent, MCP server, or skill card to `/Users/Shared/Domain/Code/Personal/my-claude-setup/index.html`, the card MUST be wired to the modal system. A card that isn't clickable is NOT done.**

Origin: 2026-04-21. Added `/visualize` card to index.html but skipped the `skills[]` data object entry. The card rendered but wasn't clickable. User already told me the wiring pattern before. Can't happen again.

## The three objects that drive modals

`index.html` wires cards via DOMContentLoaded auto-wire code (around line 5946). Cards become clickable only when their `<h3>` text matches a key in one of three objects:

| Card type | Section | Object | Function called |
|-----------|---------|--------|-----------------|
| Agent (card-blue / card-cyan / card-pink / card-purple / card-green / card-amber / card-teal) | anywhere | `agents` (line 3123) | `openModal('agent-name')` via inline `onclick` |
| MCP server (mcp-card) | MCP section | `mcpServers` (line 3955) | `openMcpModal('Server Name')` via inline `onclick` |
| Skill (card card-pink in `#skills`) | `#skills` section | `skills` (line 5147) | auto-wired by DOMContentLoaded → `openGenericModal` |

## Checklist for EVERY addition

Before committing any change to `my-claude-setup/index.html` that adds a new card:

1. **Card HTML:** matches the pattern of neighboring cards (icon, title, paragraph, tags).
2. **Data object entry:** a key matching the card's `<h3>` EXACTLY is present in the right object:
   - Agents → `agents['agent-name']`
   - MCP → `mcpServers['Server Name']`
   - Skills → `skills['/skill-name']`
3. **Data object entry has ALL required fields:**
   - `icon`, `iconBg`, `color`
   - `installPrompt` (a copy-paste block for Claude Code)
   - `content` (HTML body for the modal)
4. **Agent + MCP cards ONLY:** add `card-clickable` class and `onclick="openModal('key')"` or `onclick="openMcpModal('key')"` inline. Skills cards are auto-wired so do NOT add the inline handler.
5. **Verify the match key:**
   - Skills: `<h3>` text must include the leading slash. `/visualize` in the card → `'/visualize'` in the data object.
   - Agents: no slash, just the kebab-case name.
   - MCP: display name as shown on card.
6. **Physically test the click** by opening the local `index.html` in a browser and clicking the new card. If a modal doesn't open, the wiring is broken and the work is not done.
7. **Commit message** should include both "add card" and "wire modal" in the description so the next person (or future me) doesn't forget the pair.

## Don't forget

- If the skill has a SKILL.md that changed locally, copy it to the repo too: `cp ~/.claude/skills/<name>/SKILL.md /Users/Shared/Domain/Code/Personal/my-claude-setup/skills/<name>/SKILL.md`.
- Agents: `cp ~/.claude/agents/<name>.md /Users/Shared/Domain/Code/Personal/my-claude-setup/agents/<name>.md`.
- This is a CONTENT site. If something you're showcasing changes locally, the site copy drifts; always sync the canonical file alongside the modal entry.

## Anti-pattern (what I did on 2026-04-21)

Added only the card. Skipped the `skills['/visualize']` data entry. Commit looked clean, push went through, live site rendered the card, but it was dead — no modal, no copy-install button, no content. User was (rightly) furious.

**Never do card-only additions again. The data entry is half the work, and the more important half.**
