# Suzuki GSX250R/A public references

检索日期：2026-09-18。用途：Blender 实车外形与比例参考；未接触或上传工作区 `IMG/` 原照片。

## 尺寸与规格

- [Suzuki Cycles 2024 GSX250R ABS](https://suzukicycles.com/sportbike/2024/gsx250r-abs)（Suzuki Motor USA 官方车型页）：overall length 2085 mm、width 740 mm、height 1110 mm、wheelbase 1430 mm、ground clearance 160 mm、seat height 790 mm；前胎 110/80-17M/C、后胎 140/70-17M/C；248 cc 液冷 SOHC 并列双缸、15 L 油箱；ABS 版整备质量 181 kg。与用户规格一致，作为比例基准。
- [Suzuki 日本车主手册下载页](https://www1.suzuki.co.jp/motor/support/owners_manual/dl/index.html?bikedisp=3&modelname=GSX250R)：官方列出 GSX250R 年式 2020/2023/2024/2026 手册入口（页面显示文件大小约 4.8–4.97 MB）；适合查仪表、灯具、操控件和拆装说明。
- [Suzuki Hungary GSX250R ABS L8 brochure PDF](https://www.suzuki.hu/motor/files/document/document/294/GSX250R_ABS_L8_EN.pdf)：官方/经销体系英文规格页，包含 248 cc、53.5×55.2 mm、15 L 油箱及车型照片；作为早期外形与尺寸交叉核对。

## 外形与零件分解图

- [Suzuki 日本官方零件目录页](https://www1.suzuki.co.jp/motor/support/parts_catalog/dl/index.html?bikedisp=3&modelname=GSX250R)：官方提供 2020/2021/2023/2024/2026 GSX250R 零件目录入口。
- [GSX250RM0_N00（2020）官方零件目录 PDF](https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RM0_N00.pdf)：搜索索引确认含 FIG.485C/485D 车身/整流罩爆炸图、FIG.530A/530B 前轮与制动盘爆炸图；适合作为整流罩层级、卡扣/紧固件、前轴/垫片和刹车盘相对位置参考。
- [GSX250RAM1_GSX250RAZM1 官方零件目录 PDF](https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RAM1_GSX250RAZM1.pdf)：官方索引确认 FIG.481B “COWLING BODY”，含左右整流罩、风挡、车架盖、Suzuki 标识、紧固件和支架编号；适合中国 GSX250R/A 外观覆盖件建模。
- [GSX250RL_XM5 官方零件目录 PDF](https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RL_XM5.pdf)：官方索引确认 FIG.541A 后车架/摆臂分解图，FIG.555A 发动机/变速箱侧分解图；可核对发动机安装、摆臂、链条区域和支架位置。
- [RevZilla 2025 GSX250R ABS FRAME OEM diagram](https://www.revzilla.com/oem/suzuki/2025-suzuki-gsx250r-abs/frame)：基于 Suzuki OEM 件号的车架图，显示 41100-20K10 FRAME、41942-48H00 前发动机安装支架及螺栓，适合核对主车架/发动机固定点。零件图版权归页面权利人，仅作建模参考。
- [OEMMotorParts 2023 GSX250R FRAME](https://www.oemmotorparts.com/en/model/suzuki/gsx250r-p01-m3/2023/drawing/frame)：列出 41100-20K10 主车架、41498-48H00 下管盖、41942-48H00 前发动机安装支架；用于安装关系交叉验证。

## 归档与下载状态

本目录仅建立 `references/public/`，但当前运行环境的文件下载执行器返回 `helper_unknown_error`，因此官方 PDF 未能落盘；以上链接均为公开原始 URL，访问时可直接下载。网页检索结果已记录官方尺寸与 PDF 内可见图号证据。未找到可公开且可信的完整官方维修手册下载；第三方“service manual”销售页未归档，避免版权风险。

## 建模提示（证据限定）

- 采用 1430/2085/740/1110/790 mm 作为整体包络约束；轮胎规格锁定轮胎外径与轮圈比例的基准。
- 官方零件目录爆炸图支持整流罩、风挡、车架盖、前后轮、摆臂、发动机与安装支架的分件关系；无法从爆炸图单独推断精确曲面尺寸，曲面仍需以实车照片/正侧后视图校准。
- 公开官方结果未提供完整独立的前/左/右/后正投影视图；本次归档不声称存在缺失角度的官方测量图。


## 2026-09-18 归档补充

主智能体已成功下载 `GSX250RM0_N00_parts.pdf`（108 页，约 4.9 MB），并渲染了其中发动机、排气、车架、整流罩与前后轮相关页到 `references/public/parts_*.png`。上述最初“下载器失败”记录已经由本节更新。

- 实际查看的零件图页：13 缸头、27 排气、76 前整流罩、95 前轮；相邻相关页一并归档。第 95 页与官方型录说明支持十辐条轮毂；第 27 页确认双头段汇入排气总成、独立消音器及隔热罩。
- [Suzuki 官方 GSX250R 360°](https://www.globalsuzuki.com/motorcycle/smgs/products/2021gsx250r/360viewer/)：网页、公开 JSON 资源索引和八个转台帧已保存；原始帧为该页 `img/main/g01_c01_{1,5,10,14,19,23,28,32}.jpg`。它们用于原厂形体参考，未把其版画或轮贴覆盖到车主版。
- L8 英文型录在线 PDF 可以读取，包含 8 页、10 辐轮毂、248 cc / 18.4 kW / 23.4 Nm、181 kg ABS 规格；当前本地下载副本交叉引用损坏，未将损坏副本当成有效归档验证结果。可靠规格由在线官方 PDF 与已验证零件目录交叉核对。
- 搜索了 `GSX250R 护杠 三点安装 黑色 管 防摔杠`、`GSX250R 手机支架 方向阻尼器 安装`、`Suzuki GSX250R top view underside engine exhaust header`。发现的通用滑块和手机横杆并非照片中的同一件，不据此替换实车附件。
- [R&G CP0435 产品页](https://www.rg-racing.com/browsebike/Suzuki/V-Strom_250/2018/CP0435/?v=atv)访问返回 403，未绕过限制；[Sato GSX250R 滑块](https://www.satoracingstore.com/store/p/sliders-s-gsx250fs-bk)仅作不同加装类型的线索，不是管式护杠尺寸依据。
- 未找到可靠的标定顶/底蓝图或车主护杠的精确工程图。隐藏安装点与管径在 README 中标为近似，没有伪称从网络得到测量值。

公开素材版权归相应权利人，仅在本地用于观察。最终外观文字为自制几何，未将下载照片直接用作车体贴图；唯一照片纹理用于第一阶段本地参考对齐检查图。

最终归档状态：通过 HTTP 断点续传补齐了 L8 型录，`GSX250R_ABS_L8_brochure.pdf` 已由 pypdf 验证为 **8 页完整 PDF**；第 5–8 页另存为 PNG。先前下载不完整的说明现已解决。最终本地有两份经过页数验证的官方 PDF，不再把损坏下载视为有效文件。

## r36 后部外露结构补证

- 继续使用[铃木 GSX250RAM1 / GSX250RAZM1 官方目录](https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RAM1_GSX250RAZM1.pdf)。PDF 零基页100的 FIG.541A 显示一体式链条罩/前段轮胎挡泥瓦，件号 `63110-20K00`；零基页56的 FIG.415A 显示不同的左右后座脚踏支架 `43811-20K00` / `43821-20K00`，右侧包含排气吊耳。零基页53的 FIG.401A 用于核对副车架和安装耳的结构关系。
- 本地截图在 `reconstruction_v2/references/raw/parts_detail_{53,56,100}.png`，不进入Git。用户69/70仅本地核对可见轮廓与折叠脚踏状态；目录不给出隐藏深度或精准安装尺寸。
- 检索另出现印度产 GSX250RLM0 P31 目录，平台适配未证实，本轮未采用其零件数据，避免将相近车型名称直接混用。


### r36 后部核对补充
- Suzuki官方转台：https://www.globalsuzuki.com/motorcycle/smgs/products/2021gsx250r/360viewer/ ，已查看5/10/14/19帧；仅作原厂结构参考，不替换实车配色或当独立实车视角。
- 既有官方GSX250RAM1目录FIG339A（后灯35710-20K01）/FIG474A（后挡泥63113-20K10、支座63131-20K00）；页图和脚本只存本地references。爆炸图不作精确尺寸。
