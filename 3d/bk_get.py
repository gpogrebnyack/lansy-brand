# Fetch a free BlenderKit material by name into 3d/dl/mats/ and record it in bk.json (name, file, author, texture size).
# python3 3d/bk_get.py "Anodized Titanium"        → prints the top matches; downloads the exact-name match if it's free
# python3 3d/bk_get.py <gallery link or asset id> → that asset
import json, os, re, subprocess, sys, urllib.parse
MATS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dl', 'mats')
API = 'https://www.blenderkit.com/api/v1/search/?'
def curl(url): return subprocess.run(['curl', '-sL', url], capture_output=True, check=True).stdout

name = sys.argv[1]
uid = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', name)   # a gallery link or an id works too
if uid:
    res = []
    for key in ('asset_base_id', 'asset_id'):   # gallery links carry either id
        res = res or json.loads(curl(API + urllib.parse.urlencode({'query': f'{key}:{uid.group(0)}'})))['results']
    if not res: sys.exit('no asset with that id')
    name = res[0]['name']
else:
    q = urllib.parse.urlencode({'query': f'asset_type:material search_text:{name}', 'page_size': 8})
    res = json.loads(curl(API + q))['results']
for r in res: print(('FREE ' if r['isFree'] else 'paid ') + r['name'], '·', r['author']['fullName'] if r.get('author') else '')
hit = next((r for r in res if r['name'].strip().lower() == name.strip().lower()), None)
if not hit: sys.exit('no exact match')
if not hit['isFree']: sys.exit('not free')
blend = next(f for f in hit['files'] if f['fileType'] == 'blend')
link = json.loads(curl(blend['downloadUrl'] + '?scene_uuid=00000000-0000-0000-0000-000000000000'))['filePath']
fn = re.sub(r'[^a-z0-9]+', '-', hit['name'].lower()).strip('-') + '.blend'
open(os.path.join(MATS, fn), 'wb').write(curl(link))
db_path = os.path.join(MATS, 'bk.json'); db = json.load(open(db_path)) if os.path.exists(db_path) else {}
db[hit['name']] = {'file': fn, 'author': hit['author']['fullName'] if hit.get('author') else '', 'license': hit.get('license'),
                   'isFree': True, 'ts': hit.get('dictParameters', {}).get('textureSizeMeters', 1)}
json.dump(db, open(db_path, 'w'), indent=1, ensure_ascii=False)
print('SAVED', fn, 'ts', db[hit['name']]['ts']); print('NAME', hit['name'])
