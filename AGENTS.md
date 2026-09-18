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

## 当前状态 V2 / r08
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