# Vault Sync & Visibility

- **`Public/`** is automatically pushed and published to a public GitHub Pages (Quartz) website. Treat everything inside `Public/` as public-facing and follow the Quartz/publishing rules below.
- **Auto-publish `Public/Uni/` changes:** Whenever you create, edit, move, or delete notes under `Public/Uni/` (or anywhere in `Public/`), automatically publish the changes to the Quartz site using the publishing workflow in `CLAUDE.md` (`export-drawings.sh`, `obsidian.com quartz-syncer:mark path="Public/**" state=publish`, `obsidian.com quartz-syncer:sync force`, and `sync-media.sh`) — don't wait to be asked.
- **The entire vault** is pushed to a GitHub repository. Avoid placing sensitive information or stray temporary/scratch files anywhere in the vault.

# Conventions

Follow all vault conventions defined in `CLAUDE.md`:

@[CLAUDE.md](CLAUDE.md)
