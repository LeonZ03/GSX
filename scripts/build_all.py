"""Full reproducible pipeline; use the local Blender executable."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import build_motorcycle as b
import refine_motorcycle as r
import polish_motorcycle as p
import finish_motorcycle as f
import fix_details as d
import surface_refinement as sr
b.main();r.refine();p.polish();f.finish();d.fix();sr.refine_surfaces()
exec(compile((Path(__file__).parent/'prepare_final.py').read_text('utf-8-sig'),str(Path(__file__).parent/'prepare_final.py'),'exec'))
exec(compile((Path(__file__).parent/'validate_source.py').read_text('utf-8-sig'),str(Path(__file__).parent/'validate_source.py'),'exec'))
print('GSX_BUILD_COMPLETE')
