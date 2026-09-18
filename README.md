# Suzuki GSX250R 实车重建

以 `IMG/` 中的十张车主照片为外观依据，通过本机 **Blender 5.2.1 LTS / Blender MCP** 重建蓝白版 GSX250R。最终保留三角管护杠、手机支架、方向阻尼器及用户指定的京 B 车牌；排除尾包、网绳、手套和骑手。

**当前为 V2 / r04 灰模重建，第一里程碑尚未通过。不是 1:1 已验收成品。** r6.2 的外观已被否决，旧文件只作失败对照；旧 4K 图和旧三格式导出不代表新版。新版不含贴花或最终材质，错误的“ヨシムラ”字样没有进入新版。

## 现在查看什么

项目根目录：`D:\Work\gadgets\GSX`。

| 内容 | 本地路径 |
|---|---|
| 最新可编辑灰模 | `reconstruction_v2/blends/04_gray_review.blend` |
| 前三轮独立源文件 | `reconstruction_v2/blends/01_gray_r01.blend`、`02_gray_r02.blend`、`03_gray_review.blend` |
| 三视角四联对照总览 | `reconstruction_v2/renders/review_r04_contact_sheet.jpg` |
| 每角度原照／灰模／叠加／轮廓 | `reconstruction_v2/renders/review_r04_62.jpg`、`review_r04_63.jpg`、`review_r04_64.jpg` |
| 灰模原始透明渲染 | `reconstruction_v2/renders/gray_r04_*.png` |
| 实际几何测量 | `reconstruction_v2/qa/geometry_r04.json` |
| 验收状态与误差说明 | `reconstruction_v2/qa/review_r04.json`、[差距记录](reconstruction_v2/ISSUES.md) |
| 可编辑四边面控制网格 | `reconstruction_v2/data/control_cages/*.json` |
| 官方资料及版本排除 | [资料索引](reconstruction_v2/references/evidence.md)、[件号复核](reconstruction_v2/references/review.md) |
| 旧版冻结与哈希 | `reconstruction_v2/baseline/` |

用户已明确授权将代码、文档和控制网格推送到此公开仓库；真实照片及含原照的对照图不推送。

原照片、照片标注、镜头参数、参考下载、源文件、渲染和真实号牌配置只保存在本地，不上传 GitHub。仓库保存脚本、控制网格、文档和公开资料索引。没有修改原照片；私有号牌配置仍保留，灰模只使用空白牌板。

## 已落实的工作

- 冻结 r6.2 源文件和状态，使用新增独立场景重建，不清空用户当前 Blender 场景。
- 建立油箱、座垫、尾罩、侧整流罩、下包围、上罩、座下侧罩、三角侧盖、风挡、灯罩与挡泥板等 **16 份四边面控制网格**；保留镜像、细分和厚度修改器。
- 62、63 两张照片以真实荧光轮圈贴弧线与轮心拟合相机；保存焦距、姿态、前轮转向参数和版本。相机按轮组证据校正，不以车身观感任意调镜头。
- 64 作为左侧独立诊断视角。其前轮严重裁切，镜头仍欠约束，不能计为已通过的独立标定。
- 为上述三视角建立固定排除区和四联对照。轮廓页青色为灰模外轮廓，橙色为已标注的实物边缘／轮圈点；橙色并不是完整前景分割。
- 修正座下侧盖缺失、上罩侧面缺失及发动机、脚踏、护杠的明显位置偏差。机械件仍属于待逐件重核的占位结构。
- 几何检查直接读取求值后的网格：轴距约 **1430.0001 mm**；制动盘约 **290 / 240 mm**；胎宽约 **110 / 140 mm**。这些是模型对公开名义尺寸的检查，不是对实车的测量证明。

## 当前不能宣称完成的部分

轮圈贴中心的实际半径仍采用 `220 ± 5 mm` 估计；17 寸是轮胎胎圈座直径，不能直接当作可见轮圈外缘。没有 EXIF，镜头畸变尚未标定，车身侧倾包含在相对相机姿态中。低轮圈残差不能证明车身形状正确。

尚无通过复核的完整整车及分件遮罩，因此 **没有公布轮廓 IoU，也没有声称达到 98%**。车身关键点误差门槛与至少两个可靠独立视角的门槛均未通过。61、66 暂保留，未参与本轮控制网格调整；驾驶位 65 和后部照片仍需后续匹配。

车头、风挡、镜子、座尾曲率、外露机械形状及护杠安装关系仍有可见差距。材质、逐笔贴花、真实磨损、UV、最终三格式导出及六张 4K 图尚未开始新版制作。不得以文件存在或尺寸检查通过代替外观验收。

## 尺寸与证据

`+X` 向右、`+Y` 向前、`+Z` 向上。场景按米，控制网格按毫米除以 1000 写入，`scale_length=1`，不再重复缩小。

[豪爵 GSX250R-A 官方参数](https://en.haojue.com/NEWGSX250R/canshu.html)确认轴距 1430 mm、前后盘 290/240 mm、轮胎 110/80-17 与 140/70-17、座高 790 mm、油箱 15 L。GSX250R-F 的资料已排除。其他市场的铃木零件目录仅提供同车型家族分件和结构证据；中国实车的年份和具体件号仍需交叉核对。爆炸图和官方转台照片都不是尺寸蓝图。

原厂长宽高 2085×740×1110 mm 不用来强行缩放包含护杠、支架及镜子调整的整个模型包络。

## 重要命令

在项目根目录的 PowerShell 运行：

```powershell
$blender = 'D:\Program Files\Steam\steamapps\common\Blender\blender.exe'
$python = 'C:\Users\22797\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

# 打开最新独立灰模
& $blender reconstruction_v2/blends/04_gray_review.blend

# 按当前相机重新渲染本轮灰模、生成对照和检查报告
& $blender --background reconstruction_v2/blends/04_gray_review.blend --python reconstruction_v2/scripts/render_gray.py -- 62 63 64 r04
& $python reconstruction_v2/scripts/make_review_boards.py r04
& $blender --background reconstruction_v2/blends/04_gray_review.blend --python reconstruction_v2/scripts/audit_gray.py

# 从 JSON 控制网格生成新的独立修订文件；不会改写输入 .blend
& $blender --background reconstruction_v2/blends/04_gray_review.blend --python reconstruction_v2/scripts/apply_cages.py -- working_next.blend

# 相机拟合默认保留已有参数；证据修正后才显式重拟合，并自动归档旧参数
& $python reconstruction_v2/scripts/fit_cameras.py
# & $python reconstruction_v2/scripts/fit_cameras.py --refit
```

相机工具使用隔离于 `.tools/calibration/` 的 NumPy、SciPy 和 OpenCV。重新克隆时，先在本机恢复原照片和本地标注／相机数据；不能把缺少证据的构建当成车主版重建。

`initialize_cages.py` 只用于首次初始化，遇到已有控制网格会拒绝覆盖。`apply_cages.py` 明确以 JSON 为准；在 Blender 中手工精修后，应先将修改写回控制网格或保存独立源文件，避免把精修网格同步回旧数据。`upgrade_r03.py` 是一次历史迁移，不能代替日常编辑入口。

## 后续推进顺序

1. 继续第一里程碑：完善稳定关键点和闭合分件遮罩，解决镜头欠约束；修正灰模并通过至少两个可靠独立视角。
2. 主要覆盖件通过后，再逐件重建驾驶位、灯具、轮组机械和实车改装件。
3. 最后制作实车矢量贴花、明确可见的磨损、材质与 UV，完成新版源文件、FBX/GLB/OBJ 和六张 4K Cycles 图。

每阶段保存独立版本、保留误差记录。旧版说明及命令已归档为 [r6.2 历史记录](docs/legacy_r6_2.md)，不要对新版运行旧 `build_all.py`。
