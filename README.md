# Suzuki GSX250R 实车重建

以本机 `IMG/` 的 **12 张实车照片**为外观依据，使用 **Blender 5.2.1 LTS / Blender MCP** 重建。目标包含蓝白版画、荧光轮圈贴、对称三角管护杠、手机支架、方向阻尼器及指定的京 B 车牌；排除尾包、网绳、手套和骑手。

**当前：V2 / r09 座尾灰模候选，第一里程碑未通过，尚未达到 1:1。** 车头、座尾曲面和机械结构仍有明显偏差。灰模通过前，不制作新版完整贴花、最终材质、4K 成片或三格式交付。旧 r6.2 已冻结，只作失败对照。

## 当前文件

项目：`D:\Work\gadgets\GSX`。

| 内容 | 本地路径 |
|---|---|
| 最新可编辑灰模 | `reconstruction_v2/blends/09_gray_review.blend` |
| 四角度四联对照总览 | `reconstruction_v2/renders/review_r09_contact_sheet.jpg` |
| 原照／灰模／叠加／轮廓对照 | `reconstruction_v2/renders/review_r09_{62,63,64,69}.jpg` |
| 灰模透明渲染 | `reconstruction_v2/renders/gray_r09_*.png` |
| 实际几何检查 | `reconstruction_v2/qa/geometry_r09.json` |
| 对照状态、哈希和错误说明 | `reconstruction_v2/qa/review_r09.json`、`seat_tail_r09.json` |
| 可编辑控制网格 | `reconstruction_v2/data/control_cages/`，19 个四边面网格 |
| 护杠和镜壳控制数据 | `reconstruction_v2/data/guard_control.json`、`mirror_control.json` |
| 尚未解决的问题 | [ISSUES.md](reconstruction_v2/ISSUES.md) |
| 官方证据 | [资料索引](reconstruction_v2/references/evidence.md)、[件号核对](reconstruction_v2/references/review.md) |

r01–r08 的独立文件仍保留。当前 Blender 会话中已通过 MCP 追加并显示 r09，旧场景没有被清空。

用户已授权推送非照片内容。GitHub 保存代码、文档和控制网格；**真实照片、含原照的对照图、真实车牌配置及相关成品不推送**。本次继续将参考下载、照片标注、相机参数、blend 和检查渲染保存在本地。灰模车牌为空白，无真实号牌文字。

## 迭代路线

详见[迭代路线与每轮验收](reconstruction_v2/ITERATION_PLAN.md)。当前只处于准确灰模阶段；r09继续聚焦座尾；局部仍未通过，先继续座尾，再依次处理油箱、车头和侧罩。

对照图的纯灰模面板现已取消排除遮罩，显示完整模型。原照、叠加、轮廓面板用带文字斜线区标明排除区域；旧图中的车尾黑箱是尾包遮罩，不是模型部件。该展示纠正发生在r08，不计为形体进步。

## r09 本轮结果

本轮只修后座、尾罩及可见过渡壳；没有更改相机。新增[本轮误差与回退记录](reconstruction_v2/reviews/r09_seat_tail.md)，本地对照图为 `reconstruction_v2/renders/seat_tail_r09_comparison.jpg`。

69号照片中，后座轮廓距离中位数从36.2降至3.6 px，P95从50.2降至14.9 px。这是候选镜头下的局部拟合诊断，人工描边约±4 px，**不能解释为整车完成度或1:1通过**。骑手座试改使侧面部分误差增大，已回退；骑手座及相邻侧板保持r08。

尾罩下缘、骑手座曲率、后座圆角和支座连接仍未通过。约90 mm量级的后座高度校正依赖候选相机，尚无独立角度和实测支撑。继续座尾，不进入油箱或最终材质。

## r08 历史改变

- 将油箱侧黑饰板按照片接缝重画；取消侧整流罩上错误的分离接缝，把向下延伸的部分接成连续四边面曲面。
- 修正油箱端部控制点反折、旧尾罩遮挡座下侧板的问题；根据新左前照片修补座垫与侧板间的缺口。
- 将椭圆状护杠改为三角直管、短弯角、支座及滑块，左右镜像。隐藏安装深度尚未验证。
- 加入独立驾驶位黑色内衬、狭长位置灯分件，调整后视镜背壳轮廓与朝向；这些仍是待校正的形体。
- 62/63：从真实照片得到 61 个去重 SIFT 对应点，剔除两组误匹配；59 个点参与联合诊断，其中 12 个不参与拟合。保留点的极线误差中位数从约 2.91 px 降至 0.17 px、P95 从 4.97 px 降至 1.53 px。**这是照片之间的一致性检查，不是模型相似度。** 特征集中在贴纸区，仍有分布局限。
- 新照片 69 为左前方、70 为右后方，均已本地归档。69 使用倾斜转向轴后，轮圈拟合 RMS 约 0.39 px；70 仍约 9.0 px 且触及参数边界，标为失败诊断，不能验收。
- 69 是早期单滑块状态，其对照临时隐藏当前三角护杠。最新源文件仍保留用户要求的三角护杠；新图中的旧车牌不替换指定京 B。
- 求值网格实测轴距约 1430.0001 mm、前后盘约 290/240 mm、胎宽约 110/140 mm；18 个主要控制网格均为四边面。这里只证明模型符合部分名义构造尺寸。

## 未通过的检查

r09新增了局部座垫人工描边诊断；尚无经过复核的完整整车与主要分件遮罩，因此整体验收 IoU 仍为未评估，**没有达到 98% 的声明**。橙色线只是局部人工可见边缘，橙色点是实际轮圈贴像素，不是完整分割。青色是灰模外轮廓。

没有可用 EXIF；焦距、主点、轮圈贴实际半径和畸变仍存在不确定性。圈贴半径采用 `220 ± 5 mm`，不能把 17 寸胎圈座直径当成可见圈贴直径。62/63 的旧轮组转向模型仍简化，69/70 新诊断使用倾斜轴；统一更新需重新生成和复核所有对照。

64 前轮裁切，69 为候选，70 相机失败。66 已用于灯组和镜壳参考，不能再称为独立保留角度；61 仍未用于本轮形体调整。至少两个有效独立角度的门槛未通过。隐藏尺寸、机械外壳、排气、前叉装配和支架均未获得实车精度证明。

## 尺度与资料

`+X` 右、`+Y` 前、`+Z` 上，场景米制、控制网格毫米，写入时乘 0.001，场景 `scale_length=1`。

[豪爵 GSX250R-A 参数](https://en.haojue.com/NEWGSX250R/canshu.html)用于轴距 1430 mm、前后盘 290/240 mm、轮胎规格、座高 790 mm等名义尺度。[铃木 L8 官方型录](https://www.suzuki.hu/motor/files/document/document/294/GSX250R_ABS_L8_EN.pdf)第 1/8 页提供 25.6° 后倾角与 104 mm 拖曳距；它是其他年份/市场的车型家族资料，与用户车辆的精确适配尚未确认。GSX250R-F 资料不混用。爆炸图和转台照片不是尺寸蓝图。

## 重要命令

在项目根目录 PowerShell 运行：

```powershell
$blender = 'D:\Program Files\Steam\steamapps\common\Blender\blender.exe'
$python = 'C:\Users\22797\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

# 打开最新独立灰模
& $blender reconstruction_v2/blends/09_gray_review.blend

# 重建四角度诊断图；64欠约束，69候选，70失败不参与本轮像素验收
& $blender --background reconstruction_v2/blends/09_gray_review.blend --python reconstruction_v2/scripts/render_gray.py -- 62 63 64 69 r09
& $python reconstruction_v2/scripts/make_review_boards.py r09 62 63 64 69
& $blender --background reconstruction_v2/blends/09_gray_review.blend --python reconstruction_v2/scripts/audit_gray.py

# JSON 同步到新文件：拒绝覆盖已有文件，拒绝未经迁移的拓扑变化
& $blender --background reconstruction_v2/blends/09_gray_review.blend --python reconstruction_v2/scripts/apply_cages.py -- working_next.blend r10
```


局部对照复算（依赖本地冻结相机和座尾描边）：

```powershell
& $blender --background reconstruction_v2/blends/08_gray_review.blend --python reconstruction_v2/scripts/export_tail_meshes.py
& $blender --background reconstruction_v2/blends/09_gray_review.blend --python reconstruction_v2/scripts/export_tail_meshes.py
& $python reconstruction_v2/scripts/review_tail.py
```

照片匹配工具依赖隔离在 `.tools/calibration/` 的 NumPy、SciPy、OpenCV。`match_reference_pair.py` 和 `joint_calibration.py` 生成本地诊断，不代表模型通过。`calibrate_added_photos.py` 默认保留现有标注；`fit_added_review.py` 生成新图候选并按残差标记失败。

`prepare_r05.py`、`refine_r06.py`、`refine_r07.py`、`refine_r08.py`、`refine_tail_r09.py`、`upgrade_r05.py` 是本轮历史迁移，**不要对精修后的数据随意重复运行**。`apply_cages.py` 以 JSON 为权威，Blender 手改后应先同步控制网格或另存，防止精修丢失。重新克隆时需恢复本地参考与标定，公开代码不足以替代这些证据。

下一步继续座尾：骑手座曲率、尾罩连接和独立角度；镜头修订另立标定记录，不与形体修改混记。通过灰模后才进入机械细节、逐笔贴花、实物磨损、PBR/UV，以及最终源文件、FBX/GLB/OBJ 和六张 4K 图。旧流程见 [r6.2 历史记录](docs/legacy_r6_2.md)，不要对新版运行旧 `build_all.py`。