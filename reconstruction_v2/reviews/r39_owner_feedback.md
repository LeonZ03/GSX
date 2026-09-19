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

