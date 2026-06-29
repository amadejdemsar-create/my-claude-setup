#!/usr/bin/env bash
#
# Installs the Lavish Editor (lavish-axi) plus the visual-plan and visual-recap
# Claude Code skills, and wires the SessionStart hook that auto-loads Lavish.
#
# Safe to run more than once (idempotent): it never overwrites unrelated skills,
# and it appends the SessionStart hook only if one is not already present.
#
# Requirements: git, Node.js >= 22 (npm comes with Node).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/amadejdemsar-create/my-claude-setup/main/share/lavish-visual-skills/install.sh | bash
# or download, read, then run:
#   bash install.sh
#
set -euo pipefail

REPO_URL="https://github.com/amadejdemsar-create/my-claude-setup.git"
SKILLS=("visual-plan" "visual-recap")

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
SETTINGS="$CLAUDE_DIR/settings.json"

say() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

# --- 1. prerequisites -------------------------------------------------------
command -v git >/dev/null 2>&1 || die "git is required. Install git and re-run."
command -v node >/dev/null 2>&1 || die "Node.js >= 22 is required. Install it from https://nodejs.org then re-run."

NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
if [ "$NODE_MAJOR" -lt 22 ]; then
  die "Node.js $NODE_MAJOR detected; lavish-axi needs >= 22. Upgrade Node, then re-run."
fi
say "Node.js $(node -v) OK"

# --- 2. install lavish-axi (for the SessionStart hook) ----------------------
# If the global install fails (e.g. permission on a system Node), the skills
# still work because they fall back to `npx -y lavish-axi`.
if command -v lavish-axi >/dev/null 2>&1; then
  say "lavish-axi already installed ($(lavish-axi --version 2>/dev/null || echo '?'))"
else
  say "Installing lavish-axi globally via npm..."
  if npm install -g lavish-axi >/dev/null 2>&1; then
    say "lavish-axi installed ($(lavish-axi --version 2>/dev/null || echo '?'))"
  else
    warn "Global npm install failed. Skills will use the 'npx -y lavish-axi' fallback instead."
  fi
fi

# --- 3. fetch and install the skills ---------------------------------------
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
say "Fetching skills from $REPO_URL ..."
git clone --depth 1 --quiet "$REPO_URL" "$TMP/repo"

mkdir -p "$SKILLS_DIR"
for s in "${SKILLS[@]}"; do
  [ -d "$TMP/repo/skills/$s" ] || die "skill '$s' not found in repo (unexpected)."
  rm -rf "${SKILLS_DIR:?}/$s"
  cp -R "$TMP/repo/skills/$s" "$SKILLS_DIR/$s"
  say "Installed skill: $s -> $SKILLS_DIR/$s"
done

# --- 4. resolve the command + timeout for the hook --------------------------
if command -v lavish-axi >/dev/null 2>&1; then
  HOOK_CMD="$(command -v lavish-axi)"
  HOOK_TIMEOUT=10
else
  HOOK_CMD="npx -y lavish-axi"
  HOOK_TIMEOUT=30   # first npx run downloads the package; give it room
fi

# --- 5. merge the SessionStart hook into settings.json (idempotent) ---------
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
  (block.hooks || []).some(h => typeof h.command === 'string' && h.command.includes('lavish-axi'))
);

if (present) {
  console.log('hook already present, leaving settings.json unchanged');
} else {
  s.hooks.SessionStart.push({
    matcher: '',
    hooks: [{ type: 'command', command: cmd, timeout: Number(timeout) }],
  });
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(s, null, 2) + '\n');
  console.log('hook added: ' + cmd);
}
NODE

# --- 6. done ----------------------------------------------------------------
echo
say "Done. Next steps:"
echo "   1. Restart Claude Code so the SessionStart hook loads."
echo "   2. The Lavish context (description + playbooks) should appear at session start."
echo "   3. Test:  echo '<h1>hi</h1>' > /tmp/lavish-test.html && lavish-axi /tmp/lavish-test.html"
echo "   4. The skills /visual-plan and /visual-recap are now available."
