# Suzuki GSX250R 实车重建

## 当前进展：r38，B/C仍未通过

本批新增后挡泥板、尾灯、后转向灯、牌照灯和空白牌架，纠正座尾支撑露出与尾尖自交；油箱盖按实车近照拆分为五螺栓外圈、锁盖和铰接件，并重新安装到油箱曲面。已完成局部几何检查、三视角对照和独立重放。

**这仍是未验收灰模，不是1:1成品。** 主要车身曲面、整体/分件轮廓、独立角度和若干机械细节尚未通过。隐藏尺寸和本轮尾部截面近似均保留说明，不以零件数或修订号代替完成度。

- [本批记录与已知偏差](reconstruction_v2/reviews/r38_tail_and_cap.md)
- 本地源：`reconstruction_v2/blends/38_gray_review.blend`
- 本地对照：`reconstruction_v2/renders/stage_bc_r38_comparison.jpg`
- 本地驾驶位：`reconstruction_v2/renders/stage_bc/r38_Cockpit.png`

依据本地 `IMG/` 的 12 张实车照片，使用 **Blender 5.2.2 LTS / Blender MCP** 重建用户 GSX250R。还原蓝白版画、荧光轮圈贴、对称护杠、手机支架、方向阻尼器及指定京 B；排除尾包、网绳、骑手和手套。没有使用 Computer Use。

**当前可编辑检查版本为 r38。阶段 B（准确灰模）和 C（外露结构与附件）均未通过，尚不是 1:1 成品。** 不进入最终贴花、材质、4K 成片或导出。r26 工作基线、r27 及本轮候选均保留。

## 此前 r28–r35 主体重建进展

- 前罩上肩与侧回折合并为共享四边面控制，重新处理车头侧回折和驾驶位接缝；消除本轮检查到的侧罩—散热器、前罩—内衬等表面交叉。
- 主灯下半轮廓改为较宽的碗形，移除错误的蓝色中央下包围；主灯黑框改为开口框，位置灯更换折叠的旧控制网格。
- 排气重建异形筒体、包裹式隔热罩、独立端盖和空心出口。隔热罩实际求值网格与筒体的表面交叉为零。
- 右离合器盖改为不规则铸件，校正圆形凸台的位置和尺寸；左发电机盖由大圆形占位改为异形外壳与小检修盖。只保留有图像依据的可见螺栓，未确定的孔位仍待核对。
- 保存完整控制快照，完成从 r26 的独立重放：908 个对象的控制几何、变换、照片相机、所查修改器参数及可见性一致。

本轮指定的 19 个部件未检出非流形、退化面或非相邻三角自交；这是局部网格检查。右盖与曲轴箱仍有装配接触，完整装配、外形和隐藏尺寸没有因此通过。名义轴距实测 1430.0001 mm、制动盘 290/240 mm、胎宽 110/140 mm，仅证明模型构造尺寸正确。

## 本地成果

项目：`D:\Work\gadgets\GSX`。

| 内容 | 路径 |
|---|---|
| 当前可编辑源 | `reconstruction_v2/blends/38_gray_review.blend` |
| 实车 / r26 / r35 对照 | `reconstruction_v2/renders/stage_bc_r35_comparison.jpg` |
| 四角度叠加与轮廓检查 | `reconstruction_v2/renders/review_r35_{62,63,64,69}.jpg` |
| 左发动机盖局部改前改后 | `reconstruction_v2/renders/alternator_r34_comparison.jpg` |
| 本批次说明与未通过项 | [r35 检查记录](reconstruction_v2/reviews/r35_stage_bc.md) |
| 当前控制网格快照 | `reconstruction_v2/data/revisions/r35_controls/manifest.json` |
| 本地几何、装配与重放检查 | `reconstruction_v2/qa/geometry_r35.json`、`assembly_r35.json`、`replay_r35.json` |

`data/control_cages/` 仍是旧兼容输入，不可用它覆盖 r35。当前控制以 r35 快照和源文件内 `control_cage_source` 为准；保留精修拓扑、隐藏构造面和实时装配依赖。

## 仍需完成

车头折面、侧罩开口、油箱肩部及座尾曲率仍有可见差异。发动机隐藏深度、盖板完整孔位、排气支座及内部灯具、护杠和手机架安装细节未验收。

整车及分件 98% 轮廓、正式关键点误差、两个可靠且未用于形体调整的有效角度仍未通过。现有局部拟合值不能代替这些指标。原厂转台相机试算仅为诊断，不替代用户实车独立验证。下一步必须围绕这些外形与证据缺口推进，不能继续以增加修订号或小零件数代替阶段完成。

旧的 10–14 大轮预算已不能作为可信完工预测，本批次不再追加未经依据的轮数承诺。[执行路线](reconstruction_v2/ITERATION_PLAN.md) · [问题清单](reconstruction_v2/ISSUES.md)。

## 重要命令

在项目根目录 PowerShell 执行。自动建模通过 Blender MCP；下面保留人工打开、检查和复现命令。

```powershell
$blender = 'D:\Program Files\Steam\steamapps\common\Blender\blender.exe'
$python = 'C:\Users\22797\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

& $blender reconstruction_v2/blends/35_gray_review.blend

# 固定照片相机预览，不保存模型修改
& $blender --background reconstruction_v2/blends/35_gray_review.blend --python reconstruction_v2/scripts/render_gray.py -- 62 63 64 69 r35
& $python reconstruction_v2/scripts/make_review_boards.py r35 62 63 64 69
& $python reconstruction_v2/scripts/make_stage_bc_comparison.py r35 r26

# 从实际求值网格检查名义尺寸
& $blender --background reconstruction_v2/blends/35_gray_review.blend --python reconstruction_v2/scripts/audit_gray.py

# 完整重放；必须给一个未使用过的输出前缀，已有输出会被拒绝
& $blender --background reconstruction_v2/blends/26_gray_review.blend --python reconstruction_v2/scripts/replay_r35.py -- my_r35_replay
```

## 参考与近似

官方来源包括[豪爵中国参数](https://en.haojue.com/NEWGSX250R/canshu.html)、[铃木零件目录](https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RAM1_GSX250RAZM1.pdf)、[铃木原厂转台](https://www.globalsuzuki.com/motorcycle/smgs/products/2021gsx250r/360viewer/)。[资料清单](references/sources.md)记录原始来源。爆炸图只说明分件和装配，不是精确尺寸图；车型家族资料也不能自动认定适用于用户具体年份。

发动机盖横向深度、壳厚、接缝及隔热罩间隙等仍有构造假设，详见 r35 记录。当前没有新的最终贴图、版画或磨损制作。

## 隐私

GitHub 只保存代码、文档及派生三维控制数据。原照片、含照片对照图、像素标注、镜头、参考下载、blend、渲染、车牌配置和相关成品仅保存在本地。当前灰模牌板空白，新增照片中的旧车牌不替换指定京 B。

旧图车尾的黑箱是已修正的二维尾包排除遮罩，并非模型尾箱。纯灰模面板现在显示完整模型，照片面板保留隐私遮蔽。

## r38 重放与检查

通过Blender MCP在独立的`36_gray_review.blend`中调用：

```python
import sys
sys.path.insert(0, "D:/Work/gadgets/GSX/reconstruction_v2/scripts")
import replay_r38
replay_r38.run("新的唯一前缀")
```

已有输出会被拒绝覆盖。重放包括r37尾部和r38油箱盖，保留编辑用布尔工具；`verify_r38.verify(参考源路径)`检查控制几何、相机、曲线和指定修改器。最新尾罩控制使用`data/revisions/r37_tail_assembly/Body_Tail.json`，不要用旧快照覆盖。检查不证明外形达到1:1。
