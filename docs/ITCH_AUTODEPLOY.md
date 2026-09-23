# itch.io automatic deployment

Capture My Heart uses itch.io's **butler** CLI to update the browser build after a successful GitHub Pages deployment.

## One-time setup

1. Get a Butler/Wharf API key from your itch.io account's API key settings.
2. In GitHub open:
   - Repository **Settings**
   - **Secrets and variables**
   - **Actions**
   - **New repository secret**
3. Name it exactly:
   `BUTLER_API_KEY`
4. Paste the itch.io Butler/Wharf API key as the value.
5. Re-run **Deploy Capture My Heart to GitHub Pages** or push a new commit.

Do not put the API key in source files, issues, commit messages, or build logs.

## First Butler upload only

The workflow pushes the browser build to:

`wlsdn8842-cyber/capture-my-heart:html5`

If the current browser build was originally uploaded manually through the itch.io website, the first Butler push creates a new upload/channel rather than converting the old web upload.

After the first successful Butler push:

1. Open **itch.io → Edit game → Uploads**.
2. Find the new Butler-managed `html5` upload.
3. Check **This file will be played in the browser** for that upload.
4. Confirm the game launches correctly.
5. Remove the old manually uploaded ZIP only after the Butler build is confirmed working.

After that, future pushes to `main` update the same `html5` channel automatically.

## What is uploaded

Only the playable runtime is pushed:

- index.html
- styles.css
- config.js
- game / analytics / feedback scripts
- manifest / privacy / service worker
- assets, including bonus WebM files

The private `admin/` dashboard is intentionally excluded from itch.io.

## Versioning

The workflow reads `CMH_CONFIG.VERSION` and passes it to Butler with `--userversion`.
