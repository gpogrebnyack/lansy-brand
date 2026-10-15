# Lansy — design tools

Lansy's visual language: colour, type, logo and icon, and four techniques — the marker, the blob, the dots and 3D — with the rules for people and for agents. Live: https://lansy-brand.vercel.app

## Run locally

```bash
python3 -m http.server 8766 --directory web
```

Open http://localhost:8766. The canvas with layouts in use: http://localhost:8766/labs/canvas.html.

## What is where

- `web/index.html`, `marker.html`, `blob.html`, `dots.html`, `3d.html` — the pages.
- `web/labs/canvas.html` — the board of finished layouts; the dotted pictures are live code in it.
- `web/labs/line-lab.html` — the Lab: the pen, the generator, the posts with people. Tweak the pen here, keep a shape by its seed, save its path to `web/assets/line/`.
- `web/brand.md`, `tokens.json`, `llms.txt`, `assets/manifest.json` — the same rules for agents. `tokens.json` is the source of truth.
- `3d/` — the Blender scripts behind the 3D page: the rubric icons, the coin ring, the spinning icon. See `3d/README.md`.
- `scripts/export-examples.sh` — renders the pages' example pictures from the blob lab.

## Before a commit

```bash
python3 scripts/check.py
```

It checks that the pages and `brand.md` use only the colours from `tokens.json`, that every file in the manifest exists and that every local link works.

Every push to `main` deploys to Vercel (root directory `web`).
