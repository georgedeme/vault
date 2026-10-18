// Export every Excalidraw drawing under Public/ to a PNG next to it
// (`X.excalidraw.md` -> `X.png`), so notes can embed `![[X.png|800]]` and
// the published site shows the drawing as an image.
//
// Why PNG and not SVG: the site can't render embedded `.excalidraw` files,
// and Quartz embeds `.svg` wikilinks as <object data="…"> with a path that
// is never made relative to the page, so SVG embeds show up blank. PNG
// embeds become <img>, whose paths Quartz does fix.
//
// Runs inside Obsidian (needs the Excalidraw plugin). Only re-exports a
// drawing when it's newer than its PNG, unless called with force = true.
// Called by export-drawings.sh.
(async (force) => {
  const ea = window.ExcalidrawAutomate?.getAPI?.();
  if (!ea) return 'ERROR: Excalidraw plugin not available';
  const drawings = app.vault.getFiles().filter(
    (f) => f.path.startsWith('Public/') && f.path.endsWith('.excalidraw.md'));
  const done = [];
  for (const f of drawings) {
    const pngPath = f.path.replace(/\.excalidraw\.md$/, '.png');
    const pngFile = app.vault.getAbstractFileByPath(pngPath);
    if (!force && pngFile && pngFile.stat.mtime >= f.stat.mtime) continue;
    try {
      ea.reset();
      // Dark theme with its background (like the PNG previews), so it reads
      // the same in the site's light and dark modes. 2x scale for sharp text.
      const blob = await ea.createPNG(f.path, 2,
        { withBackground: true, withTheme: true }, undefined, 'dark', 12);
      const data = await blob.arrayBuffer();
      if (pngFile) await app.vault.modifyBinary(pngFile, data);
      else await app.vault.createBinary(pngPath, data);
      done.push(pngPath);
    } catch (e) {
      done.push('ERROR ' + f.path + ': ' + e.message);
    }
  }
  return done.length ? 'Exported:\n' + done.join('\n') : 'Drawing PNGs up to date.';
})
