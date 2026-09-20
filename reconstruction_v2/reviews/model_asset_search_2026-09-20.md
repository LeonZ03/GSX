# GSX250R 现成模型检索（2026-09-20）

## 结论

本轮只检索和核查公开资源，没有改动 r50 工作模型、没有购入模型、没有获取付费源文件。尚未确认“免费、同款、精度足够且可实际下载”的整车资产。不得把搜索未找到表述为网上不存在。

## 同款商业候选

- 3DModels.org：<https://3dmodels.org/zh/3d-models/suzuki-gsx250r-2023/>。URL 为 2023，当前标题为 GSX250R 2025，SKU h3dA233069。页面列出 blend / FBX / OBJ / GLB、约 55.9 万多边形和主要零件分离；这是供应商描述，未回读模型验证。约 £175，活动/地区显示有差异，以实际结算为准；Royalty Free 不表示免费下载。
- 公开转台入口：<https://3dmodels.org/ua/360-view/?id=233069>。可以作为正常网页可见参考线索，但本轮程序请求商品页、转台页、公开缩略图均返回 403，未取得可用参考图或证明其底层采用图像序列/三维网格。不能声称已获取完整转台或可提取源文件。
- Cults：<https://cults3d.com/en/3d-model/various/suzuki-gsx250r-2017-sportbike-motorcycle>。搜索索引显示约 US$2.93、OBJ/STL，免费标题与价格冲突，应按收费候选处理。原页未可靠加载，许可、原始作者权利和网格质量未核实，未推荐购买。

## 免费候选与排除项

- SketchUp 3D Warehouse：<https://3dwarehouse.sketchup.com/model/ad8d1864-91a1-43e9-a91f-bf894c26e8a8/Suzuki-Gixxer-250-SF>。作者 Cyrus Khan，标题 Suzuki Gixxer 250 SF，但描述写 GSX250R，公开预览外观接近 GSX250R。不是仅依据 Gixxer 名称认定为同款。
- 通过匿名公开目录检索 GSX250R、GSX-250R、GSX 250、Suzuki 250 找到上述候选；元数据记录 2817 polygons、9 materials。实际查看公开预览：轮胎轮廓明显分段，发动机/前灯/版画很大程度由图片表现；不适合作为 1:1 曲面基准。仅为预览判断，没有完成源网格检查。
- 官方 COLLADA ZIP 源下载返回 401 / ANONYMOUS_ACCESS_NOT_ALLOWED。停止该下载路线，未绕过登录限制，未下载预览网格充当源模型。
- Warehouse 使用条款 FAQ：<https://help.sketchup.com/en/3d-warehouse/3d-warehouse-terms-use-faq>。下载不收费，允许修改；有独立转售/聚合等限制，不能简单称 CC0。未取得源文件，未导入当前工作场景。
- Sketchfab 公开 API 对 gsx250 / gsx250r 返回空结果，只说明这些查询本次未命中。
- CGTrader 免费 STABILZER SHOCK GSX250：<https://www.cgtrader.com/free-3d-models/industrial/industrial-machine/stabilzer-shock-gsx250>。只有 SLDPRT 零件，2014 年发布，页面标 no AI；未证实适用于目标车，未下载采用。
- 3D66 聚合页 <https://3d.3d66.com/relation/relation_2184250.html> 的搜索索引列有现代铃木 GSX250R 摩托车模型；尚未核到有效商品详情、免费条件或许可，不计为可用来源。

## 下一步使用方式

公开商品预览只能作为二级形体参考，实车照片仍是最终依据。若公开预览可正常访问，重点核对主灯外沿与黑色凹槽、蓝色外罩连续面、油箱肩部、座垫下垂侧裙和板件分缝。不能把光影当接缝，也不能把预览当精确尺寸图。未经许可不提取受限源模型、不把展示图片制作成最终贴图或提交公开仓库。

如以后获得合法源文件，应在单独检查场景中验证车型年份、轴距、分件、贴图依赖和关键部位形似，再决定局部采用；不覆盖 r50。外部资产不自动证明 1:1。

公开目录元数据与检索中间资料在 references/public/model_search_2026-09-20/，受 Git 忽略，仅本地。本轮没有成功下载模型源或 3DModels 多角度图片。

## 后续：用户授权公开网页截图

用户已明确允许仅本次公开参考网页使用Computer Use，建模仍MCP。统一浏览器工具初始化（含重置）及技能备用Node初始化均在任何UI操作前因Windows sandbox helper错误退出；直接HTTP仍403。故本次尚未采集转台/商品图，图片数0。记录在references/public/3dmodels_gsx250r_233069/capture_manifest.json；不需要重复索取同一授权，工具环境恢复后继续正常公开预览采集。
