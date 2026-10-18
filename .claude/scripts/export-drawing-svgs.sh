#!/usr/bin/env bash
# Export Excalidraw drawings under Public/ to SVG through the running
# Obsidian app (see export-drawing-svgs.js).
# Usage: bash .claude/scripts/export-drawing-svgs.sh [--force]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
command -v cygpath >/dev/null && here="$(cygpath -m "$here")"
force=false; [[ "${1:-}" == "--force" ]] && force=true
cd "$here/../.."
timeout 600 obsidian.com eval code="(async()=>{const f=eval(require('fs').readFileSync('$here/export-drawing-svgs.js','utf8'));return await f($force)})()"
