# 3D

Blender 5.x scripts behind the 3D page. Paths are relative to this folder.

- `build_meshes.py`, `rubric_icons.py` — the icon meshes and the rubric icons (`models/rubric_icons.blend`).
- `studio_bk.py` — renders an object in a material in BlenderKit's preview studio.
- `coin_ring.py` with `ring_render.sh`, `ring_anim.sh` — the coin ring and its loop.
- `icon_spin.py` — the spinning icon. `cup_scene.py`, `brooch_scene.py` — compositions. `stand.py` — every part in every material.
- `icon/lansy-icon.blend` — the Lansy icon model, from the landing.
- `blobs/` — the blob outlines the scenes are cut from. `research-3d-*.md` — what we tried and chose.

Not in git, fetch them once:

- `dl/mats/` — free BlenderKit materials: `python3 3d/bk_get.py "Brushed aluminium"` (names in `free-materials.json`, `material-packs.json`).
- `dl/thumbnailer/` — BlenderKit's material-preview studio, from the BlenderKit add-on.
- `hdri/` — Poly Haven HDRIs, CC0, 2k: `studio_small_09`, `monochrome_studio_02`, `wooden_studio_08`.
- `models/` — built by the scripts (`rubric_icons.py`, `prep_cup.py`).

Renders go to `check/` (ignored); finished ones are copied to `web/labs/3d/renders/` or uploaded to R2 (`brand/v1/`).
