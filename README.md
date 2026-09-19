# Suzuki GSX250R 实车重建

以本机 `IMG/` 的12张实车照片为依据，使用 **Blender 5.2.2 LTS / Blender MCP** 重建用户的 GSX250R。目标包含蓝白版画、荧光轮圈贴、对称三角护杠、手机支架、方向阻尼器及指定京B牌照；排除尾包、网绳、骑手和手套。

**当前：V2 / r15，油箱整段曲面连续重修。准确灰模阶段仍未通过，尚未达到1:1。** 本轮没有使用Computer Use。主要车身曲面、车头、机械结构与实车仍有明显差距，灰模通过前不做最终贴花、材质、4K成片和三格式交付。

## 当前成果

项目位于 `D:\Work\gadgets\GSX`。r13、r14及旧r6.2源保留；r15只改变油箱及随表面调整的油箱盖，相机和其它18个控制网格不变。

| 内容 | 本地路径 |
|---|---|
| 最新可编辑灰模 | `reconstruction_v2/blends/15_gray_review.blend` |
| 油箱三角度改前/改后/叠加 | `reconstruction_v2/renders/tank_crown_r15_comparison.jpg` |
| 四角度整车对照 | `reconstruction_v2/renders/review_r15_{62,63,64,69}.jpg` |
| 对照总览 | `reconstruction_v2/renders/review_r15_contact_sheet.jpg` |
| 实际几何及接缝检查 | `reconstruction_v2/qa/geometry_r15.json`、`tank_interface_15_gray_review.json`、`seat_interfaces_r15.json` |
| 照片距离与冻结检查 | `reconstruction_v2/qa/tank_review_r15.json`、`tank_frozen_r15.json` |
| 可编辑控制网格 | `reconstruction_v2/data/control_cages/` |

本轮连续比较了后部、肩部、端盖和完整上缘候选；复核发现侧面上缘约束遗漏后，修正程序并继续迭代到r15。油箱前后端封闭，控制网格为80顶点/69四边面；保留镜像、细分和可撤销座垫避让，移除不适用的重复内壳，最大控制点位移约49.1 mm。

实际渲染的开放边界平均距离如下。它们是局部诊断，**不是整车还原率**；标注约±4–5px，三个角度均参与拟合。

| 检查区域 | r13 | r15 |
|---|---:|---:|
| 62侧面油箱上缘 | 13.62 px | 4.31 px |
| 69左前油箱上缘 | 17.05 px | 0.71 px |
| 62后缘 | 21.17 px | 16.71 px |
| 63后缘 | 3.82 px | 1.49 px |

**仍未解决：**62后缘与前端局部曲率、肩部折线和座垫接缝。69后缘均值2.82→3.15px、接缝2.86→4.33px，略有退步；不能把上缘改善说成整个油箱已通过。最终局部油箱/座垫未检出自交、非流形边或表面相交；全车装配未验收。详见[本轮误差及限制](reconstruction_v2/reviews/r15_tank_full.md)。

## 下一步

继续油箱肩部、62后缘和接缝；补跨图稳定特征，必要的镜头修订单独记录。之后再处理车头/侧罩及外露机械、附件，最后进入贴花、PBR/UV、六张4K和FBX/GLB/OBJ。

62/63镜头仍为候选，69未定型，64裁切欠约束，70拟合失败；两个有效独立角度和完整分件遮罩尚未具备。不用轮圈拟合残差或名义尺寸代替整车验收。[迭代路线](reconstruction_v2/ITERATION_PLAN.md) · [问题清单](reconstruction_v2/ISSUES.md)。

## 隐私与文件范围

GitHub仅保存代码、文档和派生控制网格。真实照片、含原照对照图、私有车牌配置及相关成品不推送；参考下载、标注、相机、blend、渲染和QA也保持本地。当前灰模是空白牌板，没有真实牌号文字。

旧图里的车尾黑箱是已纠正的二维尾包排除遮罩，不是模型尾箱。当前纯灰模面板不绘制遮罩，原照和叠加面板保留带文字的隐私/遮挡区域。

## 重要命令

在项目根目录PowerShell运行：

```powershell
$blender = 'D:\Program Files\Steam\steamapps\common\Blender\blender.exe'
$python = 'C:\Users\22797\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

# 打开最新灰模
& $blender reconstruction_v2/blends/15_gray_review.blend

# 四角度低采样对照；不修改源文件
& $blender --background reconstruction_v2/blends/15_gray_review.blend --python reconstruction_v2/scripts/render_gray.py -- 62 63 64 69 r15
& $python reconstruction_v2/scripts/make_review_boards.py r15 62 63 64 69

# 实际几何、油箱及座尾接口检查
& $blender --background reconstruction_v2/blends/15_gray_review.blend --python reconstruction_v2/scripts/audit_gray.py
& $blender --background reconstruction_v2/blends/15_gray_review.blend --python reconstruction_v2/scripts/audit_tank_interface.py
& $blender --background reconstruction_v2/blends/15_gray_review.blend --python reconstruction_v2/scripts/audit_seat_interfaces.py

# 油箱局部原生渲染与分件颜色诊断；材料不保存回源
& $blender --background reconstruction_v2/blends/15_gray_review.blend --python reconstruction_v2/scripts/render_tank_review.py
& $blender --background reconstruction_v2/blends/15_gray_review.blend --python reconstruction_v2/scripts/render_tank_review.py -- --ids
& $blender --background reconstruction_v2/blends/15_gray_review.blend --python reconstruction_v2/scripts/render_tank_review.py -- --ids-full
# 对照需要本地照片、标注及已保留的r13基线渲染
& $python reconstruction_v2/scripts/review_tank_r15.py r15

# 显式同步控制数据到新源；拒绝覆盖和未经迁移的拓扑改变
& $blender --background reconstruction_v2/blends/15_gray_review.blend --python reconstruction_v2/scripts/apply_cages.py -- working_next.blend r16
```

Blender手改后先同步控制JSON或另存精修源，不能用旧JSON覆盖手改。两个隐藏座垫避让工具共享Seat_Rider.data，换数据块时须同步。旧迁移、拟合脚本只用于明确冻结输入，不是日常重建命令；当前油箱拓扑不能直接同步到r13而忽略检查。Python科学依赖位于`.tools/calibration/`，公开仓库不能替代本地照片和标定。

## 尺度与来源

`+X`右、`+Y`前、`+Z`上；场景米制，控制网格毫米乘0.001。

[豪爵官方GSX250R-A参数](https://en.haojue.com/NEWGSX250R/canshu.html)提供轴距1430mm、前后盘290/240mm等名义约束；[铃木L8型录](https://www.suzuki.hu/motor/files/document/document/294/GSX250R_ABS_L8_EN.pdf)提供车型家族的25.6°后倾角/104mm拖曳距，具体年份适配未确认。爆炸图不是精确尺寸图，隐藏尺寸未验收。[证据索引](reconstruction_v2/references/evidence.md) · [零件核对](reconstruction_v2/references/review.md)。

历史：[r14油箱候选](reconstruction_v2/reviews/r14_tank_crown.md) · [r13接口](reconstruction_v2/reviews/r13_tank_rear.md) · [r12镜头敏感性](reconstruction_v2/reviews/r12_camera_sensitivity.md) · [r6.2冻结记录](docs/legacy_r6_2.md)。
