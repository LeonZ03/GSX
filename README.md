# GSX250R 实车重建

以车主提供的 10 张多角度实车照片为主要依据，用 Blender Python 与 Blender MCP 从零制作的 Suzuki GSX250R/A 可编辑模型。采用照片中的蓝色车身、白色大幅字样、荧光黄轮圈贴、黑色三角管护杠、左侧手机支架及京 B 黄色车牌；不含尾包、网绳、手套和骑手。

**当前状态：可编辑重建首版 r6.2，完整文件管线已建立，但尚未达到 100% 外观还原，也不是扫描、测绘或可制造 CAD。** 头灯/车头曲率、整流罩接缝、大字版画形状、发动机铸件与小贴纸仍有可见近似。4K 表示输出分辨率，不表示已经达到摄影级真实性。

按用户补充，以本机 **Blender 5.2.1 LTS** 为准，不再以 Blender 4.x 为交付要求。脚本不依赖收费模型、生成图片贴图或网上下载的成品三维模型。

## 本地交付

项目目录：`D:\Work\gadgets\GSX`。用户原始照片保留在 `IMG/`，没有修改。

| 内容 | 路径 |
|---|---|
| 可编辑源文件 | `blends/10_final.blend` |
| 十阶段快照 | `blends/01_reference.blend` 到 `blends/10_final.blend` |
| 求值后的网格版 | `exports/GSX250R_evaluated.blend` |
| GLB | `exports/GSX250R.glb` |
| FBX | `exports/GSX250R.fbx` |
| OBJ 与材质 | `exports/GSX250R.obj`、`exports/GSX250R.mtl` |
| 4K Cycles 渲染 | `renders/final/` |
| 隐藏真实牌号的检查图 | `renders/checks/` |
| 官方 PDF、零件图页、八个转台视角 | `references/public/` |
| 参考来源 | [references/sources.md](references/sources.md) |
| 尺寸、导出与回导报告 | `qa/dimensions.json`、`qa/export_report.json`、`qa/roundtrip.json` |

本地产物、原照片、车牌配置和第三方参考下载不提交 Git。GitHub 保存脚本、需求、来源索引和开发记录。重新克隆后须使用本地原照片与私有配置才能构建车主版；缺少私有配置时自动使用通用占位牌号。

## 已建立的结构

- 按名义轮胎规格建立前后轮，十辐条轮毂、几何胎纹、实孔刹车盘、ABS 圈、卡钳、轮轴、气门嘴和荧光贴环。
- 正立前叉、上下联板、分体车把、开关、拉杆、后视镜、前挡泥板、风挡、中央大灯、位置灯、转向灯、数字仪表与钥匙孔。
- 发动机外壳、缸体/缸头、散热器、水管、车架、摆臂、减震、链轮和链条、脚踏、侧撑、双排气头段、消音器与独立隔热罩。
- 油箱、座垫、尾罩、侧罩、下包围、加油口、牌照架、尾灯、线管和常见紧固件。
- 自制几何文字/贴花、PBR 表面、打包 HDRI、四盏工作室面积灯与多个相机。

首版采用程序化曲面、实体化、倒角、细分和独立零件。r6.2 已将车头上罩与侧罩改为共享边界的连续曲面，重新制作盾形灯罩、内凹反射碗和风挡。两侧指定基础网格边界的坐标检查误差为 0 mm（不代表整车所有接缝或实体化厚度均已验证）。车身仍需要进一步手工造型及逐角度拟合，不能把上述结构清单理解为每个原厂零件都已精确复刻。

## 尺寸与坐标

`+X` 为车辆右侧，`+Y` 为前方，`+Z` 向上。网格单位为米，脚本中的构造数值按毫米乘 `0.001` 转换，因此场景 `scale_length=1`，不会再重复缩小。

| 项目 | 官方/输入基准 | 当前模型 |
|---|---:|---:|
| 轴距 | 1430 mm | 1430 mm 构造锚点 |
| 全长 | 2085 mm | 2074.2 mm |
| 全宽 | 740 mm | 736.4 mm |
| 全高 | 1110 mm | 1102.0 mm |
| 座高 | 790 mm | 以 790 mm 座面控制点构造，曲面存在局部起伏 |
| 前胎 | 110/80-17 | 名义宽 110、外径 607.8 mm |
| 后胎 | 140/70-17 | 名义宽 140、外径 627.8 mm |

尺寸来自求值网格，不使用 Blender 5.2 对部分 Curve 对象返回的异常扩大包围盒。护杠主要控制点左右镜像误差为 0 mm。该检查没有测量实车管径或隐藏安装点。

官方规格交叉核对：248 cc 水冷 SOHC 并列双缸、15 L 油箱、18.4 kW / 8000 rpm、23.4 N·m / 6500 rpm。早期 ABS 官方型录标注整备质量 181 kg，与需求中的“约 178 kg”存在版本差异，未把不同市场年份混为同一实车测量值。来源见来源索引。

## 实车识别与不确定项

| 部位 | 采用依据 | 仍存在的近似 |
|---|---|---|
| 蓝色漆、白字版画 | 用户 62、63、64、66 号照片 | 照片光照不同，未取得实体色卡；大字用重新制作的粗体几何近似，并非原厂贴花矢量 |
| 护杠 | 62、63 的黑色三角管架；用户要求两侧对称 | 25 mm 管径、隐藏支座和三维伸出量为图像估计；未做应力/装配验证 |
| 车牌 | 用户明确选京 B，与 57、59 一致 | 文字已录入本地私有配置；牌照字体、圆角、固定螺钉尺寸为近似 |
| 手机支架与阻尼器 | 65 驾驶位近照 | 左把安装位置、四角夹持和横向阻尼器已建立；背面机构、品牌和精确长度未知 |
| 尾部 | 57、59、64 与原厂公开图 | 去掉尾包/网绳后，部分原来被遮挡的尾罩、后座采用原厂结构推定 |
| 发动机/底部 | 官方零件目录，实车外露部分 | 铸件、管线、传感器、底面内部简化；没有完整标定底视照片 |
| 头灯、风挡、镜子 | 58、61、65、66 与官方 360 图 | 曲率、灯内反射器、镜面轮廓仍偏近似；接缝不能宣称与原厂一致 |
| 小标识、使用痕迹 | 照片能辨识处 | 若干小标识、字形、轮胎品牌、磨损、油漆划痕未逐一复制 |

原照片都是透视照片；没有伪称找到官方正交蓝图。`01_reference.blend` 含四个图片空物体、正交相机与尺寸辅助线，图片摆放是近似参考定位，不能当作镜头标定完成或四视图严格对齐。

## 重要命令

也可以使用统一入口：`./scripts/gsx.ps1 -Task Build`、`-Task Preview`、`-Task Export`、`-Task Validate`、`-Task Render`；`-Task All` 执行完整本地流程。

在项目根目录的 PowerShell 中运行。下列命令默认使用本机 Steam 安装位置，可根据实际路径调整。

```powershell
$blender = 'D:\Program Files\Steam\steamapps\common\Blender\blender.exe'

# 打开可编辑源文件
& $blender blends/10_final.blend

# 从零重建十阶段快照，再执行外观修正，生成最新源文件
& $blender --background --factory-startup --python scripts/build_all.py

# 快速检查，自动将预览中的牌号替换为通用文本
& $blender --background blends/10_final.blend --python scripts/render.py -- --preview

# 4K Cycles：真实车牌保留在本地输出
& $blender --background blends/10_final.blend --python scripts/render.py -- Camera_Front_3Q Camera_Right_Ortho Camera_Rear_3Q Camera_Left_3Q Camera_Cockpit Camera_Wheel_Detail

# 输出 GLB / FBX / OBJ，随后做三格式回导检查
& $blender --background blends/10_final.blend --python scripts/export_model.py
& $blender --background blends/10_final.blend --python scripts/validate_source.py
& $blender --background --factory-startup --python scripts/validate_exports.py
```

MCP 建模用 `execute_blender_code` 调用项目脚本；后台环境需要窗口上下文时使用 `bpy.context.temp_override(window=bpy.context.window_manager.windows[0])`。初次构建请使用 `build_all.py`；单独重复运行修正脚本可能再次缩放灯光或局部几何。

## 渲染与导出设置

最终渲染为 Cycles、3840×2160、160 samples 上限、自适应阈值 0.01、降噪、AgX。优先 OptiX GPU；本机 RTX 3050 Ti Laptop 4 GB。环境使用本机 Blender 自带 `studio.exr` 并打包到 `.blend`。背景与工作室灯光保留在源文件，不进入模型导出。

可编辑源保留造型修改器。导出副本将曲线、文字与修改器求值成网格，保留零件名、米制单位与材质。GLB 使用标准 Y-up 转换；FBX/OBJ 指定 Y forward / Z up。OBJ 材质依赖同目录 MTL。

当前导出约 36.6 万顶点、41.1 万面，不是移动端优化资产。每个导出网格均有 UV 和材质。导出副本使用 Smart UV Project，按部件分岛排列到各自 0–1 范围，并检查无非有限坐标或越界；不同部件复用 UV 空间。可编辑源保留基础 UV，整理后的 UV 在求值网格版与三格式导出中。**尚未制作整车共用的烘焙图集或统一纹素密度**。Blender 程序化微观凹凸、复杂玻璃和某些表面节点不能在 FBX/OBJ 中完全等价还原；跨软件优先 GLB 或 `.blend`。

## 本次文件验收

已完成 10 个阶段 .blend、3 种模型导出及 6 张 3840×2160 Cycles 渲染。导出分别回读验证，尺寸一致，无材质/UV 缺失；完整重建在无私有输入的隔离目录通过。文件哈希和分辨率记录于本地 qa/artifact_manifest.json，概要为 qa/delivery.json。最终视角为 Front_3Q、Right_Ortho、Rear_3Q、Left_3Q、Cockpit、Wheel_Detail。

这些通过项针对文件完整性和可重复运行，不替代实车外观精度验收。

## 后续精修优先级

1. 根据照片校正车头/侧罩连续曲率与接缝，修整局部穿插及遮挡关系。
2. 逐笔描绘真实 SUZUKI 大字与小贴纸，替换当前近似字形。
3. 校正发动机铸件、排气端盖、轮胎胎纹与磨损；补充支架背面、护杠隐藏固定点证据。
4. 制作统一纹素密度的整车烘焙图集、降低面数，再做渲染器之间的外观一致性检查。

不得在没有这些验证的情况下把当前首版标为“100%还原”“测绘精度”或“已完成产品摄影级验收”。
