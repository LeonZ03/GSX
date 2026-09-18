"""Audit generated artifacts without disclosing private registration in console output."""
from pathlib import Path
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(2**20),b''):h.update(block)
    return h.hexdigest()

photos=[]
for p in sorted((ROOT/'IMG').glob('*')):
    if p.is_file():photos.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':digest(p)})
(ROOT/'references/local/photo_inventory.json').write_text(json.dumps(photos,ensure_ascii=False,indent=2),encoding='utf-8')
artifacts=[]
for folder in ['blends','exports','renders/final']:
    for p in sorted((ROOT/folder).glob('*')):
        if not p.is_file() or p.suffix=='.blend1':continue
        row={'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':digest(p)}
        if p.suffix=='.png':
            with p.open('rb') as f:f.seek(16);row['size']=struct.unpack('>II',f.read(8))
        artifacts.append(row)
(ROOT/'qa/artifact_manifest.json').write_text(json.dumps(artifacts,indent=2),encoding='utf-8')
print(json.dumps({'photo_count':len(photos),'artifact_count':len(artifacts),'final_png_count':sum(a['path'].startswith('renders') for a in artifacts),'non_4k_images':[a['path'] for a in artifacts if 'size' in a and a['size']!=(3840,2160)]}))
