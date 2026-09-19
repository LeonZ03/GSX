# GSX250R 实车重建 — AI 工作记录

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

## r15之后的计划管理纠正（优先于历史下一步）
- 用户追问还需几轮/是否可控。r编号仅源文件修订，不作里程碑或剩余工期依据；承认之前缺少封顶轮次和不收敛退出机制。
- 当前暂定剩余工作预算10–14个大工作轮，低可信度的管理预算，不是保证10–14轮达到1:1的完工预测。第一轮证据基线后必须显式重估，不能静默追加。
- P1参考/验收基线1轮；P2主要覆盖件灰模3–4；P3机械驾驶位附件3–4；P4版画磨损1–2；P5材质UV1；P6复核交付1–2。详见ITERATION_PLAN.md。
- 下一轮优先P1，核清有效镜头、可见边界/关键点覆盖、已使用照片与真正独立视角的可行性；不要再直接开一轮油箱微调。P1+P2共4–5大轮必须给整车灰模验收或失败原因/方案重估，不自动加轮。
- 每个大轮内部连续完成多候选和验证；不要求用户反复说继续。相同误差连续两轮未超标注不确定性地改善，停止该方法，检查证据/拓扑/装配原因再换路线。
- 达到工作包预算仍不通过，要记录具体失败和重新估算；不降低98%等原验收要求，不自动进入材质/4K。当前仅修计划，无新几何、无质量通过声明。

## 当前状态 V2 / r15（几何状态）
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
