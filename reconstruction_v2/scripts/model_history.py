"""Local-only single-file Blender history. Never configure a remote here."""
from pathlib import Path
import subprocess, shutil, json, hashlib
ROOT=Path(__file__).resolve().parents[2]
H=ROOT/'reconstruction_v2/model_history'
def git(*args):
 return subprocess.check_output(['git','-c',f'safe.directory={H.as_posix()}','-c','user.name=Codex','-c','user.email=codex@localhost','-C',str(H),*args])
def commit(message):
 if git('remote').strip(): raise RuntimeError('Private model history must have no remotes')
 git('add','GSX250R.blend');git('commit','-m',message)
 return git('rev-parse','HEAD').decode().strip()
def migrate():
 H.mkdir(exist_ok=True)
 if not (H/'.git').exists():git('init')
 manifest=H/'archive_manifest.json'
 if manifest.exists():raise RuntimeError('Archive already exists; use checkpoint or restore, not migration')
 records={}
 paths=sorted((ROOT/'reconstruction_v2/blends').glob('*.blend'),key=lambda p:(p.stat().st_mtime,p.name))
 for p in paths:
  if p.name in records:continue
  shutil.copy2(p,H/'GSX250R.blend')
  if git('status','--porcelain').decode().strip():
   try: rev=commit('Archive '+p.name)
   except subprocess.CalledProcessError:
    rev=git('rev-parse','HEAD').decode().strip()
  else:rev=git('rev-parse','HEAD').decode().strip()
  original=hashlib.sha256(p.read_bytes()).hexdigest()
  restored=hashlib.sha256(git('show',rev+':GSX250R.blend')).hexdigest()
  if original!=restored:raise RuntimeError('Restore verification failed '+p.name)
  records[p.name]={'commit':rev,'sha256':original}
  manifest.write_text(json.dumps(records,indent=2))
 # Latest accepted parent, not a later diagnostic candidate.
 source=ROOT/'reconstruction_v2/blends/38_gray_review.blend'
 shutil.copy2(source,H/'GSX250R.blend')
 if git('diff','--name-only').strip():commit('Select accepted r38 source')
 print(json.dumps({'archived':len(records),'verified':True,'head':git('rev-parse','HEAD').decode().strip()}))
def restore(revision):
 if git('status','--porcelain','--','GSX250R.blend').strip():raise RuntimeError('Checkpoint current model before restoring')
 payload=git('show',revision+':GSX250R.blend')
 if not payload.startswith(b'BLENDER') and not payload.startswith(bytes.fromhex('28b52ffd')) and not payload.startswith(bytes.fromhex('1f8b')):raise ValueError('Not a Blender file')
 (H/'GSX250R.blend').write_bytes(payload)
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['migrate','checkpoint','restore']);parser.add_argument('value',nargs='?');args=parser.parse_args()
 if args.action=='migrate':migrate()
 elif args.action=='checkpoint':print(commit(args.value or 'Model checkpoint'))
 elif args.action=='restore':
  if not args.value:parser.error('restore requires a commit hash')
  restore(args.value)

