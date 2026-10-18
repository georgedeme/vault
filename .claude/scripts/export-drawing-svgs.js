// Export every Excalidraw drawing under Public/ to an SVG next to it
// (`X.excalidraw.md` -> `X.svg`), so notes can embed `![[X.svg|800]]` and
// the published site shows the drawing as an image. Quartz can't render
// drawings embedded in notes, and Quartz Syncer doesn't convert them.
//
// Runs inside Obsidian (needs the Excalidraw plugin). Only re-exports a
// drawing when it's newer than its SVG, unless called with force = true.
// Called by export-drawing-svgs.sh.
(async (force) => {
  const ea = window.ExcalidrawAutomate?.getAPI?.();
  if (!ea) return 'ERROR: Excalidraw plugin not available';
  const drawings = app.vault.getFiles().filter(
    (f) => f.path.startsWith('Public/') && f.path.endsWith('.excalidraw.md'));
  const done = [];
  for (const f of drawings) {
    const svgPath = f.path.replace(/\.excalidraw\.md$/, '.svg');
    const svgFile = app.vault.getAbstractFileByPath(svgPath);
    if (!force && svgFile && svgFile.stat.mtime >= f.stat.mtime) continue;
    try {
      ea.reset();
      // Dark theme with its background, matching the PNG previews, so it
      // reads the same in the site's light and dark modes. Fonts embedded.
      const svg = await ea.createSVG(f.path, true,
        { withBackground: true, withTheme: true }, undefined, 'dark', 12);
      const text = svg.outerHTML;
      if (svgFile) await app.vault.modify(svgFile, text);
      else await app.vault.create(svgPath, text);
      done.push(svgPath);
    } catch (e) {
      done.push('ERROR ' + f.path + ': ' + e.message);
    }
  }
  return done.length ? 'Exported:\n' + done.join('\n') : 'Drawing SVGs up to date.';
})
