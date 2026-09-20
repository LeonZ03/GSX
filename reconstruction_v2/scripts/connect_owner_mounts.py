"""Connect the discovered missing headstock stay and guard mounting roots."""
import bpy,sys
from pathlib import Path
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_structure import init

def apply(s):
 b=init(s);b.COL=b.C['Details']
 for side,lab in [(-1,'L'),(1,'R')]:
  if 'GuardMount_RearBolt_'+lab not in s.objects:b.rod('GuardMount_RearBolt_'+lab,(side*163,-201.34,441.41),(side*182,-201.34,441.41),6,'steel',24)
 if 'Frame_SteeringHead' in s.objects:return
 o=b.cyl('Frame_SteeringHead',(0,489,790),35,130,'gun',(0,-.42,.9075),64,1.5)
 o['unverified']='Inferred hidden headstock envelope from existing clamp axis, not measured'
 stem=b.rod('SteeringStem_Column',(0,536,697),(0,445,886),13,'steel',48);stem['steer_with_front']=True
 for side,lab in [(-1,'L'),(1,'R')]:
  q=lambda p:(side*p[0],p[1],p[2])
  b.panel('Frame_HeadGusset_'+lab,[q(p) for p in [(61.5,452,791),(26,490,778),(26,481,820)]],'gun',8,2)
  b.panel('Dashboard_StayRoot_'+lab,[q(p) for p in [(48,500,824),(48,488,836),(26,470,835),(26,483,824)]],'black',5,1)
  b.rod('GuardMount_UpperFoot_'+lab,q((134,272,542)),q((153,279,546)),11,'black',32)
  b.rod('GuardMount_LowerFoot_'+lab,q((135,170,327)),q((163,170,327)),11,'black',32)
  b.cyl('GuardMount_LowerBolt_'+lab,q((155,170,327)),6,6,'steel',(side,0,0),6,.5)
 bpy.context.view_layer.update()
