#!/bin/zsh
# The coin-ring swirl as a seamless loop: coin_ring.py with ANIM=L (every coin makes the Lansy icon's own turn, one after the
# other round the ring), rendered in the three passes of ring_render.sh (no lime light · with it · the edges' mask), composited
# frame by frame so the lime gleam stays on the edges, then encoded with alpha: WebM (VP9) for Chrome/Firefox, MOV (HEVC) for
# Safari, and a poster. ./3d/ring_anim.sh [RES] [SAMPLES] [FRAMES]  → web/labs/3d/renders/ring-swirl.{webm,mov} + -poster.webp
cd "$(dirname "$0")"; B=/Applications/Blender.app/Contents/MacOS/Blender; RES=${1:-1400}; S=${2:-128}; L=${3:-180}
OUTD=$PWD/check/swirl; mkdir -p $OUTD/a $OUTD/b $OUTD/m $OUTD/c
C="NORENDER=1 FACE_ANISO=.9 WORLD_SAT=0 WORLD_ROT=90 WORLD_TILT=25 PERSP=85 SUN_K=.2 WORLD_K=.95 FACE_TINT=.86,.76,.62 FACE_ROUGH=.05 THICK_ADD=.007 DIAM=.24 MARGIN=1.08 RIM_COL=.45,.9,.1 KEY=0 RING_CARD=33694F ASPECT=1.43 RES=$RES ANIM=$L RING_ICONS=${RING_ICONS:-full,retail,clinics,schools,hotels}"
M="$PWD/dl/mats/brushed-aluminium.blend::Brushed aluminium"
for job in "a RIM=0 SAMPLES=$S" "b RIM=220 SAMPLES=$S" "m RIM=0 MASK=1"; do set -- ${=job}; t=$1; shift
  # Blender on Metal crashes now and then: the run resumes (use_overwrite off) until every frame is there
  for try in 1 2 3 4 5 6 7 8; do n=$(ls $OUTD/$t | wc -l | tr -d ' '); [ "$n" -ge "$L" ] && break
    env ${=C} "$@" MAT="$M" TARGET=disc OUT=$OUTD/$t $B -b lansy-3d-test.blend -P studio_bk.py -P coin_ring.py > $OUTD/log-$t.txt 2>&1; done
  echo "pass $t: $(ls $OUTD/$t | wc -l | tr -d ' ') frames"; done
python3 - "$OUTD" "$L" <<'PY'
import sys, numpy as np
from PIL import Image
d, L = sys.argv[1], int(sys.argv[2])
for f in range(L):
    a = np.array(Image.open(f'{d}/a/f_{f:04d}.png').convert('RGBA')).astype(float); b = np.array(Image.open(f'{d}/b/f_{f:04d}.png').convert('RGBA')).astype(float)
    m = np.array(Image.open(f'{d}/m/f_{f:04d}.png').convert('L')).astype(float)[..., None] / 255
    Image.fromarray((a * (1 - m) + b * m).clip(0, 255).astype('uint8')).save(f'{d}/c/f_{f:04d}.png')
print('composited', L)
PY
R=../web/labs/3d/renders
ffmpeg -y -loglevel error -framerate 30 -i $OUTD/c/f_%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 30 -row-mt 1 $R/ring-swirl.webm
ffmpeg -y -loglevel error -framerate 30 -i $OUTD/c/f_%04d.png -c:v hevc_videotoolbox -alpha_quality .8 -tag:v hvc1 -b:v 6M $R/ring-swirl.mov
python3 -c "from PIL import Image; Image.open('$OUTD/c/f_0000.png').save('$R/ring-swirl-poster.webp', quality=88)"
ls -la $R/ring-swirl*; echo done
