"""Local image evidence and numeric table for camera69 assumption sensitivity."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
from pillion_camera_sensitivity import outline

def main():
 a=json.loads((V2/'calibration/camera69_sensitivity_r12_refined.json').read_text());report=json.loads((V2/'qa/pillion_camera_sensitivity_r12.json').read_text());rows=report['results'];cameras={c['name']:c for c in [a['frozen_camera'],*a['candidates']]}
 lo=min(rows[1:],key=lambda r:r['parts']['r11']['diagnostic_offset_z_mm']);hi=max(rows[1:],key=lambda r:r['parts']['r11']['diagnostic_offset_z_mm'])
 geo={t:json.loads((V2/f'qa/tail_mesh_{t}.json').read_text())['Seat_Pillion'] for t in ['r08','r11']}
 ann=json.loads((V2/'annotations/photo_69.json').read_text());parts=json.loads((V2/'annotations/seat_tail_r09.json').read_text());boundary=next(x for x in parts['boundaries'] if x['image_id']==69 and x['part']=='Seat_Pillion')['points']
 photo=Image.open(next((ROOT/'IMG').glob('*_69_97.jpg'))).convert('RGB');d=ImageDraw.Draw(photo)
 for p in ann['exclude_polygons']:d.polygon([tuple(x) for x in p['polygon']],fill=(190,198,207))
 font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
 board=Image.new('RGB',(1440,1320),'#f6f8fa');d=ImageDraw.Draw(board)
 d.text((22,15),'r12 证据检查：镜头假设对后座高度的影响（模型仍为 r11）',font=font,fill='#192b3a')
 d.text((22,56),'25组局部拟合，16组通过轮圈低残差筛查；不是相机验收或统计置信区间。',font=small,fill='#9c382d')
 panels=[('固定镜头：r08 与 r11后座',[('frozen_baseline','r08',(212,60,142)),('frozen_baseline','r11',(0,177,204))]),('固定模型：更低高度诊断的镜头',[(lo['name'],'r11',(239,111,50)),('frozen_baseline','r11',(0,177,204))]),('固定模型：更高高度诊断的镜头',[(hi['name'],'r11',(81,96,224)),('frozen_baseline','r11',(0,177,204))])]
 box=(1030,445,1400,655)
 for col,(label,traces) in enumerate(panels):
  arr=np.array(photo.copy());cv2.polylines(arr,[np.array(boundary,np.int32)],True,(251,187,20),2)
  for cam,tag,color in traces:
   edge=outline(geo[tag],cameras[cam]);pix=np.rint(edge).astype(int);valid=(pix[:,0]>=0)&(pix[:,0]<photo.width)&(pix[:,1]>=0)&(pix[:,1]<photo.height);mask=np.zeros((photo.height,photo.width),np.uint8);mask[pix[valid,1],pix[valid,0]]=1;arr[cv2.dilate(mask,np.ones((2,2),np.uint8))>0]=color
  tile=Image.fromarray(arr).crop(box).resize((466,265));board.paste(tile,(col*480+7,136));d.text((col*480+10,99),label,font=small,fill='#25384b')
 d.text((22,416),'黄＝照片已标后座边界；青＝r11固定镜头；紫＝旧r08；橙／蓝＝改变镜头后同一r11。',font=small,fill='#344b5e')
 d.text((22,452),'上图没有移动任何网格。下表“Z补偿”是另行计算的诊断值，未写回模型。',font=small,fill='#9c382d')
 headers=[(24,'被扰动的假设'),(600,'轮圈 RMS / px'),(858,'旧r08 Z补偿 / mm'),(1154,'r11 Z补偿 / mm')]
 for x,label in headers:d.text((x,501),label,font=small,fill='#162d42')
 def label(row):
  name=row['name']
  if name=='baseline_refit':return '原假设重新拟合'
  if row['family']=='focal_profile':return f"焦距固定 {row['focal_px']:.0f} px"
  if row['family']=='radius':return f"圈贴半径 {row['radius_mm']:.0f} mm"
  dx=(row['cx']-853)/1706*100;dy=(row['cy']-640)/1280*100
  return ('组合：' if row['family']=='joint_envelope' else '主点：')+f"R={row['radius_mm']:.0f}, Δx={dx:+.0f}%, Δy={dy:+.0f}%"
 for i,row in enumerate(rows[1:]):
  y=540+i*36
  if i%2==0:d.rectangle((12,y-3,1428,y+31),fill='#e9eef3')
  vals=[label(row),f"{row['wheel_rms_px']:.3f}",f"{row['parts']['r08']['diagnostic_offset_z_mm']:+.1f}",f"{row['parts']['r11']['diagnostic_offset_z_mm']:+.1f}"]
  for (x,_),val in zip(headers,vals):d.text((x,y),val,font=small,fill='#25384b')
 d.text((22,1136),'这16组候选中：旧后座需上调78–105 mm；当前r11诊断补偿约 −13 至 +16 mm。',font=small,fill='#192b3a')
 d.text((22,1174),'支持保留上调方向；不能据此锁定高度。畸变、圈贴偏移、标注误差及独立视角仍待验证。',font=small,fill='#9c382d')
 d.text((22,1212),'照片人工边界约±4 px。仅计算独立分件轮廓，不包含相邻遮挡，不是整车相似度。',font=small,fill='#344b5e')
 d.text((22,1250),'真实照片与本对照仅留本地；正式相机、控制网格和r11源文件未改。',font=small,fill='#344b5e')
 board.save(V2/'renders/camera69_sensitivity_r12.jpg',quality=94)
 checks={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in a['input_sha256'].items()}
 qa={'status':'NOT_PASSED','all_source_inputs_unchanged':all(checks.values()),'input_checks':checks,'low_height_diagnostic_camera':lo['name'],'high_height_diagnostic_camera':hi['name'],'production_camera_replaced':False,'geometry_modified':False}
 (V2/'qa/camera_sensitivity_frozen_r12.json').write_text(json.dumps(qa,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in qa.items() if k!='input_checks'},indent=2))
if __name__=='__main__':main()