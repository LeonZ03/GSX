# GSX250R 实车重建 — AI 工作记录

## 需求与最高优先级
- 用户批准 V2 重建计划：先资料纠错、照片匹配、准确灰模。灰模未通过，不进入新版完整贴花、最终材质、4K成片或导出。
- 目标实车1:1；当前未达标，不用面数、分辨率、文件完整或名义尺寸代替外形验收。隐藏尺寸不能盖章100%。
- 本机 Blender 5.2.1 LTS，必须使用 Blender MCP。+X右、+Y前、+Z上；场景米、控制网格mm乘0.001。
- 以 IMG/ 实车照片为准：蓝白版画、荧光轮圈贴、左右三角管护杠、左把手机夹、方向阻尼器、指定京B。排除尾包、网绳、骑手、手套。只还原可辨认磨损。
- 不要求用户补照片、测量或选择配色；缺角主动搜原厂证据，不能臆造文字/贴纸。新版未制作错误日文标记。

## 隐私与授权
- 用户最新明确授权“真实照片不要推送，别的可以推送”。可以推送代码、文档、派生控制网格，不需再次确认。
- 原照、含原照对照图、标注、镜头、参考下载、blend、渲染、真实牌号配置和相关成品均保持本地。IMG/等路径已被.gitignore排除。
- 真实牌号只使用config/*.local.json，不输出日志或文档。57/59指定京B；60及新增图片的旧牌不替换它。M1只有空白牌板、无文字对象。
- 本地预览先遮蔽车牌及固定排除区，不推送照片。不可把允许推代码理解为允许发布真实号牌成品。
- origin使用ssh.github.com:443/LeonZ03/GSX.git；仓库为公开。命令级safe.directory，不改全局Git，不强推。
- 已推送d497004与9fbcbf5；本轮后续提交需再核对范围，仅显式暂存代码/文档/控制数据。

## 当前状态 V2 / r10（以本节为准）
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
