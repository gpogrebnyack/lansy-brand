#!/bin/zsh
# Renders the brand page's technique examples straight from the lab (web/labs/line-lab.html, export mode) with headless Chrome.
# Needs the local server: python3 -m http.server 8766 --directory web
set -e
cd "$(dirname "$0")/.."
OUT=web/assets/examples; mkdir -p $OUT
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE="http://localhost:8766/labs/line-lab.html"
shot(){ # name, query, width, height
  "$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=8000 \
    --window-size=$3,$4 --screenshot="$PWD/$OUT/$1.png" "$BASE?$2" >/dev/null 2>&1
  echo "$1"; }
enc(){ python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1"; }
# 05 · marker: the line's pen and construction, the phrase on each ground, examples, don'ts
shot marker-alone      "solo=spec&set=$(enc '{"noline":1,"text":"Every guest // is *a lesson*","size":0.22}')" 1600 800
shot marker-pen        "shape=line&path=1" 1600 800
shot marker-build      "solo=spec&set=$(enc '{"guides":1,"bg":"white"}')" 1600 800
shot marker-on-white   "solo=spec&set=$(enc '{"bg":"white"}')" 1600 800
shot marker-on-floor   "solo=spec&set=$(enc '{"bg":"floor"}')" 1600 800
shot marker-on-lime    "solo=spec&set=$(enc '{"bg":"lime"}')" 1600 800
shot marker-on-dark    "solo=spec&set=$(enc '{"bg":"dark","noline":1,"bg":"white"}')" 1600 800
shot marker-quote      "solo=quote" 1080 1080
shot marker-factoid    "solo=line" 1080 1080
shot marker-factoid-floor "solo=line&set=$(enc '{"bg":"floor"}')" 1080 1080
shot marker-dont-whole "solo=spec&set=$(enc '{"text":"*Every guest is a lesson*","noline":1,"bg":"white"}')" 1600 800
shot marker-dont-thick "solo=spec&set=$(enc '{"bg":"white","thick":170}')" 1600 800
shot marker-dont-colour "solo=spec&set=$(enc '{"bg":"white","ink":"dark"}')" 1600 800
shot marker-dont-dark  "solo=spec&set=$(enc '{"bg":"dark"}')" 1600 800
shot marker-dont-two   "solo=spec&set=$(enc '{"text":"*Every guest* is *a lesson*","noline":1,"bg":"white"}')" 1600 800
shot marker-dont-number "solo=spec&set=$(enc '{"text":"*4 380* conversations // a day","noline":1,"bg":"white"}')" 1600 800
shot marker-dont-small "solo=spec&set=$(enc '{"text":"Heard at *every counter*, after every shift","noline":1,"bg":"white","size":0.045}')" 1600 800
# 06 · blob
shot blob-shape-a      "shape=a&path=1" 800 800
shot blob-shape-b      "shape=b&path=1" 800 800
shot blob-shape-kept   "shape=kept&path=1" 800 800
shot blob-over         "solo=above" 1080 1080
shot blob-fill-colour  "solo=below2&set=$(enc '{"fill":"dark","bg":"lime"}')" 1080 1080
shot blob-small        "solo=hero" 1600 800
# the marker page's hero: the headline itself, on transparency, cropped to its ink
"$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=8000 --default-background-color=00000000 \
  --window-size=3000,1500 --screenshot="$PWD/$OUT/marker-hero.raw.png" "$BASE?solo=spec&clear=1&set=$(enc '{"bg":"none","align":"left","margin":0.01,"text":"Every text has *one phrase* // that matters most","size":0.16,"track":-0.025,"thick":62}')" >/dev/null 2>&1
python3 - "$OUT" <<'PY'
import sys,os; from PIL import Image
o=sys.argv[1]; p=o+'/marker-hero.raw.png'; im=Image.open(p).convert('RGBA'); b=im.getbbox()
im.crop((b[0],b[1]-6,b[2]+12,b[3]+6)).save(o+'/marker-hero.webp',quality=90); os.remove(p)
PY
echo marker-hero
# the blob page's hero: a headline with a small blob standing in its first line, people coming out of it
"$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=8000 --default-background-color=00000000 \
  --window-size=3000,1500 --screenshot="$PWD/$OUT/blob-hero.raw.png" "$BASE?solo=hero&clear=1&set=$(enc '{"bg":"none","bare":1,"size":0.16,"fill":"photo","small":150,"ppl":105,"py":6,"lines":[[{"t":"A place"},{"b":1},{"t":"for people"}],[{"t":"to come out of"}]]}')" >/dev/null 2>&1
python3 - "$OUT" <<'PY'
import sys,os; from PIL import Image
o=sys.argv[1]; p=o+'/blob-hero.raw.png'; im=Image.open(p).convert('RGBA'); b=im.getbbox()
im.crop((b[0],b[1]-6,b[2]+12,b[3]+6)).save(o+'/blob-hero.webp',quality=90); os.remove(p)
PY
echo blob-hero
# previews for the cards on the main page, on transparency, cropped to their ink
prev(){ "$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=8000 --default-background-color=00000000 \
  --window-size=$3,$4 --screenshot="$PWD/$OUT/$1.raw.png" "$BASE?$2&clear=1" >/dev/null 2>&1
python3 - "$OUT/$1" <<'PY'
import sys,os; from PIL import Image
p=sys.argv[1]; im=Image.open(p+'.raw.png').convert('RGBA'); b=im.getchannel('A').point(lambda v:255 if v>40 else 0).getbbox(); im.crop((b[0]-8,b[1]-8,b[2]+8,b[3]+8)).save(p+'.webp',quality=90); os.remove(p+'.raw.png')
PY
echo $1; }
# the cards' previews: the marker's text and its line as two layers, the blob with its people; a card's layers share one box
raw(){ "$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=8000 --default-background-color=00000000 \
  --window-size=$3,$4 --screenshot="$PWD/$OUT/$1.raw.png" "$BASE?$2&clear=1" >/dev/null 2>&1; }
MK='"text":"Every text has // *one phrase* that // matters most","size":0.2,"track":-0.025,"thick":62,"bg":"none","ink":"white"'
raw mk-all  "solo=spec&set=$(enc "{$MK}")" 1600 1200
raw mk-text "solo=spec&set=$(enc "{$MK,\"noline\":1}")" 1600 1200
raw mk-line "solo=spec&set=$(enc "{$MK,\"notext\":1}")" 1600 1200
BL='"bg":"none","bare":1,"blob":{"size":92,"x":50,"y":62},"people":{"size":56,"x":50,"y":8,"close":8}'
raw bl-lime  "solo=below2&set=$(enc "{$BL,\"fill\":\"lime\"}")" 1200 1200
python3 - "$OUT" <<'PY'
import sys,os,json; from PIL import Image
o=sys.argv[1]; L=lambda n:Image.open(f'{o}/{n}.raw.png').convert('RGBA')
def box(im): b=im.getchannel('A').point(lambda v:255 if v>40 else 0).getbbox(); return (b[0]-8,b[1]-8,b[2]+8,b[3]+8)
for card,ref,parts in [('marker-card','mk-all',{'mk-text':'marker-card-text','mk-line':'marker-card-line'}),('blob-card','bl-lime',{'bl-lime':'blob-card'})]:
  B=box(L(ref))
  for src,dst in parts.items(): L(src).crop(B).save(f'{o}/{dst}.webp',quality=90)
for n in ['mk-all','mk-text','mk-line','bl-lime']: os.remove(f'{o}/{n}.raw.png')
PY
echo card-previews
for f in $OUT/*.png; do python3 - "$f" <<'PY'
import sys; from PIL import Image
p=sys.argv[1]; im=Image.open(p).convert('RGB'); im.save(p[:-4]+'.webp',quality=86); import os; os.remove(p)
PY
done
ls $OUT
