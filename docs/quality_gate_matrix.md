# Quality Gate Matrix

| 阶段 | 必须通过的门槛 | 阻塞等级 |
|---|---|---|
| Idea Brief | 核心想法、时长、类型、限制不为空 | P0 |
| Story | 剧本可读、人物动机清楚、适合 2-5 分钟；不得输出 `story.json` | P0 |
| Art Direction | 用户视觉方向优先；无明确方向时先给候选方案；最终 `style_bible.md` 只含画面风格、整体色调、光线风格、AI 视觉执行要求 | P1 |
| Storyboard | 每个 shot 有时长、动作、具体构图/景别/镜头；不得定义资产 | P0 |
| Asset Manifest | 分镜引用资产全部存在，无 ID 冲突 | P0 |
| Character Assets | 主要人物身份锚点稳定 | P1 / final P0 |
| Scene Assets | 核心场景空间关系明确 | P1 |
| Prop Assets | 关键道具锚点稳定；普通道具不强行独立生成 | P1 |
| Storyboard Prompts | 每个 shot 都有分镜生图提示词，且资产引用来自映射 | P0 |
| Video Prompts | `video_prompts.md/json` 齐全，中文-only，无默认 `@PROP` | P0 |
| Final Handoff | 只交付 story、video prompts、角色资产、场景资产和分镜图 | P0 |
