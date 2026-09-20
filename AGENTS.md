# 当前r45执行状态（优先于以下历史记录）

## 当前 r45：十五项反馈的结构重建批次，形似验收仍未通过

唯一工作模型：`reconstruction_v2/model_history/GSX250R.blend`。本轮使用本机 Blender 5.2.2 LTS 的 MCP，连续完成结构重建、整合纠错和检查；没有使用 computer use。

| 反馈 | 本批实际改动及限制 |
|---|---|
| 1 前脸 | 重做盾形主灯边界、厚壳、反射碗、灯座和上缘密封，并修改相邻面罩。整体曲率和位置灯衔接仍待实拍精度验收。 |
| 2 厚度、悬空 | 给反射碗加壁厚、封闭管件端口；补转向头、车架加强片、仪表支架根部与包围固定片。1056个可见几何对象的开放边/非流形/零面积面检查为0；这不证明所有装配均已正确。 |
| 3 边撑 | 保留已认可的支点/落地点，改为渐细杆身、折弯脚端、叉形转轴、脚板及带挂钩的弹簧。形似仍待验收。 |
| 4 多余外露管梁 | 上车架内收、尾部上梁重新布线；撤掉本批检查发现的过长支撑，换为20.2mm短安装片。隐藏梁线并无实测依据，不宣称全部准确。 |
| 5 中控台 | 增加仪表外沿罩、两侧内衬、内托盘、仪表固定架、转向头和线束连接；仪表文字仍留待后续。 |
| 6 手机支架 | 用统一坐标重建八边托板、四组滑臂/夹爪/胶垫、球头、锁轮和手把夹座；检查夹爪至手把夹座的连接链，原悬空夹爪已撤换。外形细节仍需精校。 |
| 7 护杠 | 按新72实拍补下回折、三组轴向滑块、上下支座及后安装螺栓；两边严格镜像。深度、管径及实物节点尚未量化通过。 |
| 8 牌照架 | 双细杆改为带折边的宽支架、横梁、螺栓和牌照灯连接片；仍保留空白牌板，真实京B仅本地私有配置。 |
| 9 马鞍座垫 | 骑手座回到纵向凹弧、前后抬升，撤销r42过强的横向鼓包。保持后座鼓度；没有宣称其横截面已实测。 |
| 10 右后脚踏 | 按用户认可的左侧折起结构镜像到右侧，包括防滑条和转轴；右侧排气吊耳保留。 |
| 11 底部进排气 | 网上核对并实际查看铃木M1目录，双头段接扁平汇流腔、连接管及原右侧消音器；补双进气接管/节气门、通气管和氧传感器。已纠正头段穿曲轴箱；隐藏管路走向/内部催化器仍未知。 |
| 12 风挡 | 重建连续弧面，去掉横截面的反复起伏，保留3mm构造壳厚；未将构造值当成实测。 |
| 13 转向灯 | 球形占位改为长圆胶囊灯壳/透镜、胶杆和安装螺母；后灯也调整轮廓。 |
| 14 油箱 | 从本地r39提交提取80点原始形体，在其肩部和膝部做减材式控制点削切，并恢复r39油箱盖姿态；未继续放大r42形体。 |
| 15 牛角间距 | 保留铰点，重建向前展开的扁拉杆，提高与握把的间距，并保留端部球头。 |

**这些是已实施的改动，不等于十五项已达到实物1:1。B/C仍为NOT_PASSED。** 前脸曲面、附件精确形状、隐藏安装尺寸、完整轮廓/关键点指标和两个独立视角仍未通过，不启动最终贴花、4K或成品导出。

检查报告：`qa/owner_fifteen_assembly.json`。11个重点形体所查自交候选为0；骑手座与油箱/侧板/后座底托、双头段与曲轴箱等所查非配合表面无交叉。手机支架、护杠安装链、仪表支承链、排气连接链另做表面连接检查；安装配合处允许有意嵌入，未模拟螺纹或全转向行程。不要把这组有限检查写成“全车无悬空、全车无穿插”。

当前模型本地提交：`8b46d0c7b0d352dd95e4442b7dcdda7fdcb0955e`，已从提交回读验证SHA256相同；本地模型仓库无remote。公开提交只含代码、文档和派生三维控制，原照、相机、标注、含照对照、模型和渲染均留在本地。

检查图：`renders/owner_fifteen_review.jpg`（四角度结构检查）、`renders/owner_fifteen_photo69.jpg`（固定照片69对照，历史实车无现款护杠）、`renders/assembly_review/r45_*.png`。69对照和早期Cycles正面图生成于最后隐藏安装支座补齐前，不能当作最后安装节点的证据；最终四角度图使用更新后的工作文件。

当前控制：`data/current_controls/assembly_r45.json`记录163组分件控制，主曲面另存网格JSON。`r39_shape_basis.json`是从r39本地提交提取的几何/油箱盖基准；不能用旧canonical覆盖。迁移顺序与限制见manifest；本批没有完成独立全链重放，当前blend为权威源。

下批优先：新72视角的前脸/灯组轮廓对应、62/63/72护杠三组节点交叉复核、65驾驶位/油箱削切复核，再处理牌架和后座外形。各项形似仍待验收，不以版本号、零件数或封闭性替代进度。

本轮仅1个资料复核子任务，请求配置为gpt-5.6-luna/medium；工具未返回实际配置。首轮误用的LM0平台资料已被主线程否决并改成M1核对，不作为模型依据。

---

## 当前 r42：九项反馈已逐项改模，实车精度验收仍未通过

唯一工作模型：`reconstruction_v2/model_history/GSX250R.blend`。本轮通过本机 Blender MCP CLI 建模，没有使用 computer use，没有启用子智能体。

| 用户反馈 | 本轮实际修改 |
|---|---|
| 1. 双侧护杠 | 两侧均显示，主护杠中心线镜像误差 0 mm；取消历史视角隐藏规则。 |
| 2. 护杠形状 | 按62/63可见管件节点重建空间折弯、内撑、后连接片和滑块，不再仅用三角环代替。 |
| 3. 边撑位置 | 按69支点/落地点重定位、缩短杆身，重做脚板、转轴、拨脚和弹簧。 |
| 4. 前挡泥板 | 重建冠部、前叉两侧翼和向前下方收尖的前缘。 |
| 5. 前脸、座垫过平 | 修改车头折面、主灯轮廓及翼形位置灯；两座垫增加横向弧面。 |
| 6. 座垫形状 | 后座前端圆角、鼓度、可见接缝和贴形底托；修理座垫与油箱/尾罩接口。 |
| 7. 手把 | 结合65俯视重做分体夹座、上联板孔位、握把/端头、扁拉杆、左右开关与右制动总泵；调整手机夹具外形；补齐转向时手把/夹座/夹具/相应构造工具的随动关系。 |
| 8. 油箱 | 调整肩部折线、侧面转折、膝部凹面，重新贴合油箱盖总成。 |
| 9. 后轮挡泥板 | 维持移除轮拱，保留链条罩、尾灯和牌照支架。 |

**以上表示对应修改已实施，不表示九项已达到实物1:1。** 62/63/69仍为参与调整的相机；65俯视和66正面是结构参考，不是已标定验收镜头。隐藏安装深度、护杠管径、座垫横截面、前脸/油箱曲面精度仍未实测或通过完整照片指标。B/C继续NOT_PASSED，不做最终材质、4K或成品导出。

局部检查：`qa/owner_geometry_review.json` 中本轮所查部件无非流形边、零面积面和未解释自交候选；八组重点表面相交计数均为0。这是有限范围几何检查，不代表整车装配/外形通过。新前挡泥板和管件保留可编辑控制形体，使用实时体积焊接处理局部薄壳/管件交叠。1.5 mm座垫接口间隙及0.7/1.2/1.5 mm表面采样均为建模设置，非实测公差。

本地模型提交：`48d21ca2c50fdcce6b95cfbedd724d604b1c5484`。已从提交回读验证SHA256一致，无远程地址，照片/模型/号牌不推送。公开仓库仅提交脚本、文档和派生三维控制数据。变更控制在`data/current_controls/`；其中位置灯边框是显式顶点/面，不是grid格式。其余历史控制不能覆盖当前源文件。

检查图位于`renders/owner_nine_issues_comparison.jpg`、`renders/gray_r42_63.png`、`renders/gray_r42_69.png`以及`renders/stage_bc/r42_CockpitTop.png`、`r42_FrontSymmetry.png`、`r42_SeatProfileGeometry.png`。含实拍对照仅本地。历史69没有现款护杠，显示差异已注明。

后续按这些对照继续形似复核，优先核对护杠各连接节点、前挡泥板侧翼、两座垫轮廓，以及俯视油箱/驾驶位。不能以这次修改数量或局部检查为九项精度验收盖章。

---

## 当前 r39（覆盖历史状态）

唯一工作模型：`reconstruction_v2/model_history/GSX250R.blend`。B/C仍未通过。
已取消69视角隐藏护杠规则；左右护杠中心线镜像误差0mm，但造型仍未通过。移除后轮轮拱，保留链条罩和尾部牌照灯架。
用户要求重新纠正：护杠形状、边撑位置、前挡泥板、前脸、前后座垫过平/形状、手把（参考65俯视）和油箱肩部/凹面。以上均未完成，不以旧局部网格检查代替形似验收。
下一批按①护杠/边撑/前挡泥板，②两座垫/油箱，③俯视驾驶位/前脸推进，各批交固定相机改前改后；相机和排除区不改。不进入最终材质/4K。

### 单工作模型与本地历史

112个旧blend已逐个提交到无remote的独立本地Git仓库，并从commit回读验证SHA256一致后清理重复文件。旧文件名到提交号的映射保存在本地`model_history/archive_manifest.json`。旧文档中的blend路径需通过此映射恢复。
当前本地模型commit：`987998d5b46590f2c9e65be60f48c9c1b041d0b6`。原r38也已归档。

```powershell
python reconstruction_v2/scripts/model_history.py checkpoint "本轮模型修改说明"
python reconstruction_v2/scripts/model_history.py restore <本地模型提交号>
```

先保存模型并checkpoint，再恢复旧版本。后续只保存这个工作blend，不再输出编号文件；修改前先检查当前工作文件已提交。model_history已被公共仓库忽略，照片/号牌/模型不推送；本地模型历史不随公共push备份。
历史r36重建脚本会加入轮拱，只用于复现历史；重放到r38后须应用apply_owner_corrections，不能当当前最终装配入口。迁移命令migrate不能重复运行，避免覆盖新工作模型。
本轮通过本机Blender MCP CLI保存与渲染，无computer use，无子智能体。预览`renders/gray_r39_69.png`，检查`qa/owner_corrections_r39.json`（均在reconstruction_v2内）。

---

# GSX250R 实车重建 — AI 工作记录

## 当前状态 r38（覆盖全部历史状态）
- 最新源reconstruction_v2/blends/38_gray_review.blend，988对象；B/C仍NOT_PASSED。用户要求持续推进直到B/C完成，未满足，不能宣称1:1或完成。
- r37补后挡泥/后灯/后转向灯/牌照灯及空白牌架；座尾支撑入壳、端点连接封口、2mm构造避让；修复r36已有62对尾尖自交。隐藏车架路径/厚度、挡泥截面仍近似。
- r38五螺栓油箱盖、锁盖/铰接及安装凹口，按求值油箱表面倾斜。直径114mm及XY沿用，非实测。4对原始三角接触用双半空间证明为边界接触，0.1微米浮点容差，保留原始计数；不推广成全车通过。
- 关键记录reviews/r38_tail_and_cap.md；qa/tail_assembly_r37_mesh_clearance.json、fuel_cap_geometry_r38_review.json、replay_r38.json；最新三视角renders/stage_bc_r38_comparison.jpg及驾驶位stage_bc/r38_Cockpit.png。
- 独立重放从36经replay_r38.run(唯一前缀)，拒绝覆盖；988对象控制几何/变换/相机/曲线手柄/所查修改器与可见性一致，不是全材质/求值网格证明。
- Body_Tail控制指向data/revisions/r37_tail_assembly/Body_Tail.json；其他网格仍r35快照。保留Tool_TaillightAperture、Tool_TailFrameClearance、Tool_FuelCapRecess/Bore/Hex依赖。布尔操作数须Mesh，不能使用Curve假装切削生效。
- 38最终父源37_tail_assembly_mesh_clearance→37_gray_review→38_fuel_cap_welded→38_gray_review。早期r37失败候选不能误用。
- 本轮无新子智能体，全部由主线程实际看图与MCP复核。58/59重看仍欠约束，无新正式相机；62/63/69不变。像素标注/相机/照片/含照板/源/渲染仍本地。主要曲面、闭合mask/正式关键点和两独立视角未通过，D/E不启动。


## 当前状态 r36（覆盖历史状态）

尾部下一候选尚未建模：63/69四点对应中三点触及宽度下界，两点残差8–10px，已拒绝；转向灯中心约0.5px仅是局部诊断。r36实际缺后灯/后挡泥总成，下一项先修正对应关系。

最新源 `reconstruction_v2/blends/36_gray_review.blend`，947对象。后部链条罩/轮拱、左右三角后座脚踏架及右排气吊耳已重建并完成局部网格/间隙检查。固定62/63/69镜头渲染和左右对照已查看。**B/C仍未通过，持续推进，D/E不启动。** 详细记录见 `reconstruction_v2/reviews/r36_rear_hardware.md`。

主体控制仍用r35快照，r36附件控制在`data/revisions/r36_rear_hardware/control.json`；不要用旧canonical覆盖。支架隐藏焊接/厚度、脚踏姿态、整车曲面、完整分件遮罩、两独立角度仍未验收。新件局部检查不代表整车精度。下一项核对后部挡泥/牌照安装及胎肩证据。


## 需求与最高优先级
- 用户批准 V2 重建计划：先资料纠错、照片匹配、准确灰模。灰模未通过，不进入新版完整贴花、最终材质、4K成片或导出。
- 目标实车1:1；当前未达标，不用面数、分辨率、文件完整或名义尺寸代替外形验收。隐藏尺寸不能盖章100%。
- 本机 Blender 5.2.2 LTS（r11实际复核），必须使用 Blender MCP。+X右、+Y前、+Z上；场景米、控制网格mm乘0.001。
- 以 IMG/ 实车照片为准：蓝白版画、荧光轮圈贴、左右三角管护杠、左把手机夹、方向阻尼器、指定京B。排除尾包、网绳、骑手、手套。只还原可辨认磨损。
- 不要求用户补照片、测量或选择配色；缺角主动搜原厂证据，不能臆造文字/贴纸。新版未制作错误日文标记。

## 隐私与授权
- 用户最新明确授权“真实照片不要推送，别的可以推送”。可以推送代码、文档、派生控制网格，不需再次确认。
- 原照、含原照对照图、标注、镜头、参考下载、blend、渲染、真实牌号配置和相关成品均保持本地。IMG/等路径已被.gitignore排除。
- 真实牌号只使用config/*.local.json，不输出日志或文档。57/59指定京B；60及新增图片的旧牌不替换它。M1只有空白牌板、无文字对象。
- 本地预览先遮蔽车牌及固定排除区，不推送照片。不可把允许推代码理解为允许发布真实号牌成品。
- origin使用ssh.github.com:443/LeonZ03/GSX.git；仓库为公开。命令级safe.directory，不改全局Git，不强推。
- r15代码、文档与派生控制网格已推送（模型改动提交d13cfe1）；后续仍需核对范围，仅显式暂存代码/文档/控制数据。

## 历史执行 r35
- 用户最新要求持续推进直到B/C完成；旧r27“收尾停止扩展”已失效。当前B/C仍NOT_PASSED，不能称本任务完成或1:1。D/E不启动。
- 当前源blends/35_gray_review.blend，908对象，23控制快照（21有效+2 superseded）。本机5.2.2LTS、Blender MCP后台，无Computer Use。r26及全部候选保留。
- 同一批次r28–r35：共享前罩肩部/侧回折、散热器间隙、灯罩碗形/开口灯框/位置灯、异形消音器/包裹隔热罩/空心出口、左右不规则发动机铸件与小检修盖。正式相机和本轮之外主要机械未改。
- 本轮19件求值QA非流形/退化/非共享顶点自交全0；指定8组非配合表面交叉0。右盖/曲轴箱38对装配接触未作全配合认证。隐藏控制片可接触，最终联合实体另检，不能扩大为全车通过。
- r31排气及r33 Boolean切缝失败候选未采用。正确父链28_front_connected→30_engine_exhaust_fixed→31_front_lamp_exhaust_fixed→32_front_frame_candidate→33_front_seam_review→34_engine_review→35_gray_review。33_gray_review.blend不是最终可用r33，不要误选。
- 前罩内衬接缝最终靠NoseSideReturn首排+Y4.5mm构造间隙，不含失败切缝Boolean。共享Body_UpperSideCowl加入实时GN，旧UpperCowling/CowlingSide隐藏且superseded，不恢复导出。
- r35 data/revisions/r35_controls/manifest.json为当前23组源几何快照，含显式faces；每对象control_cage_source指向此目录。canonical control_cages仍旧r26输入，不能默认apply_cages覆盖r35。发动机两份参数控制在r30_engine_candidate/r34_engine_candidate。
- Tool_TransmissionCaseSupport保留曲轴箱联合依赖；Tool_AlternatorHexSocket为浅孔工具；Tool_SprocketCoverClearance共享新左盖mesh，替换时同步。均隐藏/export_exclude，不删。
- 从r26运行replay_r35.py实际重放成功；908对象签名、所查modifier属性、visibility和照片camera一致，qa/replay_r35.json。不是全部材质/GN/求值网格完全等价认证。
- 最终renders/stage_bc_r35_comparison.jpg及review_r35四角度；qa/assembly_r35.json、geometry_r35.json。本批详细reviews/r35_stage_bc.md。所有照片、含照板、像素标注、镜头、QA、源、渲染仍本地，公开仅代码/文档/3D控制。
- 右盖只建5个可辨螺栓，目录家族13孔其余未定位；左盖4个可辨位置，单69拟合、X深度假设未独立验证。剩余车头/油箱/座尾外形、整车闭合mask、两有效独立角度、灯具内部与附件安装仍未通过。下一轮不得以新增小零件代替这些主要验收缺口。
- 原厂转台诊断calibrate_oem_turntable输出本地，中位1.79/P955.69px，未接受；不要作为用户实车独立角度。62/63/69已用于调整，64欠约束；70与59/60旧失败诊断仍不能直接转正。
- 本轮1子任务exhaust_rebuild请求gpt-5.6-luna/medium，实际配置未回传；独立排气QA由主线程复核。子任务后续看图失败不提供视觉结论，主线程已实际看原照/渲染。

## 历史收尾 r27 候选
- 用户本轮最终要求收尾汇报，已停止扩展；B/C仍NOT_PASSED。r26仍为工作基线，最新待验收源blends/27_front_review_candidate.blend，不得宣传通过或1:1。
- 4组候选Body_SideFairing/Body_UpperCowling/Body_CowlingSide/Cockpit_InnerPanel在data/revisions/r27_front_candidate，canonical control_cages未更新。旧3D控制归档data/archive/r26_front。严禁默认apply_cages用r26覆盖r27候选。
- 修正外侧蓝色尖角与内侧灯旁点混淆；前上沿实际求值开放边界62/63/69局部误差改善，约±5px标注不确定，均为拟合角度，不是98%轮廓/关键点/独立验证。
- 前罩侧回折面试改产生更多重叠已回退；最终候选从真实r26继承Body_NoseSideReturn。早期从JSON恢复该面有面连接顺序/方向差异，已弃用该恢复方式；最终候选直接继承r26原面，最终四角度和QA均重新从27_front_review_candidate生成。
- 侧面折返13自交接触候选；侧罩/散热器202、鼻罩总成/上罩1945、上罩/折返209三角重叠候选仍未判通过。侧罩和内衬等局部非流形/退化为0不能代替装配。926对象，照片相机与机械未改。
- renders/stage_bc_r27_comparison.jpg、review_r27四角度及contact_sheet；本地qa/front_r27的geometry/upper_rail_metrics/replay_final。最终从r26独立重放926对象的源几何/变换/相机签名一致，非材质/修改器等价认证。公开记录reviews/r27_front_candidate.md。
- C本轮只证据复核，未新建发动机/排气；下一轮先重建前罩组连续边界及厚度，再排气异形截面/包裹隔热罩和发动机外壳。预算仍不可靠，不默许无限迭代或降门槛。
- front_evidence与mechanical_evidence请求gpt-5.6-luna/medium，实际配置工具未确认；机械子任务本地读图失败，主线程复核了实际排气裁图，不采用未看的照片推测。所有照片、像素标注、镜头、源和渲染保持本地。

## 历史状态 V2 / r26
- 最新blends/26_gray_review.blend，926对象/22quad控制网格；B/C仍NOT_PASSED，D/E不启动。实际本机5.2.2LTS、MCP后台，无Computer Use。
- 同一连续批次r20→r26；r25镜壳/风挡/侧盖/链轮罩/减震保留。r26根据62/63右侧安装点和69左侧轮廓重建不同Rearset_L/R，贯穿孔、折叠脚踏、橡胶/横纹、左换挡连杆、右后刹踏板/可见主缸。隐藏厚度、横向深度、运动行程未验收。
- 旧脚踏确有r03随发动机+Y140/-Z50偏移；本次按可见安装点重新建，不只机械撤销旧位移。正式相机、车架/摇臂未改。新的扁条GuardMount_Rear左右镜像，主护杠中心线不变；data/guard_control.json已同步后连接端点，旧值data/archive/r20保留。
- r26新增组65件局部质量/所查相邻表面相交0；连同前批共99件非流形/退化/自交候选0。qa/increment_r26相对r20有35旧对象按范围改变/移除、91新增，无非预期旧变化；22cage同步最大0.00014mm。不是整车装配认证。
- qa/rearset_r26/actual_mount_projection来自实际求值螺栓：62上/下0.47/0.25px，63为2.34/5.53；仅2个参与拟合点、标注约±4px，不是全局关键点/独立验收。
- 实际replay_r26.py从r20完整重放，926对象几何/变换/相机签名与最终源一致，qa/replay_r26.json。新脚踏构建只允许独立r25，冻结数据data/revisions/r26；不要对精修源重放。Boolean依赖Tool_Rearset_*隐藏/export_exclude，不可删。
- 对照renders/rearset_r26_comparison.jpg、stage_bc_r26_comparison.jpg及四角度review_r26；报告reviews/r26_stage_bc.md。原r25及所有失败候选保留。70只诊断候选，仍无2可靠独立角度。
- 下一主项回到车头—侧罩整个组的边界/接缝与控制网格，不再扩展装饰；C处理发动机铸件和排气。B/C均未通过，没有可信完工轮数，不以修订号作为进度百分比。
- 实际1新建子任务请求luna/medium、2复用子任务配置未回传；结构子任务再次只读目录核对。主线程最终建模、集成、全部验收。只推送代码/文档/派生控制，原照/含照板/镜头/QA/源/渲染/真实牌号仍本地。

## 历史增量 V2 / r25

- 最新blends/25_gray_review.blend，879对象、22quad控制网格；B/C仍NOT_PASSED，D/E不启动。全程Blender MCP后台，不用Computer Use。
- 本批次r21–r25：风挡保留下2排后拟合上缘；镜壳扁片改闭合圆润壳/镜片/镜杆；替换Body_MidSideCover左右黑侧盖、Engine_SprocketCover；重建短弹簧/筒体/安装眼/贯轴/垫圈/双耳/紧凑上下横梁。所有隐藏深度、弹簧圈数线径及支座尺寸未验收。
- 侧盖控制从两侧照片诊断约置于X±113mm、车架内侧，原车架未改。初稿尖端加厚自交370对已修复；最终侧盖对Frame_Main/Body_SeatSide无所查表面穿插。不要恢复失败r23尖端。
- Tool_SprocketCoverClearance共享Engine_AlternatorCover.data并保留其修改器，额外法线外推1mm供盖板差集；隐藏/export_exclude。盖板Boolean后3微米Weld，镜杆端盖后1微米Weld，不能漏掉或删除工具。
- qa/increment_r25检查34本批次部件：非流形/退化/所查自交全0；局部非配合件表面相交0，上下横梁对frame/swingarm的配合相交有意保留。不是全车装配认证。22cage同步最大约0.00014mm。
- 原r20的9对象有意改变，其他原对象几何/变换/相机签名无非预期变化；新增26。所有正式相机未改。实际从r20重放r25后879对象签名一致，qa/replay_r25.json；不扩展成材质/所有modifier比较。
- data/revisions/r24和r25是公开冻结派生控制；replay_r25.py从r20运行并拒绝已存在输出。rebuild_* / add_missing / repair_*为明确迁移，不对精修源随意重放。apply_cages仅在最新兼容拓扑源同步。
- 70原失败镜头不覆盖。主线程复核真实黄圈采样后新qa/camera70_r21候选RMS0.62px/P951.16px，留每四点测试RMS0.60px；半径±5mm对应镜头明显变化，仅诊断，不是毫米认证/严格新holdout。render_candidate_camera.py单独渲染且不改正式相机。
- 子任务59/60错误ROI/双加像素偏移、风挡错位标注均作废，禁止使用其旧残差。失败代码/资料仅qa。60实图前轮圈不可清晰辨认，59前轮短弧需另核。不要再称子任务标注已通过。
- 风挡root开放线62/63/69都参与拟合，约±5px；62中位22.7→11.7，63 6.4→6.0，69 6.6→4.7。不是完整IoU/关键点/独立角度，63变化小于标注误差。
- 脚踏r03曾整体+Y140/-Z50，位置明显可疑但清晰铰点未建立，本批次未盲目平移；下一步重建左右脚踏架与操纵连接，并处理车头—侧罩整体曲率。完整分件mask/两独立视角/隐藏尺寸仍未验收。
- 本轮1新建请求luna/medium，复用2旧子任务配置未确认；主线程负责全部结果复核并重写失败产物。详细reviews/r25_stage_bc.md。照片/车牌/含照板/源/渲染/标定QA仅本地；只显式暂存安全代码/文档/派生控制。

- 最终对象清单纠错：旧Body_MidSideCover一直存在，r24新FrameSidePanel是重建候选，不能两层叠放或声称原件缺失。r25移除旧件并将新件命名Body_MidSideCover，控制总数仍22。后续判缺件前必须同时查场景、控制网格和组件索引。

## 历史批次 V2 / r20
- 最新20_gray_review.blend，853对象/22quad控制网格。r15–r20为同一连续B/C批次多个候选，不是完成多个阶段；B/C仍NOT_PASSED。全程Blender MCP后台，无Computer Use。
- 保留r19车头/驾驶位/轮组/侧盖改进，r20侧罩56→70控制点、支持截面收尖。62/63/69实际求值最低点投影诊断26.7/34.9/23.1→6.8/4.5/8.4px，标注约±8px；三图已用于调整，非独立验证或完整关键点验收。复杂加厚消除初次8个内壳自交；canonical及重放方式已同步。
- r19旧SideFairing控制快照在data/archive/r19；refine_fairing_stage_b只读明确快照，不能改用当前70点JSON作旧输入。原候选/失败加厚源均保留。
- 官方目录FIG206A/550B：14/46齿、116节DID520；DID官方520节距15.875/内宽6.35。新drive_layout由每相邻销轴精确节距求解：理想张紧中心距677.768mm、输出Y约−39.557，替换旧Y−225。Z370/X−101仍旧假设，链条松弛/实车改齿比/深度/动力学未验收。不得称实测精度。
- Chain现在是空物体父级，232块交替内外板+116滚子+116销轴为关联mesh；新14/46齿链轮、后毂连接、输出轴和曲轴箱局部Boolean避让。Tool_OutputSprocketClearance及Tool_OutputChainExit隐藏/export_exclude，不能删除依赖。
- ABS改50槽/3固定件，前后盘支臂及螺栓各5，后链轮固定件5，依据FIG530D/550B。ABS实体欧拉数−100；原BVH20/14对逐几何检查是端面顶点碰孔壁边界，非内部穿越。原计数保留，不抹成未检查的0。
- 真正销轴位置测得节距误差最大0.000067mm；22组控制网格源/JSON差<0.0001mm、面连接一致；空白牌板/无FONT。旧385保护对象数仅r19成立，r20保留72个旧对象/313个旧传动对象有意替换单列，不能宣称全部原结构未变。
- 源及图以20文件为准；renders/stage_bc_r20_comparison.jpg、review_r20_*.jpg及stage_bc局部；qa/drive_r20、abs_contacts_r20、source_sync_r20、stage_bc_r20、geometry_r20和stage_b_tip_r20。详细reviews/r20_stage_bc.md。照片/标注/含照对照/源/QA及真实牌照仅本地。
- 61错误ROI作废及真正后轮短弧欠约束结论不变；59/60未可靠标定。缺完整部件mask及两独立角度，主要曲率和座尾/安装仍有明显偏差；不能进入D/E。
- 下一批优先独立标定/可见边界与车头油箱座尾跨图误差；C优先前链轮外罩、脚踏、护杠支座和悬挂上下连接。不能新增更多装饰来替代这一组问题。
- 两子任务请求gpt-5.6-luna/medium，实际未回传；主线程否决错误初稿并完成集成验收。Git只明确暂存代码/文档/派生控制，发布范围已核对；实际提交和推送结果以Git记录为准。

## 历史批次 V2 / r19
- 最新用户授权全速推进B/C，可以并行制作；实际B/C均NOT_PASSED，不进入D/E。不得说已完成1:1。
- 最新源 reconstruction_v2/blends/19_gray_review.blend，681对象、22个quad控制网格；r15及r16–r19候选均保留。全部Blender MCP后台，未使用Computer Use。
- 新NoseCheek/NoseSideReturn/WindscreenSeat控制面，修Cockpit_InnerPanel前缘及SideFairing/TankSideTrim/SeatSide内部断面；油箱、座垫主体和原相机未改。canonical JSON已同步7项；旧FairingBlade索引清理，失败NoseCrown窄带只留历史。
- Body_NoseAssembly经Geometry Nodes实时读取三组隐藏控制面，1mm体素合并、Smooth/Decimate/Weld/删除孤立点生成可见实体。控制面hide_render/export_exclude，不能单独导出；源内壳接触/自交不代表最终实体，最终实体另验收。不能把体素大小称实车精度。
- 驾驶位：双肩仪表壳/空白LCD/按键，四爪手机夹/球头/夹座，阻尼器筒体/细轴/安装耳，叉盖/钥匙座、灯碗。没有猜测仪表文字。
- 机械增量：五段八边截面弯曲轮辐、真实盘孔/承载臂/分体卡钳/ABS槽圈、闭合侧盖/螺栓台阶/折面隔热罩；修旧发动机位移后的悬空螺栓与排气入口。原胎纹/车架/链节/摇臂/减震/脚踏/侧撑/护杠保留。新增前轮从属steer_with_front=True，render_gray已支持。
- 子任务初始机械方案有删除未重建、单面轮辐、圆管消声器/隔热罩、空心侧盖等退步，主线程否决后重写，不得重放失败版。
- QA：385受保护对象与照片相机内外参未变；名义轴距/盘径/胎宽保持。最终前罩78301点，非流形/孤立/退化/所查自交均0；20轮辐、侧盖、隔热罩同项0。盘原BVH前2/后3对经几何判别是端面顶点碰孔壁边界，非三角内部穿越；raw计数保留，不能只抹成0。
- 骑手座对Tank/Tail/SeatSide/PillionBase所查表面相交0。全车穿插、机械轮廓和安装深度未通过。
- 61初始子任务ROI错误：两段都来自同一前轮，原RMS6.24等统计完全作废。主线程实际看轮组纠正后：前56点、后8点约40°，候选RMS2.76/median0.66/P951.98、转角38.8°；后轮遮挡导致欠约束，未改正式标定，车身未参与求解，不可评分。
- 实际看图分类：57近后视、58骑手近前视、59/60右后斜视、65驾驶位；59/60未可靠标定。不能说已证明不存在独立角度，也不能说已有两个有效holdout。62/63/69拟合、64欠约束、66结构已用、70失败。
- 新rebuild_body_stage_b/refine_nose_stage_b/rebuild_cockpit_stage_c/rebuild_mechanics_stage_c/assemble_front_cowl/finalize_stage_bc为明确基线迁移，不是日常重放。apply_cages在最新源运行，保持隐藏控制和GN依赖；新建场景只读JSON不够，还须建实时装配。
- render_gray/render_stage_bc只在一次性渲染进程缓存求值实体，不保存缓存源。MCP单次120s，超时先查产物，不能把缺图称成功。
- 本地renders/stage_bc_r19_comparison.jpg、review_r19四角度/contact_sheet、stage_bc局部图；qa/geometry_r19、seat_interfaces_r19、stage_bc_r19。详细reviews/r19_stage_bc.md。
- 后续优先前罩/侧罩闭合可见区、稳定特征及59/60独立标定，再修曲面；C先核对变速箱输出—链轮/护杠支座/悬挂。B/C未达标；低可信度预算不能变保证轮数。
- 两子任务请求gpt-5.6-luna/medium，实际配置未回传。主线程纠错、集成、验收。照片/含照板/镜头标注/blend/QA/真实牌号仅本地；只显式暂存代码、文档、控制数据。

## r15之后的计划管理纠正（优先于历史下一步）
- 用户追问还需几轮/是否可控。r编号仅源文件修订，不作里程碑或剩余工期依据；承认之前缺少封顶轮次和不收敛退出机制。
- 当前暂定剩余工作预算10–14个大工作轮，低可信度的管理预算，不是保证10–14轮达到1:1的完工预测。第一轮证据基线后必须显式重估，不能静默追加。
- P1参考/验收基线1轮；P2主要覆盖件灰模3–4；P3机械驾驶位附件3–4；P4版画磨损1–2；P5材质UV1；P6复核交付1–2。详见ITERATION_PLAN.md。
- 下一轮优先P1，核清有效镜头、可见边界/关键点覆盖、已使用照片与真正独立视角的可行性；不要再直接开一轮油箱微调。P1+P2共4–5大轮必须给整车灰模验收或失败原因/方案重估，不自动加轮。
- 每个大轮内部连续完成多候选和验证；不要求用户反复说继续。相同误差连续两轮未超标注不确定性地改善，停止该方法，检查证据/拓扑/装配原因再换路线。
- 达到工作包预算仍不通过，要记录具体失败和重新估算；不降低98%等原验收要求，不自动进入材质/4K。当前仅修计划，无新几何、无质量通过声明。

## 历史状态 V2 / r15（几何状态）
- 用户要求连续迭代到有明显进展再汇报，本轮从r13连续做到r14再r15，全部Blender MCP后台，不使用Computer Use。
- 最新blends/15_gray_review.blend，589对象/19quad控制网格，M1_NOT_PASSED。只改Body_Tank及FuelCap/Core的Z；其它物件控制几何/变换和全部相机内参/矩阵签名未变。
- 复核发现初版r14 crown项在循环外，只69上缘参与；62上缘仅事后检查。主线程确认、修复、加入实际参与视角断言，并继续全10截面/40参数拟合，选full_joint_w2_r15。旧r14实际渲染测量有效但不可称双上缘联合拟合。
- 油箱保持80点/69quad封闭端盖；无Solidify、无Bevel，镜像/细分/三角化/seat Boolean保留。相对r13最大控制点位移49.13mm；油箱盖抬5.44mm。源/JSON已同步；内部壁厚和真实间隙未验证。
- 实际Cycles：62上缘mean13.62→4.31/P9520.35→17.63；69上缘17.05→0.71/P9529.03→1.43；62后缘21.17→16.71；63后缘3.82→1.49。69后缘2.82→3.15/P954.39→6.19、接缝2.86→4.33/P956.45→8.63略退步。63接缝4.09→4.14。不得宣称全指标改善。
- 旧标注约±4px，新62/69上缘约±5px。62/63/69均拟合，64欠约束回看，无新增独立holdout。不是IoU/关键点精度/整车百分比。62后缘/前端局部偏差、肩部折线和接缝仍开放。
- 最终局部油箱/座垫相交、自交、非流形均0；座垫对Tail/SeatSide/PillionBase仍0。仅名义构造尺寸通过，全车装配未验收。
- 本地renders/tank_crown_r15_comparison.jpg、review_r15四角度/contact_sheet；qa/tank_review_r15.json、tank_frozen_r15.json、geometry_r15.json、seat_interfaces_r15.json。记录reviews/r15_tank_full.md。
- extract_tank_full_basis仅明确冻结r13；fit_tank_full为双上缘正确版本，读取本地r14候选作初值、默认拒绝已有报告。apply_tank_candidate另存并显式迁移端盖；不得在精修源盲目重跑历史拟合。review_tank_r15接受实际after修订tag。
- 后续继续油箱残差/肩部/接缝，再车头/侧罩；镜头修订单独做。不进入贴花/材质/4K。
- tank_evidence请求gpt-5.6-luna/low，实际配置未回传；其只读复核发现约束遗漏，主线程核实修复后重新计算和渲染。

## 历史状态 V2 / r14
- 用户要求连续迭代到有明显进展再汇报，不使用Computer Use；本轮全部建模经Blender MCP后台，非GUI操作。
- 最新源blends/14_gray_review.blend；589对象、19个quad控制网格，M1_NOT_PASSED。油箱整段上缘/后部体量有可见改善，其余全车形体仍明显不符。
- 仅Body_Tank、FuelCap/Core改变；其它对象控制几何/变换及全部相机矩阵/内参签名未变。油箱80顶点63面→80顶点69quad面，cap_ends=True，thickness_mm=0，移除旧Solidify；镜像/细分/三角化/座垫避让Boolean保留。未保留任何新增Bevel。
- 后续确认r14只69上缘进入求解，62上缘仅事后诊断；r15已纠正。该轮36参数候选crown_w2_r14，最大控制点位移37.73mm；前9截面可改变。油箱盖XY不动，Z随表面抬1.05mm。封闭外形不代表真实油箱壁厚或容量已验证。
- 原r13边界和镜头冻结；新增本地tank_crown_r14上缘标注约±5px。62/63/69都参与拟合，不能将69称本轮holdout。旧r13后缘/接缝标注约±4px。
- 实际Cycles ID输出：62上缘均值13.62→7.27px、后缘21.17→17.24；63后缘3.82→2.09；69上缘17.05→1.18、后缘2.82→1.73。62上缘P95反而20.35→21.80；69接缝均值2.86→4.42/P956.45→7.63，必须保留退步项。不是IoU/关键点误差/整车百分比。
- 失败候选只归档本地：较强侧面拟合破坏69；部分候选自交35–40；cap_shell与座垫相交444；crown_round新增1.5mm倒角自交6。不能把它们当最终版。最终源局部相交/自交/非流形均0，座垫对三处座尾分件相交仍0。
- qa/tank_frozen_r14.json记录实际对象签名；calibration/r13_tank_frozen保存输入快照。油箱控制JSON已同步69quad拓扑；apply_cages能在r14上更新，在r13上直接套新版需显式迁移，不可忽略拓扑检查。
- 本地renders/tank_crown_r14_comparison.jpg、review_r14四角度/contact_sheet；qa/tank_review_r14.json、geometry_r14.json、seat_interfaces_r14.json、tank_interface_14_gray_review.json。记录reviews/r14_tank_crown.md。
- extract_tank_crown_basis仅从明确冻结r13提取无壳/无Boolean的线性提案，最终必须复核完整修改器；fit_tank_crown只写候选；apply_tank_candidate显式封闭端盖另存；不得对新精修源随意重放历史步骤。
- 下一步先62后缘、前部上缘局部偏差与肩部折线/接缝，不继续用整体位移解决所有角度。相机修订另立记录；独立角度和整车mask未通过。不进入贴花/材质/4K。
- tank_evidence请求gpt-5.6-luna/low，只读证据复核；实际运行配置未回传。主线程完成图检、改形和验收；没有采用其“69不能参与任何拟合”的过强推断。

## 历史状态 V2 / r13
- 最新源blends/13_gray_review.blend，589对象、19个quad控制网格，仍M1_NOT_PASSED。r11源与r6.2原件未变，r12没有几何文件。本轮MCP后台处理，不宣称GUI场景已更新。
- 只修改Body_Tank前5个后部截面的Y，分别−3.5/−5/−10/−10/−3.5 mm；X/Z、其它18个cage、相机均未改。r11_interface_frozen的35项中仅Body_Tank JSON变化；实际相机签名未变。
- 新本地annotations/tank_interface_r13.json：62/63/69油箱后缘、油箱—座垫开放接缝；62/63附黑饰板上沿，约±4px。不是闭合mask或同名三维关键点。62/63排序，69额外检查，不是独立holdout。
- 初批18大候选、第二批12小候选加1基线；较大后移使69后缘变差，拒绝。2个小候选有自交，拒绝。保留e10_w0_z0。另试1mm倒角有15自交候选，未保留。
- 注意13_interface_candidate.blend是失败倒角源，不可作为最终版；13_interface_unrounded_candidate.blend才是保留候选，最终13_gray_review.blend。新增倒角不在最终源中，尖折仍未消除。
- 实际Cycles整帧分件颜色输出计算：62后缘均值25.1→21.2px/P9526.9→22.8；63均值7.3→3.8/P9512.4→7.8；69均值2.8→2.8/P957.8→4.4，但中位1.5→2.9，不能宣称全指标改善。三视角接缝均值9.1→8.5、4.6→4.1、3.5→2.9，变化多在标注不确定性内。
- 接缝距离是开放参考线到可见油箱边界的单向距离，并筛选距可见座垫≤10px的边缘。10px是图像筛选规则，不是实测间隙。完整轮廓IoU/关键点/独立角度均未通过。
- CPU深度投影补入23个其它物件的3247个局部遮挡三角面，已对Cycles整帧分件颜色输出核对（实现一致率99.89–100%，绝不是照片IoU）。最终照片指标取实际Cycles输出。
- Blender原生裁切有取整差异：实际62框[540,720,750,900]，63[445,761,665,945]，69[930,525,1150,705]，通过裁切/整帧ID图精确对应确认；不能只由边界浮点数猜原点。图像和照片按实际框对齐。
- 最终Tank/Seat无表面相交、非流形边和非相邻自交候选；座垫对Tail/SeatSide/PillionBase仍0相交。名义轴距/盘径维持，不代表实车精度。相邻5个求值网格与r11逐值相同。
- 本地renders/tank_interface_r13_comparison.jpg、review_r13_{62,63,64,69}.jpg/contact_sheet；qa/interface_review_r13.json、interface_raster_validation_r13.json、interface_frozen_r13.json、tank_interface_13_gray_review.json、geometry_r13.json。记录reviews/r13_tank_rear.md。
- 下一步针对油箱后半部曲率与接缝：先补跨图稳定特征，分开处理上下边界，不能继续整体后移去迎合62。62约21px残差、尖折、镜头及后座高度不确定性仍开放。不加材质/贴花/4K。
- generate_interface_candidates只从r11生成本地历史候选且拒绝已有输出，不可对当前r13 JSON随意重跑。export_interface_meshes/renderer/validate/review可复核当前实际源；ID材料仅用于不保存的诊断进程。
- interface_evidence请求gpt-5.6-luna/low，只读文档/代码；工具未确认实际配置，子任务图像helper失败。主线程完成图检和几何验收；没有采用其关于可见尖折成因的未证实推断。

## 历史证据检查 V2 / r12（当时模型为r11）
- 完成69镜头假设敏感性与后座投影传播；本轮未改相机/控制网格/模型，最新源仍blends/11_gray_review.blend，未制作虚假的12几何文件。M1_NOT_PASSED。
- Blender MCP后台读取r11实际求值网格，写qa/tail_mesh_r11.json；没有保存场景。环境仍5.2.2 LTS。
- scripts/camera_sensitivity.py：仅轮圈68观测+原转向先验拟合25组离散焦距/半径/主点假设，16组通过RMS≤1/P95≤2/无贴边等诊断筛查。主点±3%是测试幅度，非真实参数边界；高焦距存在局部极小值，不能作为全局排除证据。
- calibration/camera69_sensitivity_r12_refined.json为本轮传播输入；初版camera69_sensitivity_r12.json保留。两个文件均仅诊断，不可覆盖正式camera_69.json。新脚本默认拒绝覆盖，后续另存新修订。
- 新轮圈RMS排除转向先验，冻结镜头约0.383px；旧0.395包含先验，不能写成改善。低残差不等于相机验收。
- scripts/pillion_camera_sensitivity.py：相机拟合后才对固定r08/r11后座做投影和诊断Z平移，所有位移均未写回mesh。23份相关相机/标注/cage/mesh输入哈希不变。
- 16候选下旧r08诊断上调+78.5..+104.7mm，r11诊断补偿−13.0..+15.8mm；固定r11质心投影横/纵跨度24.5/15.8px。支持保留上调方向，但不是实测精度、连续范围保证或统计置信区间。
- 仍用拟合视图69和±4px人工后座闭合边界；独立分件投影不含相邻遮挡。两个可靠独立视角门槛仍未通过，70仍失败。没有新增形体改善或验收。
- 本地renders/camera69_sensitivity_r12.jpg；qa/pillion_camera_sensitivity_r12.json、camera_sensitivity_frozen_r12.json；公开记录reviews/r12_camera_sensitivity.md。不渲染4K，不推照片或对照图。
- 下一步补油箱—座垫可见接缝/跨图稳定特征，继续后座高度独立依据。69镜头畸变、圈贴侧偏及车型先验尚未扰动，后续标定另立修订；不得边动镜头边改cage。61仍保留。
- 只读camera_audit请求gpt-5.6-luna/low，实际运行配置未回传；主线程复核其结论并完成计算/图检。初次helper失败后已授权只读重试完成，子任务未改文件/无下级委派。

## 模型状态 V2 / r11（r12未改形）
- 最新源reconstruction_v2/blends/11_gray_review.blend；589对象、19个quad控制网格，M1_NOT_PASSED。r01–r10及r6.2旧源保留。
- 本机已为5.2.2 LTS；本轮通过Blender MCP后台CLI处理独立源，交互127.0.0.1:9876未连接，未向GUI追加场景。勿把历史r10会话状态当当前可用连接。
- 仅处理油箱—骑手座求值表面接口，所有19个cage、相机/标注共34份输入哈希未变；场景相机签名也未变。冻结快照calibration/r10_interface_frozen。
- 新Tool_TankSeatClearance复制r10辅助体，与Seat_Rider共享data、COPY_TRANSFORMS，外扩3mm后再三角化；Blockout中隐藏，export_exclude=True。Body_Tank厚度后加Stable_Interface_Triangles和Editable_RiderSeatInterface差集，保留原cage。
- 两个helper都依赖Seat_Rider.data；显式换mesh必须同步两者。3mm仅构造余量，不是实测或处处精确等距证明。
- 同版5.2.2下，油箱/座垫三角相交对583→0；两者非流形边/非相邻三角面自交候选均0。骑手座与Tail/SeatSide/PillionBase仍无表面相交。r10原363是多边形计数，不能与三角计数作百分比。
- 直接移动8个油箱点导致自交的候选已否决；未三角化差集仍有7组自交候选，也否决。失败blend/QA仅本地归档，qa/Body_Tank_r11_candidate.json不可覆盖有效控制网格。
- 62/63/69原分辨率局部改前/后用同一Blender重渲染，render_interface_crops+review_tank_interface生成renders/tank_seat_r11_comparison.jpg。69浮点裁切多1列，原照框对齐924..1090。
- 外观变化小：62接口尖折、63后缘曲率/饰板遮挡、69缺口仍不符。未新增轮廓改善指标，更不能称座尾或整车通过。后座高度与69镜头依赖未解除。
- 四角度review_r11_{62,63,64,69}.jpg/contact_sheet；qa/tank_interface_11_gray_review.json、seat_interfaces_r11.json、geometry_r11.json、interface_frozen_r11.json。记录reviews/r11_tank_interface.md。
- 下一轮先复核69镜头敏感性和后座高度独立依据，明确油箱—座垫可见分件边界再改形。仍在座尾灰模阶段，不扩展材质/贴花/4K。
- 本轮未启用子智能体，主线程完成局部修正与复核。refine_tank_interface只从r10另存新候选，拒绝覆盖，不能随意重跑迁移。

## 历史状态 V2 / r10
- 最新源reconstruction_v2/blends/10_gray_review.blend；MCP当前场景GSX250R_Reconstruction_V2_Gray_r10.002；588对象、19个quad控制网格。r09与全部旧源保留，M1_NOT_PASSED。
- 本轮只修改Seat_Rider、Body_SeatSide两段上沿、Body_PillionBase前端；后座本体/尾罩主体/镜头和其它cage未改。原镜头和标注哈希冻结在r09_tail_frozen；实际场景相机矩阵与内参也比对未变。
- 骑手座13参数小幅拟合62/69，7参数触及预设边界，不继续扩大边界。63新增开放可见下缘标注，只检查未优化；63此前已用过，不能称项目独立holdout。
- 实际求值网格：62中位7.2→3.0px/P9516.6→13.0；69中位12.5→6.0/P9522.6→16.8；63开放下缘单向12.1→9.0/P9521.8→18.6。约±4px标注不确定，不是关键点误差或整车相似度。
- 新骑手座端面封闭；局部相关求值网格非流形边为0。构造尺寸检查维持。r09后座高度假设未定型，本轮未再改。
- 新Tool_SeatClearance在Blockout隐藏，export_exclude=True，共享骑手座mesh并COPY_TRANSFORMS；法向外扩3mm供两处Editable_SeatClearance差集。3mm是构造间隙，不是实测。若显式替换Seat_Rider.data，必须同步helper.data；正常apply_cages改点会共享更新。
- 骑手座与Body_Tail/Body_SeatSide/Body_PillionBase求值表面相交对为0；与Body_Tank仍有363对，不能称装配通过，计数不是可见质量评分。
- 最新局部对照renders/seat_tail_r10_comparison.jpg，四角度review_r10_{62,63,64,69}.jpg/contact_sheet；qa/seat_tail_r10.json、seat_interfaces_r10.json、geometry_r10.json。review_tail支持before/after标签，r10的63是单向开放边界。
- 记录reviews/r10_rider_seat.md。下一步先骑手座前端—油箱连接、座尾接口及固定参考关键点，后座独立验证和镜头敏感性仍未通过。不进入贴花/材质/4K。
- 子任务tail_evidence请求gpt-5.6-luna/low，只读证据复核，未写文件；工具未确认实际配置。主线程完成标注、曲面及验收。
- extract_seat_basis/fit_rider_seat/apply_rider_candidate/prepare_seat_joins/add_seat_clearance是本轮候选流程；从明确修订运行，不能对精修网格随意重放。后续以最新JSON/独立blend为准。

## 历史状态 V2 / r09
- 最新源reconstruction_v2/blends/09_gray_review.blend；MCP当前追加场景GSX250R_Reconstruction_V2_Gray_r09.002；r08及旧场景保留。
- 本轮不启用子智能体，用户要求兼顾质量与额度；只做座尾，低采样对照，无4K和细节扩展。
- 587对象、19个quad控制网格。保留Seat_Pillion、Body_Tail修改，新增Body_PillionBase可见黑色过渡壳；骑手座和Body_SeatSide试改因62侧面退步已回退。
- r08_tail_frozen保存旧网格及输入哈希。旧镜头、标注、排除区哈希全部未变；新增seat_tail_r09标注仅本地，约±4px。70仍失败不参与评分。
- 69后座双向轮廓距离median36.2→3.6px、P9550.2→14.9px，局部IoU约0.802。这是候选镜头下的拟合分件诊断，不是关键点误差、独立验证或整车相似度；整体M1_NOT_PASSED。
- 后座约90mm高度调整仍依赖69候选，不能作为实测尺寸；隐藏支座/副车架深度及完整穿插未通过。尾罩尚无可靠闭合标注。
- 后座端面cap_ends由cage_faces显式四边面连接；apply_cages复核完整连接。refine_tail_r09只用于独立r08迁移，不能对精修数据重跑。
- renders/seat_tail_r09_comparison.jpg为局部改前/后/叠加；review_r09_{62,63,64,69}.jpg和contact_sheet为四角度；qa/seat_tail_r09.json、geometry_r09.json记录误差与实际几何。
- 详细结果reviews/r09_seat_tail.md。下一轮继续骑手座、尾罩接缝与后座圆角/连接；先修座尾，暂不进入油箱、镜子/灯具或材质。

## 历史状态 V2 / r08
- 最新源 reconstruction_v2/blends/08_gray_review.blend；r01–r07保留；r6.2 baseline及原blends/10_final.blend保持冻结。
- 586对象、18个quad控制网格；镜像/细分/厚度保留。data/guard_control.json、mirror_control.json控制附件轮廓。
- 已改油箱黑饰板边界、连续侧罩/下伸部分、油箱端部反折、尾罩遮挡、座垫连接缺口、对称三角护杠、驾驶位内衬、位置灯、镜壳。仍有明显不符，M1_NOT_PASSED。
- 控制数据在data/control_cages；旧分离Body_FairingBlade在data/archive/r04。不要把它重新加入有效集合。
- 62/63：真实SIFT去重61点，剔除2组错误纹理对应，59点；12点保留不拟合。极线保留点median约0.17px/P95约1.53px，仅说明相机间一致性，不是模型误差。匹配多集中小贴纸，不能冒充均匀分布。
- 联合镜头和旧数据在calibration/r04_frozen；之后各轮cage快照在r05/r06/r07_frozen。相机修改均有轮圈/实图对应依据，不能为掩盖造型随意调镜头。
- 新增69/70两图后总计12张。69左前无当前三角护杠，70右后有三角护杠；看清尾座、左侧罩、排气及后减震。新照片不上传。
- 69的正确轮圈ROI在原图1706x1280左下前轮和右中后轮。首批子任务错把前轮两段作两轮，且错误使用弧线质心当轴心；已否决并重做。不得沿用该失败候选。
- 69使用后倾25.6°/拖曳104mm的转向轴候选，轮圈RMS约0.395px；70约9.007px且触及焦距/角度边界，REJECTED_HIGH_RESIDUAL_DIAGNOSTIC_ONLY。不可把70计作有效角度。两图轴端不可辨，不设伪造中心。
- 62/63/64仍使用其历史简化转向模型。统一升级需要重标定/重渲染，不能直接混用参数。
- 64前轮裁切欠约束；66已用于灯组/镜壳结构，不能再称严格holdout；61尚未参与本轮形体调整。两个可靠独立视角门槛未通过。
- 5张四联图及总览为renders/review_r08_*.jpg，保持新横图比例；70明确失败。没有完整闭合mask，不计算假IoU。
- 几何QA从求值网格测量：轴距1430.0001、盘290/240、胎宽110/140mm；只通过名义构造检查。guard左右中心线镜像另测，安装深度未通过。
- 最新场景通过MCP追加至会话，名GSX250R_Reconstruction_V2_Gray_r08，原会话场景保留。磁盘08文件是单独正常源文件。

## 编辑与复现
- build_gray.setup只新增场景，不清空任何现有对象/集合；本轮纠正了源码与旧文档不一致的删除逻辑。
- build_gray/apply_cages支持crease_columns/crease_boundary；apply_cages检查完整面连接，拒绝改拓扑，拒绝覆盖已有输出。revision可显式第二参数rNN；默认新时间戳文件。
- apply_cages以JSON为准。精修后先同步JSON或保存独立源，不允许旧JSON覆盖精修。
- prepare_r05/refine_r06/refine_r07/refine_r08/upgrade_r05是历史迁移，不是每天重跑的流程。不要对精修后的数据重复执行。
- initialize_cages遇已有文件拒绝覆盖。fit_cameras默认保留；新增提取脚本也默认保留标注。
- render_gray按镜头metadata选择竖轴/倾斜轴，并临时转前轮、叉、挡泥板；69临时隐藏当前三角护杠以对应早期照片。保存的最新源始终带当前护杠。
- make_review_boards按照片原始宽高比生成五组对照，排除区固定；不拿局部橙线当完整分割。
- 下一步见ISSUES：先处理车头曲率与镜头70、座尾/机械穿插、完整分件mask及独立角度。继续灰模；不进入最终材质和贴花。

## 参考与环境
- 豪爵中国GSX250R-A：https://en.haojue.com/NEWGSX250R/canshu.html 。排除GSX250R-F。
- Suzuki L8官方PDF第1/8页明确25.6°/104mm；属于车型家族资料，用户具体年份适配未证实。不能称精确实测。零件爆炸图不是尺寸蓝图。
- Blender：D:\Program Files\Steam\steamapps\common\Blender\blender.exe。
- Python：C:\Users\22797\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe；科学依赖.tools/calibration。
- 普通sandbox helper可能helper_unknown_error；可对已授权项目范围操作走require_escalated正常自动审查，不绕过拒绝。仅工具helper失败不等于安全审批拒绝。
- MCP 127.0.0.1:9876；活跃场景可能与磁盘不同，先查场景和修订。

## 本轮委派与复核
- publish_audit请求gpt-5.6-luna/low：推送范围只读审核，后续修build_gray/apply_cages；主线程复核并修正revision推导及覆盖保护。
- feature_matches请求gpt-5.6-luna/medium：真实SIFT匹配，后续新照片采样；主线程剔除误匹配、纠正69 ROI/伪轮心，重做联合标定和倾斜转向轴候选。
- 工具未确认实际运行配置，只能报告请求值。未继续向下委派。不能直接把未经复核的子任务结果当验收。
## 用户追问后的执行纠正
- 用户询问车尾黑箱及是否按系统路线推进。已由MCP及脚本核实：黑箱是make_review_boards把luggage排除遮罩画到了纯灰模面板，不是模型尾箱。
- 已改纯灰模面板不绘制遮罩，其他面板用不透明斜线和文字标明排除区，真实车牌仍遮蔽；原多边形不变。旧显示图本地归档renders/archive/r08_masked_display。
- 明确承认此前跨部件修补、镜头/形体交替变动、缺少统一量化的问题。以后遵循ITERATION_PLAN.md，每轮一个主要部件组、固定相机/排除区、改前改后对照与未通过项。
- 下一次建模专注座尾，随后油箱，再车头/侧罩；暂不扩展镜子/灯具细节。70相机失败不用于验收。当前完整M1仍未通过。
- 本次仅修正展示和执行计划，blend几何保持r08，不能描述为新一轮形体改善。
