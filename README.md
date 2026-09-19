# Suzuki GSX250R 实车重建

以本机 `IMG/` 的12张实车照片为依据，使用 **Blender 5.2.2 LTS / Blender MCP** 重建用户的 GSX250R。目标包括蓝白版画、荧光轮圈贴、对称护杠、手机支架、方向阻尼器和指定京B牌照；排除尾包、网绳、骑手及手套。

**当前 V2 / r26：阶段 B（准确灰模）、C（机械与附件）仍未通过，不能称完成或1:1。** 尚未进入最终贴花、材质、4K和导出。建模没有使用 Computer Use。

## 本轮收尾：r27 待验收候选

r26继续作为工作基线。本轮纠正侧罩外侧尖角的照片对应，制作4组前罩/侧罩/驾驶位控制候选并完成四角度检查。前上沿局部对齐改善，但前罩交界仍有重叠和自交候选，**r27没有提升为通过版本，B/C均未完成**。C本轮只有证据复核，没有新增机械建模。

候选源：`reconstruction_v2/blends/27_front_review_candidate.blend`；前后对照：`reconstruction_v2/renders/stage_bc_r27_comparison.jpg`；[检查、偏差与下一步](reconstruction_v2/reviews/r27_front_candidate.md)。候选控制单独在`data/revisions/r27_front_candidate/`，canonical控制仍保留r26。

## 上一批已保留成果（r26）

项目路径：`D:\Work\gadgets\GSX`。本批次从r20连续修改到r26，旧源和失败候选保留。

| 内容 | 本地路径 |
|---|---|
| 最新可编辑源 | `reconstruction_v2/blends/26_gray_review.blend` |
| 实车／r20／r26三角度对照 | `reconstruction_v2/renders/stage_bc_r26_comparison.jpg` |
| 四角度照片／灰模／叠加／边界 | `reconstruction_v2/renders/review_r26_{62,63,64,69}.jpg` |
| 检查总览 | `reconstruction_v2/renders/review_r26_contact_sheet.jpg` |
| 本批次结果与偏差 | [r26记录](reconstruction_v2/reviews/r26_stage_bc.md) |
| 可编辑控制网格 | `reconstruction_v2/data/control_cages/` |
| 冻结重放输入 | `reconstruction_v2/data/revisions/r24/`、`r25/`、`r26/` |
| 本地检查 | `reconstruction_v2/qa/increment_r26.json`、`replay_r26.json` |

本批次调整风挡上缘，重建圆角镜壳和镜片；重做座下三角侧盖并替换旧件，补出左侧前链轮外罩；重新制作较短的后减震弹簧段、筒体、安装眼、贯穿轴、垫圈、双耳和紧凑连接横梁。r24曾误将新旧侧盖叠放，r25已清理，旧侧盖并非原本不存在。

另外按实车分别重建左右脚踏架及长孔、折叠脚踏、换挡连杆和后刹操纵件，纠正旧脚踏明显偏前的位置。护杠后连接改成镜像扁条并接到安装点。详细局部对照：`reconstruction_v2/renders/rearset_r26_comparison.jpg`。

局部几何检查覆盖99个本批次部件，未检出所查非流形、退化面或自交；侧盖、链轮外罩和减震对指定相邻部件的非配合表面相交已消除。22组控制网格与源同步。实际从r20重放后，926对象的几何、变换和相机签名一致。**这些检查不等于外形、所有修改器/材质或整车机械验收。**

70右后照片得到新的相机诊断候选：轮圈RMS约0.62px；轮圈半径假设变化仍会影响镜头位置。正式相机没有替换，不能把这个分数称整车相似度或独立角度已通过。

## 尚未通过与后续

车头包裹曲率、侧罩折面/开口、油箱肩部、座尾体量仍有可见差异；脚踏/脚踏架、发动机铸件、排气细部及附件安装深度未验收。脚踏位置已有可见改善，但隐藏安装深度和操纵行程未验收。下一主项是车头—侧罩整个装配组的多角度可见边界与控制网格；C同步处理发动机铸件和排气。

完整闭合分件标注、两张可靠独立角度、98%轮廓与正式关键点门槛尚未通过。隐藏尺寸继续标为未验证。当前无法给出可信的完工轮数，r编号只表示源文件修订。[阶段计划](reconstruction_v2/ITERATION_PLAN.md) · [问题清单](reconstruction_v2/ISSUES.md)。

## 隐私

GitHub只保存代码、文档和派生三维控制。真实照片、含原照对照、标注、镜头、参考下载、blend、渲染、车牌配置和相关成品均保持本地。当前灰模牌板空白。

旧图中的尾部黑箱是已纠正的二维尾包排除遮罩，不是模型尾箱。当前纯灰模面板没有该遮罩，照片面板保留隐私遮蔽。

## 重要命令

在项目根目录的PowerShell运行；自动建模仍使用Blender MCP，下列命令用于本地检查和复现。

```powershell
$blender = 'D:\Program Files\Steam\steamapps\common\Blender\blender.exe'
$python = 'C:\Users\22797\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

# 打开最新源
& $blender reconstruction_v2/blends/26_gray_review.blend

# 固定照片相机的低采样对照，不修改源
& $blender --background reconstruction_v2/blends/26_gray_review.blend --python reconstruction_v2/scripts/render_gray.py -- 62 63 64 69 r26
& $python reconstruction_v2/scripts/make_review_boards.py r26 62 63 64 69
& $python reconstruction_v2/scripts/make_stage_bc_comparison.py r26 r20

# 实际求值几何和本批次保护范围检查
& $blender --background reconstruction_v2/blends/26_gray_review.blend --python reconstruction_v2/scripts/audit_gray.py
& $blender --background reconstruction_v2/blends/26_gray_review.blend --python reconstruction_v2/scripts/audit_reconstruction_increment.py

# 从保存的r20重放本批次；每次使用新的输出前缀，拒绝覆盖旧文件
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/replay_r26.py -- verify_new

# 仅同步兼容控制网格到一个新源文件
& $blender --background reconstruction_v2/blends/26_gray_review.blend --python reconstruction_v2/scripts/apply_cages.py -- working_next.blend r27
```

手工精修后先同步控制JSON或另存源，不能用旧JSON覆盖修改。历史迁移脚本只用于其指定基线，不能对精修源反复运行。前罩三组隐藏四边面驱动可见合并外壳；座垫、输出链路及前链轮盖的隐藏避让工具是修改器依赖，不能删除。科学依赖在`.tools/calibration/`，照片对照需要本地照片与标定，公开仓库不包含它们。

## 尺度与资料

`+X`右、`+Y`前、`+Z`上；Blender场景米制，控制数据以毫米记录。轴距1430mm、前后制动盘290/240mm、胎宽110/140mm是名义构造约束，不是用户实车的实测结果。

[豪爵官方参数](https://en.haojue.com/NEWGSX250R/canshu.html) · [铃木家族零件目录](https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RAM1_GSX250RAZM1.pdf) · [DID链条规格](https://didmc.com/chain/engine/) · [证据索引](reconstruction_v2/references/evidence.md)。具体年份适配和隐藏尺寸未确认；爆炸图不能当尺寸蓝图。

历史：[r20链传动与覆盖件](reconstruction_v2/reviews/r20_stage_bc.md) · [r15油箱](reconstruction_v2/reviews/r15_tank_full.md) · [r6.2冻结记录](docs/legacy_r6_2.md)。
