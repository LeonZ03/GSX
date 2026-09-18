"""Full reproducible pipeline; use the local Blender executable."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import build_motorcycle as b
import refine_motorcycle as r
import polish_motorcycle as p
import finish_motorcycle as f
import fix_details as d
b.main();r.refine();p.polish();f.finish();d.fix()
exec(compile((Path(__file__).parent/'prepare_final.py').read_text('utf-8-sig'),str(Path(__file__).parent/'prepare_final.py'),'exec'))
print('GSX_BUILD_COMPLETE')
