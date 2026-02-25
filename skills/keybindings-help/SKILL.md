---
name: keybindings-help
description: "Use when the user wants to customize keyboard shortcuts, rebind keys, add chord bindings, or modify ~/.claude/keybindings.json. Examples: \"rebind ctrl+s\", \"add a chord shortcut\", \"change the submit key\", \"customize keybindings\"."
user_invocable: true
---

# Keybindings Help

You are helping the user customize Claude Code keyboard shortcuts.

## Keybindings File

Location: `~/.claude/keybindings.json`

This file controls keyboard shortcuts in Claude Code. If it doesn't exist yet, create it.

## Format

The file is a JSON array of keybinding objects:

```json
[
  {
    "key": "ctrl+s",
    "command": "submit",
    "when": "inputFocused"
  }
]
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `key` | Yes | Key combination (e.g., `ctrl+s`, `alt+enter`, `shift+tab`) |
| `command` | Yes | The command to execute |
| `when` | No | Context condition for when the binding is active |

### Key Syntax

- Modifiers: `ctrl`, `alt`, `shift`, `meta` (cmd on Mac)
- Separator: `+` between modifier and key
- Chord bindings: Two key combos separated by space (e.g., `ctrl+k ctrl+c`)
- Common keys: `enter`, `tab`, `escape`, `space`, `backspace`, `delete`, `up`, `down`, `left`, `right`, letters, numbers

### Available Commands

| Command | Default Key | Description |
|---------|-------------|-------------|
| `submit` | `Enter` | Submit the current input |
| `newline` | `Shift+Enter` | Insert a newline |
| `plan_mode_toggle` | `Shift+Tab` | Toggle plan mode on/off |
| `interrupt` | `Escape` | Interrupt current generation |
| `clear` | None | Clear conversation |

## Workflow

1. **Read** the current `~/.claude/keybindings.json` (or note it doesn't exist)
2. **Ask** what the user wants to change if not clear
3. **Write** the updated keybindings file
4. **Tell** the user to restart Claude Code for changes to take effect

## Examples

### Change submit key to Ctrl+Enter
```json
[
  { "key": "ctrl+enter", "command": "submit" },
  { "key": "enter", "command": "newline" }
]
```

### Add a chord binding
```json
[
  { "key": "ctrl+k ctrl+p", "command": "plan_mode_toggle" }
]
```

## Important Notes

- Keybindings override defaults. If you rebind `enter`, make sure `submit` is still assigned somewhere.
- The file must be valid JSON. Always validate before writing.
- Changes require restarting Claude Code.
