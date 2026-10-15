#!/bin/zsh
# The coin-ring hero: three Blender passes (no lime light · with the lime edge light · the edges' mask), composited so the lime
# gleam lands on the coins' edges only. ./3d/ring_render.sh [RES] [SAMPLES] → 3d/check/comp/ring-final.png (alpha) and the web copy
cd "$(dirname "$0")"; B=/Applications/Blender.app/Contents/MacOS/Blender; RES=${1:-2064}; S=${2:-384}; export GROUND NAME
C="NORENDER=1 FACE_ANISO=.9 WORLD_SAT=0 WORLD_ROT=90 WORLD_TILT=25 PERSP=85 SUN_K=.2 WORLD_K=.95 FACE_TINT=.86,.76,.62 FACE_ROUGH=.05 THICK_ADD=.007 DIAM=.24 MARGIN=1.08 RIM_COL=${RIM_COL:-.45,.9,.1} KEY=0 RING_CARD=${GROUND:-33694F} ASPECT=1.43 RES=$RES"
M="$PWD/dl/mats/brushed-aluminium.blend::Brushed aluminium"
for job in "a RIM=0 SAMPLES=$S" "b RIM=220 SAMPLES=$S" "m RIM=0 MASK=1"; do set -- ${=job}; t=$1; shift
  for try in 1 2 3; do env ${=C} "$@" MAT="$M" TARGET=disc OUT=$PWD/check/comp/rc-$t.png $B -b lansy-3d-test.blend -P studio_bk.py -P coin_ring.py 2>&1 | grep -q "RENDERED ring" && break; done; done
python3 - <<'PY'
import numpy as np
from PIL import Image
a=np.array(Image.open('check/comp/rc-a.png').convert('RGBA')).astype(float); b=np.array(Image.open('check/comp/rc-b.png').convert('RGBA')).astype(float)
m=np.array(Image.open('check/comp/rc-m.png').convert('L')).astype(float)[...,None]/255
o=Image.fromarray((a*(1-m)+b*m).clip(0,255).astype('uint8')); import os; n=os.environ.get('NAME','hero-coin-ring'); o.save(f'check/comp/{n}.png'); o.save(f'../web/labs/3d/renders/{n}.webp',quality=90)
hx=os.environ.get('GROUND','33694F'); B=Image.new('RGBA',o.size,tuple(int(hx[i:i+2],16) for i in (0,2,4))+(255,)); B.alpha_composite(o); B.convert('RGB').save(f'check/comp/{n}-on-ground.png')
PY
echo done
