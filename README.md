# Suzuki GSX250R 实车重建

以本机 `IMG/` 的12张实车照片为依据，使用 **Blender 5.2.2 LTS / Blender MCP** 重建用户的 GSX250R。目标包含蓝白版画、荧光轮圈贴、对称三角护杠、手机支架、方向阻尼器及指定京B牌照；排除尾包、网绳、骑手和手套。

**当前：V2 / r20，车头、驾驶位及轮组/发动机外露结构已有改进，但阶段 B、C 均未通过 1:1 验收，不能报告完成。** 全部使用 Blender MCP，没有使用 Computer Use；尚未进入最终版画、材质、4K 和导出。

## 当前成果

项目位于 `D:\Work\gadgets\GSX`。r15及旧源保留；r16–r20是同一批次内部的候选和检查文件，不是已完成的阶段数量。

| 内容 | 本地路径 |
|---|---|
| 最新可编辑灰模 | `reconstruction_v2/blends/20_gray_review.blend` |
| 实车／r15／r20三角度并排图 | `reconstruction_v2/renders/stage_bc_r20_comparison.jpg` |
| 四角度照片／灰模／叠加／轮廓 | `reconstruction_v2/renders/review_r20_{62,63,64,69}.jpg` |
| 对照总览 | `reconstruction_v2/renders/review_r20_contact_sheet.jpg` |
| 车头、驾驶位及机械局部 | `reconstruction_v2/renders/stage_bc/r20_*.png` |
| 实际几何、接口与保护检查 | `reconstruction_v2/qa/geometry_r20.json`、`seat_interfaces_r20.json`、`stage_bc_r20.json`、`drive_r20.json` |
| 可编辑控制网格 | `reconstruction_v2/data/control_cages/` |

本轮补建大灯周围外壳、侧面回折和风挡底座，重排内衬及前罩接边；驾驶位新增分件仪表、四爪手机夹、阻尼器。轮辐改为闭合弯曲实体，制动盘增加真实通孔、分体卡钳及ABS槽圈；修正侧盖螺栓和排气入口未跟随历史发动机位移的问题。原胎纹、车架、摇臂、后减震、脚踏、侧撑及对称护杠保留。侧罩尖端增加支持截面，消除圆钝下垂；链传动按同车型目录的14/46齿、116节520链条重新约束，纠正原前链轮与发动机分离的布局。50槽ABS圈、5组制动盘固定件及3组感应圈固定件也已按目录纠正。

前罩保留三组隐藏四边面控制面，实时驱动1mm体素合并后的可见实体；控制面不单独导出。这用于修复薄壳重叠，不代表实测壁厚或制造拓扑。

**已核实：**审计分别列出未改结构与有意重建的传动对象，原照片相机保持不变；实际模型轴距1430mm、盘290/240mm、胎宽110/140mm满足名义构造检查。所查前罩、轮辐、侧盖、隔热罩和制动盘无非流形/退化面/实体自交；座垫对油箱及三处座尾分件未检出表面相交。这些不等于实车还原验收。

**仍未通过：**车头曲率、侧罩折面/开口、座尾形状与完整装配；机械铸件、盘孔模式、附件安装深度仍含近似。缺完整分件遮罩及两个有效独立角度，没有98%或整车还原率结论。[本轮结果和限制](reconstruction_v2/reviews/r20_stage_bc.md)。

## 后续路线与预算

用户已授权B/C并行推进；两者分别验收后才进入版画、最终材质和交付。下一批优先补前罩/侧罩的闭合可见区域、稳定特征及59/60等候选视角标定，再修控制曲面；机械部分先核对前链轮外罩、护杠支座、脚踏及悬挂连接；新链路的真实松弛量和安装深度仍未通过。

61初次自动提取误把同一前轮两段当成两轮，结果已否决。人工纠正后，真正后轮仍因遮挡而欠约束，不能作为通过的独立相机。62/63/69已用于形体调整，64欠约束，70失败。

此前10–14个大工作轮仍只是低可信度管理预算，当前证据不足以承诺完工轮数或r编号。同一误差连续两轮无实质改善，应改查证据、拓扑或装配，不能靠增加版本号放行。[阶段计划](reconstruction_v2/ITERATION_PLAN.md) · [问题清单](reconstruction_v2/ISSUES.md)。

## 隐私与文件范围

GitHub仅保存代码、文档和派生控制网格。真实照片、含原照对照图、私有车牌配置及相关成品不推送；参考下载、标注、相机、blend、渲染和QA也保持本地。当前灰模是空白牌板，没有真实牌号文字。

旧图里的车尾黑箱是已纠正的二维尾包排除遮罩，不是模型尾箱。当前纯灰模面板不绘制遮罩，原照和叠加面板保留带文字的隐私/遮挡区域。

## 重要命令

在项目根目录PowerShell运行：

```powershell
$blender = 'D:\Program Files\Steam\steamapps\common\Blender\blender.exe'
$python = 'C:\Users\22797\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

# 打开最新灰模
& $blender reconstruction_v2/blends/20_gray_review.blend

# 四角度低采样对照；不修改源文件
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/render_gray.py -- 62 63 64 69 r20
& $python reconstruction_v2/scripts/make_review_boards.py r20 62 63 64 69
& $python reconstruction_v2/scripts/make_stage_bc_comparison.py r20

# 实际几何、链传动及座尾接口检查
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/audit_gray.py
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/audit_drive.py
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/audit_tank_interface.py
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/audit_seat_interfaces.py

# 油箱局部原生渲染与分件颜色诊断；材料不保存回源
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/render_tank_review.py
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/render_tank_review.py -- --ids
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/render_tank_review.py -- --ids-full
# 对照需要本地照片、标注及已保留的r13基线渲染
& $python reconstruction_v2/scripts/review_tank_r15.py r15

# 显式同步控制数据到新源；拒绝覆盖和未经迁移的拓扑改变
& $blender --background reconstruction_v2/blends/20_gray_review.blend --python reconstruction_v2/scripts/apply_cages.py -- working_next.blend r21
```

Blender手改后先同步控制JSON或另存精修源，不能用旧JSON覆盖手改。两个隐藏座垫避让工具共享Seat_Rider.data，换数据块时须同步。旧迁移、拟合脚本只用于明确冻结输入，不是日常重建命令；r16/r18迁移要求本地r15_body_frozen，r20侧罩迁移要求归档的r19控制网格，缺失时拒绝替用当前控制数据；当前油箱拓扑不能直接同步到r13而忽略检查。Python科学依赖位于`.tools/calibration/`，公开仓库不能替代本地照片和标定。

## 尺度与来源

`+X`右、`+Y`前、`+Z`上；场景米制，控制网格毫米乘0.001。

[豪爵官方GSX250R-A参数](https://en.haojue.com/NEWGSX250R/canshu.html)提供轴距1430mm、前后盘290/240mm等名义约束；[铃木L8型录](https://www.suzuki.hu/motor/files/document/document/294/GSX250R_ABS_L8_EN.pdf)提供车型家族的25.6°后倾角/104mm拖曳距，具体年份适配未确认。爆炸图不是精确尺寸图，隐藏尺寸未验收。[证据索引](reconstruction_v2/references/evidence.md) · [零件核对](reconstruction_v2/references/review.md)。

历史：[r14油箱候选](reconstruction_v2/reviews/r14_tank_crown.md) · [r13接口](reconstruction_v2/reviews/r13_tank_rear.md) · [r12镜头敏感性](reconstruction_v2/reviews/r12_camera_sensitivity.md) · [r6.2冻结记录](docs/legacy_r6_2.md)。

链传动目录依据与构造假设详见[最终批次记录](reconstruction_v2/reviews/r20_stage_bc.md)。116个销轴的实测模型节距误差小于0.001mm，只证明名义链路构造一致，不代表实车毫米精度。
