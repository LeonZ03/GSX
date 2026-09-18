"""Download public primary references; private owner photos are never uploaded."""
from pathlib import Path
import urllib.request,hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'references/public';DEST.mkdir(parents=True,exist_ok=True)
URLS={
 'GSX250RM0_N00_parts.pdf':'https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RM0_N00.pdf',
 'GSX250R_ABS_L8_brochure.pdf':'https://www.suzuki.hu/motor/files/document/document/294/GSX250R_ABS_L8_EN.pdf',
 'official_360.html':'https://www.globalsuzuki.com/motorcycle/smgs/products/2021gsx250r/360viewer/',
}
for n in [1,5,10,14,19,23,28,32]:URLS[f'official_turntable_{n:02}.jpg']=f'https://www.globalsuzuki.com/motorcycle/smgs/products/2021gsx250r/360viewer/img/main/g01_c01_{n}.jpg'
report=[]
for name,url in URLS.items():
    target=DEST/name
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'GSX-local-reference-archive/1.0'})
        with urllib.request.urlopen(req,timeout=180) as response, target.with_suffix(target.suffix+'.partial').open('wb') as out:
            declared=int(response.headers.get('Content-Length','0'));count=0
            while True:
                buf=response.read(2**16)
                if not buf:break
                out.write(buf);count+=len(buf)
        if declared and count!=declared:raise IOError('Incomplete response; partial file kept')
        target.with_suffix(target.suffix+'.partial').replace(target)
        report.append({'file':name,'url':url,'bytes':count,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
        print('Archived',name,count)
    except Exception as e:report.append({'file':name,'url':url,'error':str(e)});print('Not archived',name,type(e).__name__)
(DEST/'download_manifest.json').write_text(json.dumps(report,indent=2))
