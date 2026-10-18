#!/usr/bin/env bash
# Export Excalidraw drawings under Public/ to PNG through the running
# Obsidian app (see export-drawings.js).
# Usage: bash .claude/scripts/export-drawings.sh [--force]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
command -v cygpath >/dev/null && here="$(cygpath -m "$here")"
force=false; [[ "${1:-}" == "--force" ]] && force=true
cd "$here/../.."
timeout 600 obsidian.com eval code="(async()=>{const f=eval(require('fs').readFileSync('$here/export-drawings.js','utf8'));return await f($force)})()"
