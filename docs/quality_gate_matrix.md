# Quality Gate Matrix

| 阶段 | 必须通过的门槛 | 阻塞等级 |
|---|---|---|
| Idea Brief | 核心想法、时长、类型、限制不为空 | P0 |
| Story | 2-5 分钟可执行，有结构化 `story.json` | P0 |
| Art Direction | 不改故事，风格可执行，有禁用项 | P1 |
| Storyboard | 每个 shot 有时长、资产、动作、镜头 | P0 |
| Sequence Review | 无未处理 P0，P1 已修或接受 | P0 |
| Asset Manifest | 分镜引用资产全部存在，无 ID 冲突 | P0 |
| Character Assets | 主要人物三视图状态明确 | P1 / final P0 |
| Scene Assets | 核心场景空间关系明确 | P1 |
| Prop Assets | 母题道具锚点稳定 | P1 |
| Image Results | 图片结果或缺失原因已记录 | P1 |
| Audio | 有声镜头音色 ready 或 marked missing | final P0 |
| Video Prompts | 逐 shot 文件齐全，中文-only，无默认 `@PROP` | P0 |
| External Handoff | 每个 shot 有可复制提示词和素材清单 | P0 |
| Generated Media Review | 最佳 take 无 P0 | final P0 |
| Continuity Review | 文本和生成结果一致性通过 | final P0 |
| Final Package | 无假完成，缺失项明确 | P0 |
