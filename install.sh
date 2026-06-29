#!/usr/bin/env bash
#
# Installs Amadej Demšar's Claude Code setup into the current machine:
#   - the Lavish Editor (lavish-axi) + its SessionStart hook
#   - every skill in   skills/
#   - every agent in   agents/
#   - every command in commands/
#
# Idempotent and non-destructive: it overwrites only the items it ships
# (same-named skills/agents/commands), never deletes anything else, and adds
# the SessionStart hook only if one is not already present.
#
# Requirements: git, Node.js >= 22 (npm ships with Node).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/amadejdemsar-create/my-claude-setup/main/install.sh | bash
# or, from a checkout:
#   bash install.sh
#
set -euo pipefail

REPO_URL="https://github.com/amadejdemsar-create/my-claude-setup.git"

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
AGENTS_DIR="$CLAUDE_DIR/agents"
COMMANDS_DIR="$CLAUDE_DIR/commands"
SETTINGS="$CLAUDE_DIR/settings.json"

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

# --- 1. prerequisites -------------------------------------------------------
command -v git  >/dev/null 2>&1 || die "git is required. Install git and re-run."
command -v node >/dev/null 2>&1 || die "Node.js >= 22 is required. Install it from https://nodejs.org then re-run."
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
[ "$NODE_MAJOR" -ge 22 ] || die "Node.js $NODE_MAJOR detected; need >= 22. Upgrade Node, then re-run."
say "Node.js $(node -v) OK"

# --- 2. locate the setup source (local checkout or fresh shallow clone) -----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd 2>/dev/null || echo '')"
if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/skills" ] && [ -d "$SCRIPT_DIR/agents" ]; then
  SRC="$SCRIPT_DIR"
  say "Using local checkout: $SRC"
else
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  say "Fetching setup from $REPO_URL ..."
  git clone --depth 1 --quiet "$REPO_URL" "$TMP/repo"
  SRC="$TMP/repo"
fi

# --- 3. install lavish-axi (for the SessionStart hook) ----------------------
# Skills fall back to `npx -y lavish-axi`, so a failed global install is non-fatal.
if command -v lavish-axi >/dev/null 2>&1; then
  say "lavish-axi already installed ($(lavish-axi --version 2>/dev/null || echo '?'))"
else
  say "Installing lavish-axi globally via npm..."
  if npm install -g lavish-axi >/dev/null 2>&1; then
    say "lavish-axi installed ($(lavish-axi --version 2>/dev/null || echo '?'))"
  else
    warn "Global npm install failed. Lavish-based skills will use the 'npx -y lavish-axi' fallback."
  fi
fi

# --- 4. copy skills / agents / commands -------------------------------------
copy_tree() {  # $1 = source subdir, $2 = dest dir, $3 = label, $4 = glob (optional)
  local src="$1" dest="$2" label="$3" glob="${4:-*}" n=0
  [ -d "$src" ] || { warn "no $label to install (missing $src)"; return; }
  mkdir -p "$dest"
  shopt -s nullglob
  for item in "$src"/$glob; do
    local base; base="$(basename "$item")"
    if [ -d "$item" ]; then rm -rf "${dest:?}/$base"; cp -R "$item" "$dest/$base";
    else cp "$item" "$dest/$base"; fi
    n=$((n+1))
  done
  shopt -u nullglob
  say "Installed $n $label -> $dest"
}

copy_tree "$SRC/skills"   "$SKILLS_DIR"   "skills"
copy_tree "$SRC/agents"   "$AGENTS_DIR"   "agents"   "*.md"
copy_tree "$SRC/commands" "$COMMANDS_DIR" "commands" "*.md"

# --- 5. wire the SessionStart hook for lavish (idempotent merge) ------------
if command -v lavish-axi >/dev/null 2>&1; then
  HOOK_CMD="$(command -v lavish-axi)"; HOOK_TIMEOUT=10
else
  HOOK_CMD="npx -y lavish-axi"; HOOK_TIMEOUT=30
fi
say "Wiring SessionStart hook into $SETTINGS ..."
mkdir -p "$CLAUDE_DIR"
node - "$SETTINGS" "$HOOK_CMD" "$HOOK_TIMEOUT" <<'NODE'
const fs = require('fs');
const path = require('path');
const [, , file, cmd, timeout] = process.argv;
let s = {};
try { s = JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { s = {}; }
s.hooks = s.hooks || {};
s.hooks.SessionStart = s.hooks.SessionStart || [];
const present = s.hooks.SessionStart.some(block =>
  (block.hooks || []).some(h => typeof h.command === 'string' && h.command.includes('lavish-axi')));
if (present) {
  console.log('hook already present, leaving settings.json unchanged');
} else {
  s.hooks.SessionStart.push({ matcher: '', hooks: [{ type: 'command', command: cmd, timeout: Number(timeout) }] });
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(s, null, 2) + '\n');
  console.log('hook added: ' + cmd);
}
NODE

# --- 6. done ----------------------------------------------------------------
echo
say "Done. Restart Claude Code so the SessionStart hook and new skills/agents load."
echo "   Test Lavish:  echo '<h1>hi</h1>' > /tmp/lavish-test.html && lavish-axi /tmp/lavish-test.html"
echo "   New skills include /visual-plan and /visual-recap; agents and commands are in ~/.claude/."
