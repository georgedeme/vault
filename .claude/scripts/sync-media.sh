#!/usr/bin/env bash
# Mirror every non-note file under the vault's Public/ folder (PDFs,
# images, SVGs, ...) to content/ in the Quartz site repo: add new files,
# update changed ones, and remove files that no longer exist in the vault.
#
# Quartz Syncer publishes notes and the images they embed, but it doesn't
# publish PDFs and never removes old media. Its own media cleanup treats
# every PDF as unused, so it can't be used. Notes (*.md) are left to the
# plugin.
#
# Usage: bash .claude/scripts/sync-media.sh [--dry-run]
# Runs after `quartz-syncer:sync force` in the publish Stop hook.

set -euo pipefail

DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1

VAULT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$VAULT/Public"
REMOTE="https://github.com/georgedeme/my-notes-site.git"
BRANCH="v5"
CACHE="${HOME}/.cache/quartz-media-sync"   # outside the vault on purpose
# git is a native Windows exe: hand it C:/... paths, not /c/...
command -v cygpath >/dev/null && CACHE="$(cygpath -m "$CACHE")"

git_() { git -C "$CACHE" -c core.quotepath=off "$@"; }

# Sparse clone that only checks out non-note files under content/.
if [[ ! -d "$CACHE/.git" ]]; then
  mkdir -p "$(dirname "$CACHE")"
  git clone -q --filter=blob:none --no-checkout -b "$BRANCH" "$REMOTE" "$CACHE"
  # MSYS_NO_PATHCONV keeps Git Bash from rewriting the leading "/".
  MSYS_NO_PATHCONV=1 git_ sparse-checkout set --no-cone '/content/**' '!/content/**/*.md'
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
done < <(find "$SRC" -type f ! -iname '*.md' -print0)

# Remove files that are on the site but no longer in the vault.
while IFS= read -r rel; do
  [[ -z "$rel" || "$rel" == *.md ]] && continue
  if [[ ! -f "$SRC/$rel" ]]; then
    echo "- $rel"; changed=1
    (( DRY )) || git_ rm -q --sparse -- "content/$rel"
  fi
done < <(git_ ls-files -- content | sed 's#^content/##')

if (( !changed )); then echo "Media already in sync."; exit 0; fi
(( DRY )) && { echo "(dry run, nothing pushed)"; exit 0; }

git_ -c user.name="georgedeme" -c user.email="demetriougeorge84@gmail.com" \
  commit -q -m "Sync media from vault"
GCM_INTERACTIVE=never git_ push -q origin "$BRANCH"
echo "Media synced: $(git_ rev-parse --short HEAD)"
