#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Push "Building with Sarvam" to GitHub.
#
# Run this ON YOUR OWN MACHINE, from the folder that holds README.md, Labs/ and
# Slides/. It never touches your API key and it shows you exactly what will be
# published before anything leaves your laptop.
#
#     chmod +x push_to_github.sh
#     ./push_to_github.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO_NAME="building-with-sarvam"
GH_USER="dharmanibc"
# Visibility of the repo when this script CREATES it (via `gh`).
#   "private" — staged; only you can see it. Flip to public from GitHub later:
#                 gh repo edit dharmanibc/building-with-sarvam --visibility public
#               (or Settings → General → Danger Zone → Change visibility)
#   "public"  — visible immediately.
# Note: this only applies on first creation. Once the repo exists on GitHub,
# changing this line does nothing — change it on GitHub instead.
VISIBILITY="private"

say()  { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()  { printf '  \033[31m✗ %s\033[0m\n' "$*"; exit 1; }

# ── 0 · sanity ───────────────────────────────────────────────────────────────
say "0 · Checking we are in the right folder"
[[ -f README.md && -d Labs && -d Slides ]] \
  || die "Run this from the repo root (the folder containing README.md, Labs/, Slides/)."
ok "found README.md, Labs/, Slides/"

command -v git >/dev/null || die "git is not installed."
ok "git $(git --version | awk '{print $3}')"

# ── 1 · licence ──────────────────────────────────────────────────────────────
say "1 · Licence"
if [[ -f LICENSE ]]; then
  ok "LICENSE present"
else
  warn "No LICENSE file yet."
  echo "     Fetching the canonical Apache 2.0 text..."
  if curl -fsSL https://www.apache.org/licenses/LICENSE-2.0.txt -o LICENSE; then
    cat >> LICENSE <<'EOF'

   Copyright 2026 Dr. Bhaveshkumar C. Dharmani (AIVidhya4Sarvam)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
EOF
    rm -f LICENSE.PLACEHOLDER.md
    ok "LICENSE written (Apache 2.0)"
  else
    warn "Could not fetch it. Add the licence via the GitHub UI after pushing:"
    warn "  Add file → Create new file → name it LICENSE → Choose a license template"
  fi
fi

# ── 2 · secret sweep ─────────────────────────────────────────────────────────
say "2 · Secret sweep (belt and braces — this already passed once)"
LEAKS=$(grep -rIn --exclude-dir=.git --exclude-dir=node_modules \
        -E 'sk_[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' . \
        2>/dev/null | grep -v 'sk_your_key_here' | grep -v 'sk_xxxx' || true)
if [[ -n "$LEAKS" ]]; then
  echo "$LEAKS" | head -20
  die "Possible secret above. Nothing pushed. Remove it and re-run."
fi
ok "no API keys, AWS keys or private keys found"

if git check-ignore -q .env 2>/dev/null || grep -q '^\.env$' .gitignore; then
  ok ".env is gitignored"
else
  warn ".env is NOT ignored — check .gitignore before continuing"
fi

# ── 3 · git init ─────────────────────────────────────────────────────────────
say "3 · Repository"
if [[ -d .git ]]; then
  ok "git repo already initialised"
else
  git init -q -b main
  ok "initialised, branch 'main'"
fi

git config user.name  >/dev/null 2>&1 || git config user.name  "Bhaveshkumar C. Dharmani"
git config user.email >/dev/null 2>&1 || git config user.email "bhavesh@aividhya.in"
ok "author: $(git config user.name) <$(git config user.email)>"

# ── 4 · what will be published ───────────────────────────────────────────────
say "4 · What will be published"
git add -A
FILES=$(git diff --cached --name-only | wc -l | tr -d ' ')
SIZE=$(git diff --cached --name-only | xargs -I{} sh -c 'test -f "{}" && wc -c < "{}"' 2>/dev/null \
       | awk '{s+=$1} END {printf "%.1f", s/1048576}')
echo "     ${FILES} files, ~${SIZE} MB"
echo

# Anything outside the four expected folders, or matching a junk pattern, is
# shown FIRST and in full. The old version of this script printed the first 25
# filenames alphabetically, which buried exactly the surprises you needed to
# see. Surprises now come to the top and are never truncated.
UNEXPECTED=$(git diff --cached --name-only | grep -vE \
  '^(Labs|Slides|pdf|skills)/|^(README|CHANGELOG|CONTRIBUTING|LICENSE|requirements\.txt|push_to_github\.sh|\.gitignore|\.env\.example)' || true)
JUNK=$(git diff --cached --name-only | grep -iE \
  'DS_Store|~\$|[ _-]copy[ .]|Labs_v2/|_backup_|\.bundle$|\.docx$|checkpoints|node_modules' || true)

if [[ -n "$UNEXPECTED$JUNK" ]]; then
  printf '  \033[33m! Files outside the expected set — read these carefully:\033[0m\n'
  printf '%s\n%s\n' "$UNEXPECTED" "$JUNK" | sort -u | sed '/^$/d;s|^|       |'
  echo
fi

echo "     Full list:"
git diff --cached --name-only | sed 's|^|       |'
echo
echo "     .gitignore is an ALLOWLIST — anything not named there is invisible"
echo "     to git, so scratch files cannot be swept in by 'git add -A'."
echo
read -r -p "  Continue? [y/N] " REPLY
[[ "$REPLY" =~ ^[Yy]$ ]] || { echo "  Aborted. Nothing pushed."; exit 0; }

# ── 5 · commit ───────────────────────────────────────────────────────────────
say "5 · Commit"
if git diff --cached --quiet; then
  ok "nothing new to commit"
else
  git commit -q -m "Building with Sarvam — an open teaching kit for the Sarvam AI stack

13 hands-on Jupyter labs, 10 slide decks and 2 Agent Skills covering the Sarvam
platform end to end: chat, speech, the language layer, document AI, agents,
voice agents, framework interop, MCP, and unit economics.

85% of code cells carry real executed outputs. Labs/SESSION_FINDINGS_2026-08.md
records the corrections that live testing turned up, and how each was established."
  ok "committed"
fi

# ── 6 · create + push ────────────────────────────────────────────────────────
say "6 · Push to GitHub"
if git remote get-url origin >/dev/null 2>&1; then
  ok "remote 'origin' already set: $(git remote get-url origin)"
  git push -u origin main
elif command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  ok "GitHub CLI is authenticated — creating the repo"
  gh repo create "$REPO_NAME" \
     --"$VISIBILITY" \
     --source=. --remote=origin --push \
     --description "An open teaching kit for the Sarvam AI stack — 13 hands-on labs, 10 decks, and 2 Agent Skills. Every API call priced in rupees."
else
  warn "GitHub CLI not available or not logged in."
  echo
  echo "     Do these two steps:"
  echo
  echo "     1. Create an EMPTY repo (no README, no .gitignore, no licence) at:"
  echo "        https://github.com/new    →  name it: $REPO_NAME"
  echo "        →  set visibility: $VISIBILITY"
  echo
  echo "     2. Then run:"
  echo "        git remote add origin https://github.com/$GH_USER/$REPO_NAME.git"
  echo "        git push -u origin main"
  echo
  exit 0
fi

say "Done"
echo "  https://github.com/$GH_USER/$REPO_NAME"
echo
if [[ "$VISIBILITY" == "private" ]]; then
  echo "  Repo is PRIVATE. When you are happy with it, make it public:"
  echo "    gh repo edit $GH_USER/$REPO_NAME --visibility public --accept-visibility-change-consequences"
  echo "  (or Settings → General → Danger Zone → Change visibility)"
  echo
fi
echo "  Worth doing next:"
echo "    · Add topics: sarvam-ai, indic-nlp, speech-to-text, text-to-speech,"
echo "      llm, mcp, agent-skills, jupyter, india, ai-education"
echo "    · Set the About blurb and pin the repo on your profile"
echo "    · Attach the .pptx set to a Release (they are gitignored on purpose —"
echo "      21 MB of binaries would bloat the history; the PDFs in pdf/ are the"
echo "      readable copy and GitHub previews them inline)"
