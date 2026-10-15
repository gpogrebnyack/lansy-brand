# Lansy design tools

Lansy's visual guideline: colour, type, logo and icon (Core), and four techniques: marker, blob, dots, 3D. A static site in `web/`, live at https://lansy-brand.vercel.app. Page copy is in English.

## Run and ship

- Local: `python3 -m http.server 8766 --directory web` → http://localhost:8766
- Before every commit: `python3 scripts/check.py`. It checks colours against `tokens.json`, every manifest file, every local link and that inline scripts parse.
- A push to `main` deploys the public site on Vercel (root directory `web`). Check the page in a browser before pushing.
- Never push the local branch `archive/full-history`: it holds old work that must stay private.

## Two layers, always in step

People read the pages; agents read the same rules from files. Every decision is written in both:

- pages: `web/index.html` (Core), `marker.html`, `blob.html`, `dots.html`, `3d.html`;
- agents: `web/llms.txt` → `web/brand.md` (rules, imperative, English) → `web/tokens.json` (values, W3C DTCG) → `web/assets/manifest.json` (files, grounds, minimum sizes).

When a rule changes on a page, change `brand.md` (and tokens or the manifest if values or files change) in the same commit. They must never contradict each other. `tokens.json` is the source of truth for values.

## Where things are

- `web/nav.js` — the top bar on every page: Core · Marker · Blob · Dots · 3D | Lab · Canvas. Add a page there, not in each file.
- `web/labs/line-lab.html` — the Lab: the pen, the blob generator, posts with people. `?solo=<id>` renders one post for export; the bar hides itself there.
- `web/labs/canvas.html` — finished layouts on one board. The main page shows it by turning over (`index.html?view=canvas`).
- `scripts/export-examples.sh` — renders the pages' example pictures from the Lab.
- `3d/` — Blender scripts for the 3D renders (`3d/README.md` lists what to fetch: BlenderKit materials, HDRIs).
- Videos and heavy media are not in git. They live on Cloudflare R2 (`https://pub-f554743e343b4157afc5fa154f4ba787.r2.dev/brand/v1/…`). A new version goes under a new prefix (`brand/v2/`); never overwrite.

## Page conventions

- A section head is a label and a heading. No lead under it; only the hero has a lead.
- No download buttons.
- Mark anything not yet approved as "proposal".
- Colours only from `tokens.json`; never cool or pure greys, never `#000000`.
