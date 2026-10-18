#!/usr/bin/env bash
# Mirror every PDF under the vault's Public/ folder to content/ in the
# Quartz site repo. Adds new PDFs, updates changed ones, and removes PDFs
# that no longer exist in the vault. Quartz Syncer doesn't publish PDFs on
# its own, and its media cleanup treats every PDF as unused, so this
# script handles them instead.
#
# Usage: bash .claude/scripts/sync-pdfs.sh [--dry-run]
# Runs after `quartz-syncer:sync force` in the publish Stop hook.

set -euo pipefail

DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1

VAULT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$VAULT/Public"
REMOTE="https://github.com/georgedeme/my-notes-site.git"
BRANCH="v5"
CACHE="${HOME}/.cache/quartz-pdf-sync"   # outside the vault on purpose
# git is a native Windows exe: hand it C:/... paths, not /c/...
command -v cygpath >/dev/null && CACHE="$(cygpath -m "$CACHE")"

git_() { git -C "$CACHE" -c core.quotepath=off "$@"; }

# Sparse clone that only ever checks out PDFs under content/.
if [[ ! -d "$CACHE/.git" ]]; then
  mkdir -p "$(dirname "$CACHE")"
  git clone -q --filter=blob:none --no-checkout -b "$BRANCH" "$REMOTE" "$CACHE"
  # MSYS_NO_PATHCONV keeps Git Bash from rewriting the leading "/".
  MSYS_NO_PATHCONV=1 git_ sparse-checkout set --no-cone '/content/**/*.pdf'
fi
git_ fetch -q origin "$BRANCH"
git_ checkout -q -B "$BRANCH" "origin/$BRANCH"
git_ reset -q --hard "origin/$BRANCH"

DST="$CACHE/content"
changed=0

# Add or update.
while IFS= read -r -d '' f; do
  rel="${f#"$SRC"/}"
  if ! cmp -s "$f" "$DST/$rel" 2>/dev/null; then
    echo "+ $rel"; changed=1
    if (( !DRY )); then
      mkdir -p "$(dirname "$DST/$rel")"
      cp "$f" "$DST/$rel"
      git_ add --sparse -- "content/$rel"
    fi
  fi
done < <(find "$SRC" -type f -iname '*.pdf' -print0)

# Remove PDFs that are on the site but no longer in the vault.
while IFS= read -r rel; do
  [[ -z "$rel" ]] && continue
  if [[ ! -f "$SRC/$rel" ]]; then
    echo "- $rel"; changed=1
    (( DRY )) || git_ rm -q --sparse -- "content/$rel"
  fi
done < <(git_ ls-files -- 'content/*.pdf' 'content/*.PDF' | sed 's#^content/##')

if (( !changed )); then echo "PDFs already in sync."; exit 0; fi
(( DRY )) && { echo "(dry run, nothing pushed)"; exit 0; }

git_ -c user.name="georgedeme" -c user.email="demetriougeorge84@gmail.com" \
  commit -q -m "Sync PDFs from vault"
GCM_INTERACTIVE=never git_ push -q origin "$BRANCH"
echo "PDFs synced: $(git_ rev-parse --short HEAD)"
