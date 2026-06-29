#!/usr/bin/env bash
#
# Lavish bundle installer.
# Installs the Lavish Editor (lavish-axi) plus the two skills built on it
# (visual-plan, visual-recap), and adds a short Lavish section to the global
# CLAUDE.md so an agent knows when to use them.
#
# Idempotent and non-destructive: it overwrites only the two skills it ships,
# never deletes anything else, adds the SessionStart hook only if absent, and
# adds the CLAUDE.md section only once (between markers). It never overwrites an
# existing CLAUDE.md; it appends a marked block (creating the file if missing).
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
SKILLS=("visual-plan" "visual-recap")

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
SETTINGS="$CLAUDE_DIR/settings.json"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
MARK_BEGIN="<!-- BEGIN lavish-bundle -->"
MARK_END="<!-- END lavish-bundle -->"

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

# --- 1. prerequisites -------------------------------------------------------
command -v git  >/dev/null 2>&1 || die "git is required. Install git and re-run."
command -v node >/dev/null 2>&1 || die "Node.js >= 22 is required. Install it from https://nodejs.org then re-run."
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
[ "$NODE_MAJOR" -ge 22 ] || die "Node.js $NODE_MAJOR detected; need >= 22. Upgrade Node, then re-run."
say "Node.js $(node -v) OK"

# --- 2. locate the source (local checkout or fresh shallow clone) -----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd 2>/dev/null || echo '')"
if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/skills/visual-plan" ]; then
  SRC="$SCRIPT_DIR"
  say "Using local checkout: $SRC"
else
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  say "Fetching from $REPO_URL ..."
  git clone --depth 1 --quiet "$REPO_URL" "$TMP/repo"
  SRC="$TMP/repo"
fi

# --- 3. install lavish-axi (for the SessionStart hook) ----------------------
# The skills fall back to `npx -y lavish-axi`, so a failed global install is non-fatal.
if command -v lavish-axi >/dev/null 2>&1; then
  say "lavish-axi already installed ($(lavish-axi --version 2>/dev/null || echo '?'))"
else
  say "Installing lavish-axi globally via npm..."
  if npm install -g lavish-axi >/dev/null 2>&1; then
    say "lavish-axi installed ($(lavish-axi --version 2>/dev/null || echo '?'))"
  else
    warn "Global npm install failed. The skills will use the 'npx -y lavish-axi' fallback."
  fi
fi

# --- 4. install the two skills ---------------------------------------------
mkdir -p "$SKILLS_DIR"
for s in "${SKILLS[@]}"; do
  [ -d "$SRC/skills/$s" ] || die "skill '$s' not found in source (unexpected)."
  rm -rf "${SKILLS_DIR:?}/$s"
  cp -R "$SRC/skills/$s" "$SKILLS_DIR/$s"
  say "Installed skill: $s -> $SKILLS_DIR/$s"
done

# --- 5. add the Lavish section to CLAUDE.md (idempotent, non-destructive) ----
if [ -f "$SRC/share/CLAUDE-lavish.md" ]; then
  mkdir -p "$CLAUDE_DIR"
  touch "$CLAUDE_MD"
  if grep -qF "$MARK_BEGIN" "$CLAUDE_MD" 2>/dev/null; then
    say "Lavish section already in CLAUDE.md, leaving it unchanged"
  else
    {
      printf '\n%s\n' "$MARK_BEGIN"
      cat "$SRC/share/CLAUDE-lavish.md"
      printf '%s\n' "$MARK_END"
    } >> "$CLAUDE_MD"
    say "Added Lavish section to $CLAUDE_MD"
  fi
fi

# --- 6. wire the SessionStart hook for lavish (idempotent merge) ------------
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

# --- 7. done ----------------------------------------------------------------
echo
say "Done. Restart Claude Code so the SessionStart hook, CLAUDE.md section, and skills load."
echo "   Test Lavish:  echo '<h1>hi</h1>' > /tmp/lavish-test.html && lavish-axi /tmp/lavish-test.html"
echo "   Skills installed: /visual-plan and /visual-recap."
