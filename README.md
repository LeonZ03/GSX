# Suzuki GSX250R 实车重建

根据车主多角度实拍，在本机 Blender 中重建实车；使用 Blender MCP，保留可编辑源文件。目标是尽可能1:1复刻，当前仍处于灰模形体校正，未完成最终贴花、材质、4K渲染和三格式导出。排除尾包、网绳与骑手。

## 当前 r51：按新增多角度参考重做车头

唯一工作模型：`reconstruction_v2/model_history/GSX250R.blend`。通过本机 Blender 5.2.2 LTS / Blender MCP CLI 修改；没有使用 Computer Use，没有启用子智能体。

已查看 `references/3d/` 的全部10张下载图（7张大图、3张缩略图），重点使用两张线框、灰模、正面和俯视；与实拍72、69、63及驾驶位参考交叉核对。它们是商品预览，不是商业模型源，也不是精确尺寸图。实车改装件和配置仍以 `IMG/` 为准。参考图继续仅本地保存。

本轮连续修改和检查多个候选后，实际保存的改动：

- **车头外罩：**重建环绕灯组的四边面控制曲面，抬高风挡两侧肩部，调整前伸、侧回折和下部侧翼。保留侧包围接口，清理新接口的切削碎片。
- **灯具：**重做主灯轮廓、有限厚度透镜、纵横分区反射碗、灯泡座、遮光片和后壳；位置灯重新贴合连续黑色凹槽。几何交叠修复后再保存。
- **整车复核后的其他修改：**后视镜改为带圆角的折角壳体，保留各自朝向和原杆件并补内连接；前挡泥板补两道浅纵槽；补回双后转向灯、短柄和连接牌架的支座。
- 油箱、座垫、护杠、轮组、发动机等已逐项复看，本轮没有将商品车型配置直接覆盖到实车；它们的剩余形状差异详见[整车复核记录](reconstruction_v2/reviews/r51_system_review.md)。

18个作用域对象的开放边、非流形边、零面积面及未解释自交为0；8组重点邻接面交叉为0。前罩为1个连通实体，左右侧包围及驾驶位内板分别为2个完整侧件。621个受保护对象和相机的源签名不变。轮胎实际求值包络中心测得水平轴距约1430.00005 mm。以上是局部几何与比例检查，不是整车形似认证。

**B/C仍为NOT_PASSED，尚未达到实车1:1。** 主灯光学分区、前脸精确深度、油箱/座尾曲率、轮组铸造截面等仍需继续核对；没有通过98%轮廓IoU及两个独立角度验收。不进入最终贴花、4K与三格式导出。构造壁厚、槽深和隐藏支承尺寸均为估计。

本地模型提交：`220d8ef7d6e5865033ae05b7bd0a8826d1056a49`，已从commit回读并验证SHA256。r50仍可从 `c1cb9559c9a4103cb292ac17870af3eaf79544fc` 恢复。只维护一个工作blend。后台保存不会自动刷新已打开的Blender窗口，查看新版需重新载入该文件。

检查图：`reconstruction_v2/renders/r51_front_before_after.jpg`（r50/r51固定斜前、正面、侧面）和 `r51_system_review.jpg`（整车侧面、后方与驾驶位）。原始六视图位于 `renders/assembly_review/r51_*.png`。这些是模型检查视图，不是已标定的实拍叠加。

保存后还检查了新增安装连接；后转向灯透镜后缘补1.1 mm嵌入，并单独验证闭合和实际接触。这处隐藏接合修正发生在六视图出图之后，未重新渲染全部视图。

检查记录：`qa/r51_signal_finish.json`、`qa/r51_saved_readback.json`、`qa/r51_geometry.json`、`qa/r51_integration.json`、`qa/r51_history_verified.json`。重建入口 `integrate_r51.run()` 仅接受已提交r50；不要在r51重复执行。新前罩由隐藏可编辑 `Tool_R51NoseCage` 与现行上侧罩组成；保留邻面工具依赖，不要用旧前脸控制覆盖。当前控制来源见manifest，完整独立历史重放尚未认证。

## 素材检索与参考来源

同款收费模型的公开展示已有用户下载的本地参考；此前403和截图工具失败不代表现在仍缺这批图。没有取得付费源文件，没有完成全部360帧采集。免费模型检索与许可限制见[记录](reconstruction_v2/reviews/model_asset_search_2026-09-20.md)。

## 重要操作

使用本机可用Python。Blender保存当前工作文件后记录版本：

```powershell
python reconstruction_v2/scripts/model_history.py checkpoint "说明本次模型修改"
# 恢复前必须先提交尚未保存到Git的模型变更
python reconstruction_v2/scripts/model_history.py restore <本地模型提交号>
```

旧112个blend已归档到独立本地Git并逐个验证可恢复，原文件名映射见`reconstruction_v2/model_history/archive_manifest.json`。本地模型历史无remote，不随公共仓库push；不是异地备份。
建模迁移只从指定父提交执行，不能重复覆盖精修源。最新批次入口/限制见`reconstruction_v2/data/current_controls/manifest.json`，进展与执行约束见`AGENTS.md`。

## 坐标与参考

场景米；控制数据以毫米表达，换算0.001。+X右、+Y前、+Z上。轴距1430mm；前后轮胎110/80-17、140/70-17；制动盘290/240mm。明确构造尺寸与未知隐藏尺寸分开验收。

- 实车外观、附件与使用痕迹以本地`IMG/`为准；京B号牌配置仅本地使用。
- 豪爵车型参数：https://en.haojue.com/NEWGSX250R/canshu.html
- Suzuki零件目录：https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RAM1_GSX250RAZM1.pdf
- 爆炸图用于结构辨认，不能作为精确尺寸蓝图；不同年份/市场资料须排除差异。

真实照片、含照对照图、标注、相机、下载参考、模型、渲染和号牌相关成品均不推送公共仓库。
