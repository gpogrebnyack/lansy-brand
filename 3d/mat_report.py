# One report image for a BlenderKit material: the icon · the coin · the cup, and its preview ball (BlenderKit's own thumbnail scene) small
# in the top right corner.
# python3 3d/mat_report.py "Material Name"      → 3d/check/mats/<slug>-report.png (and the three PNGs with alpha beside it),
#                                                 and web/labs/3d/renders/<slug>.webp for the 3D lab page (no ball)
import json, os, re, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); BL = '/Applications/Blender.app/Contents/MacOS/Blender'
name = sys.argv[1]; slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
db = json.load(open(f'{HERE}/dl/mats/bk.json'))
if name not in db:   # fetch it (by name, or by a gallery link / id, then use the asset's real name)
    r = subprocess.run(['python3', f'{HERE}/bk_get.py', name], check=True, capture_output=True, text=True); print(r.stdout)
    name = next(l[5:] for l in r.stdout.splitlines() if l.startswith('NAME ')); slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    db = json.load(open(f'{HERE}/dl/mats/bk.json'))
mat = f"{HERE}/dl/mats/{db[name]['file']}::{name}"; out = f'{HERE}/check/mats'; os.makedirs(out, exist_ok=True)
def run(args, env):
    for _ in range(3):   # Metal kernel loading crashes now and then; a retry passes
        r = subprocess.run([BL, '-b'] + args, env={**os.environ, **env}, capture_output=True, text=True)
        if 'RENDERED' in r.stdout or 'Saved:' in r.stdout: return
    sys.exit(r.stdout[-2000:] + r.stderr[-2000:])
if not os.environ.get('COMPOSE_ONLY'): run([f'{HERE}/dl/thumbnailer/material_thumbnailer_cycles.blend', '-P', f'{HERE}/preview_ball.py'], {'MAT': mat, 'OUT': f'{out}/{slug}-ball.png'})
CUP = os.environ.get('CUP') == '1'   # the cup is parked for now: only with CUP=1
for t in () if os.environ.get('COMPOSE_ONLY') else (('icon', 'disc', 'cup') if CUP else ('icon', 'disc')):
    run([f'{HERE}/lansy-3d-test.blend', '-P', f'{HERE}/studio_bk.py'], {'MAT': mat, 'TARGET': t, 'OUT': f'{out}/{slug}-{t}.png',
         'MATSET': db[name].get('matset', '')})   # our tuning of the material's own controls, kept in bk.json
keys = [k for k in (('icon', 'disc', 'cup') if CUP else ('icon', 'disc')) if os.path.exists(f'{out}/{slug}-{k}.png')]   # the icon · the coin (· the cup)
S = 800; W = Image.new('RGBA', (len(keys) * S, S), (255, 255, 255, 255))
Z = int(S * .92)   # all a little inset (the same scale, so the icon stays the coin's size), room for the ball in the corner
for i, k in enumerate(keys):
    W.alpha_composite(Image.open(f'{out}/{slug}-{k}.png').convert('RGBA').resize((Z, Z), Image.LANCZOS), (i * S + (S - Z) // 2, (S - Z) // 2 + (S - Z) // 4))
P = W.copy()   # the page copy: the icon and the coin only
z = S // 4   # the material's preview ball, a quarter size, in the top right corner: a key, not a third subject
W.alpha_composite(Image.open(f'{out}/{slug}-ball.png').convert('RGBA').resize((z, z), Image.LANCZOS), (len(keys) * S - z, 0))
W.convert('RGB').save(f'{out}/{slug}-report.png'); print(f'{out}/{slug}-report.png')
web = os.path.join(HERE, '..', 'web', 'labs', '3d', 'renders'); os.makedirs(web, exist_ok=True)   # the copy for the 3D lab page
P.convert('RGB').save(f'{web}/{slug}.webp', quality=88); print(f'{web}/{slug}.webp', '·', db[name].get('author', ''))
