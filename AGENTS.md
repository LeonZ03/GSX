# GSX250R 实车重建 — AI 工作记录

## 最高优先级
- 用户已批准 V2 重建计划：先做资料纠错、照片相机匹配、准确灰模和对照。**灰模未通过时，不进入贴花、最终材质、4K 成片或最终导出。**
- 最终目标为实车1:1复刻；不能把未验证部分盖章为100%，不能用面数、4K或文件完整性代替外观验收。
- 本机 Blender 5.2.1 LTS，使用 Blender MCP。米制场景，控制数据用mm；+X右、+Y前、+Z上。
- 以 IMG/ 十张实车照片为准。蓝白版画、荧光轮圈贴、左右对称三角管护杠、左把手机夹、方向阻尼器、京B牌。排除尾包、网绳、手套、骑手。只重现照片可辨认的磨损。
- 不要求用户上传照片、选配色或量车；缺角主动搜索，找不到的尺寸标为未验收。

## 隐私与仓库
- 真实牌号只读本地 config/*.local.json；不写文档、日志或公开预览。57/59为指定京B，60为旧牌，不能混用。
- IMG、blends、exports、renders、qa、references/public、V2 baseline/annotations/calibration/references/raw 等均被忽略。只提交代码、控制网格、需求、公开资料索引。
- V2灰模使用空白牌板，无文字对象；真实配置保持不变。照片对照固定遮蔽车牌候选、人物和尾包。
- 旧审批曾拒绝回传含实际牌号图像；继续使用本地遮蔽预览，不外发原照或渲染。
- origin: git@github.com:LeonZ03/GSX.git。使用命令级 safe.directory，不修改全局Git设置，不强推。

## 当前状态（V2 / r04）
- r6.2 被用户否决为外观不符。已冻结 reconstruction_v2/baseline/10_final.blend 及哈希，不修改原 blends/10_final.blend。
- 新源：reconstruction_v2/blends/04_gray_review.blend。前3轮独立保留。当前为 M1_NOT_PASSED。
- 16份独立四边面控制网格保存在 reconstruction_v2/data/control_cages/。镜像、细分、厚度修改器保留；其中若干部件的跨向宽度仍估计。
- 62/63 已建立按真实荧光轮圈贴弧线校正的相机，相机含相对姿态和简化前轮转向。半径220±5mm仅为圈贴中心估计，不能误称17寸外缘实测。
- 64 左侧为未用于改网格的诊断视角，前轮裁切，标定欠约束，不算有效通过角度。61/66保留，尚未用于形体调整。
- 62/63首批子任务标注把轮圈近似成圆，经主智能体拒绝；已另存 rejected_initial/，主智能体重标并提取真实像素弧线。
- r02镜头与曲面已另存；r03修正镜头证据后重新投射照片侧边界；r04补齐座下侧罩和三角侧盖。
- 车头/镜子/风挡/座尾仍有明显差距，机械件及护杠安装点尚未逐件复核。真实版画、磨损、UV和最终材质尚未进入V2。
- 已输出62/63/64三张四联对照与总览，路径 renders/review_r04_*.jpg。不存在完成的轮廓IoU，不得宣称98%。
- 求值几何测量：轴距1430.0001mm，前/后盘290/240mm，胎宽110/140mm。只通过名义构造尺寸检查。

## 来源与参考判断
- 豪爵中国GSX250R-A参数：https://en.haojue.com/NEWGSX250R/canshu.html 。排除GSX250R-F，规格不可混用。
- 官方铃木零件目录已归档V2 references/raw/；日本型号同家族件号仅供结构证据，中国实车具体年份/件号尚待交叉核对。
- 62/63当前三角管护杠；61/66为早期单滑块，只比原厂车身；65为驾驶位参考；64为左链传动。
- 爆炸图不是比例蓝图，官网转台不是正投影。没有EXIF，镜头畸变尚未标定。

## 编辑、重建与检查规则
- 不再对新版运行旧 scripts/build_all.py 或旧累积缩放脚本。
- build_gray.py只新增独立场景，不清空现有对象/集合。第一次清空活动场景的尝试被自动审批拦截，已改成新增场景并单独写文件的安全方式。
- build_gray.py生成带时间戳的工作副本；早期01/02文件为library-only检查点，03/04是可直接打开到灰模的标准blend。
- initialize_cages.py遇到已有JSON拒绝覆盖；apply_cages.py显式以JSON为权威同步到新的blend。手工精修后先保存独立源文件并同步控制网格，不让旧JSON覆盖精修。
- upgrade_r03.py是历史迁移，不是日常构建入口。机械偏移使用placement_r03标记防重复。
- fit_cameras.py默认不改已有相机；--refit才重拟合并归档旧参数。修改镜头必须有证据修正理由，重生成全部受影响对照，不用镜头掩盖造型问题。
- render_gray.py保持相机内参与姿态，临时应用照片转向后渲染；不保存姿态到标准源文件。简化转向仍需改成准确转向轴。
- make_review_boards.py保存排除区和相机/标注哈希。橙色只是局部可见边界和实测像素弧线，不能当完整分割做IoU。
- audit_gray.py测量实际求值网格、检查quad控制网格。不能抄写常数伪装测量；模型毫米一致不代表实车毫米精度。
- 下一步严格按 reconstruction_v2/ISSUES.md：完善闭合mask和稳定关键点，解决镜头敏感度与至少两个独立有效角度，再持续修正灰模。

## 环境
- Blender: D:\Program Files\Steam\steamapps\common\Blender\blender.exe。
- Python: C:\Users\22797\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe。
- 本地校准依赖：.tools/calibration（NumPy/SciPy/OpenCV），不更改系统Python。
- 普通沙箱进程可能helper_unknown_error；项目范围操作通过require_escalated的正常自动审查执行。不绕过拒绝。
- MCP 服务127.0.0.1:9876；活跃场景可能是较早灰模，读前确认，不把其状态当磁盘最新版。

## 委派
- 本轮启动2个子任务：官方证据 reference_evidence 请求 gpt-5.6-luna/low；照片标注 photo_landmarks 请求 gpt-5.6-luna/medium。工具只返回任务名，实际运行配置未确认。
- 证据子任务完成来源归档及件号复核；标注草稿未通过质量检查，已由主智能体重做。子任务均未继续向下委派。
- 主智能体负责造型、标定、检查与最终结论；未经复核的子任务输出不能直接进入验收。

## 本轮仓库发布状态
- 已核实 LeonZ03/GSX 为公开仓库（GitHub只读元数据）。
- 用户最新明确授权：真实照片不要推送，别的可以推送。该授权包含本轮代码、文档和照片派生控制网格；不需再次询问。原照片、含原照的对照图及真实车牌相关成品仍仅本地。
- 已复核待推送的35个文件全部是代码、文档、JSON控制网格及公开资料索引，不含照片、参考下载、blend、渲染、标注、镜头配置或真实车牌。
