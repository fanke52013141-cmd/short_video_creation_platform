# Changelog

## 2026-07-04 - v1.0.3

### Changed
- [process] 简化第一阶段：`story_generation` 只输出 `outputs/story.md`，不再输出 `story.json` 或任何 story index。
- [process] 明确艺术总监先于导演出现，但只负责视觉方向；具体构图、景别、机位和镜头调度归 `storyboard_director`。
- [process] 沉淀视频分镜合并规则：合并对象是连续 `S###`，不是 `SC###`；`SC###` 只是合并边界。
- [process] 沉淀 Seedance 资产命名规则：人物/场景使用稳定命名与素材绑定，不按表情、动作、姿态、普通光影变化拆资产。
- [process] 明确资产图片生成执行节点可使用即梦网页端、ChatGPT 网页端、Codex 或外部工具；每个 `asset_image_task` 只生成一张图，禁止拼接图、四宫格和设定表。
- [skill] 将 `story_generation` 升级到 3.0.0，明确禁止在剧本阶段拆分镜头、角色状态、场景资产、道具资产或生成提示词。
- [skill] 将 `art_direction` 升级到 2.1.0：用户有风格/参考图时优先继承并补全；用户没有明确视觉方向时先给候选方案，不直接定稿。
- [skill] 将 `storyboard_director` 升级到 2.2.0：明确导演只输出 `shot_id`、`scene_id`、`duration_seconds`、`framing`、`camera_move`、`action_desc`，不输出人物、地点或资产拆分字段。
- [skill] 将 `asset_executor` 升级到 1.1.0：改为 Seedance 主体/场景/关键道具命名、素材绑定、生成决策和 shot 映射。
- [skill] 将 `character_prompt_generator`、`scene_prompt_generator`、`prop_prompt_generator` 升级到 2.1.0：分别适配身份资产组、场景参考图、关键道具才独立生成的策略。
- [skill] 将 `image_generation_executor` 升级到 1.1.0：改为工具无关的单图资产生成任务执行器，支持 `jimeng_web_manual`、`chatgpt_web`、`codex_direct`、`external_manual`。
- [skill] 将 `video_prompt_generator` 升级到 2.3.0：强连续动作优先合并，景别变化不再作为禁止合并理由；每条 `V###` 必须写入 `merge_decision`。
- [prompt] 更新 `skills/raw_prompts/story_generation.source.md`，删除机器可读故事输出要求，让模型专注剧本优化。
- [prompt] 更新 `skills/raw_prompts/art_direction.source.md`，删除 `art_direction.json`、构图硬字段和独立“禁止出现的视觉元素”字段要求。
- [prompt] 更新 `skills/raw_prompts/storyboard_director.source.md`，删除资产表、旧式资产 ID、复杂分镜提示词字段和多余 machine-readable 字段。
- [prompt] 更新 `skills/raw_prompts/character_prompt_generator.source.md`，删除角色状态变体/多视图拆分要求，改为人物身份资产组。
- [prompt] 更新 `skills/raw_prompts/scene_prompt_generator.source.md`，删除因光影变化拆场景的隐含逻辑，改为稳定场景绑定。
- [prompt] 更新 `skills/raw_prompts/prop_prompt_generator.source.md`，明确普通道具正文控制，只有核心道具才独立生成。
- [prompt] 更新 `skills/raw_prompts/seedance_video_prompt.source.md`，加入 `merge_decision`、强连续动作合并和景别变化可合并规则。
- [script] `validate_project.py` 的 `story` 阶段只校验 `story.md`，并将存在 `story.json` 视为不合格。
- [script] `validate_project.py` 的 `art` 阶段改为校验 `画面风格`、`整体色调`、`光线风格`、`AI 视觉执行要求`，并拒绝 `构图倾向` 硬字段。
- [script] `validate_project.py` 的 `storyboard` 阶段拒绝 `characters_in_shot`、`location`、资产 ID 和提示词字段。
- [schema] 删除已弃用的 `schemas/story.schema.json`；结构化从导演分镜阶段开始。
- [schema] 精简 `schemas/storyboard.schema.json`，删除 `characters_in_shot` 与 `location`。
- [schema] 扩展 `schemas/asset_manifest.schema.json`，加入 Seedance 命名策略、素材绑定、参考资产组和处理策略字段。
- [schema] 扩展 `schemas/video_prompt.schema.json`，要求每条 `V###` 包含 `merge_decision`。
- [config] 更新 `asset_policy`，记录人物不按状态拆、场景不按普通光影拆、道具只管控核心剧情道具。
- [config] 新增 `image_generation_policy`，记录单任务单图、禁止拼图和可选图片生成模式。
- [config] 更新 `video_prompt_policy.merge_policy`，记录强连续动作优先合并、景别变化可合并、跨场景/超时长/动作不连续必须拆分。
- [docs] 更新 README、schema contracts、local run 模板、Agent、flow 和质量门，统一 Seedance 资产命名、素材绑定和资产图片生成边界。
- [examples] 更新 `examples/minimal_run/`，移除 `outputs/story.json`，扩展 `story.md`，更新 `style_bible.md` 新格式，精简 `storyboard.json`，更新 Seedance 资产命名，并在 `video_prompts.md/json` 中加入合并判断。

### Reason
- 剧本优化阶段不应同时承担结构化抽取职责；否则会分散模型注意力，影响故事质量。
- 艺术总监在分镜前无法也不应规定具体构图，只应提供画面风格、色调、光线和 AI 视觉执行规则。
- 导演阶段应只完成镜头结构化和场景分组；人物、场景、道具和资产拆分属于资产执行官。
- Seedance 人物资产应以稳定主体命名和素材绑定为核心；常规表情、动作、姿态用文字控制，避免 ID 漂移和多人物误判。
- Seedance 场景资产应以空间结构为核心；普通光线、时间、天气变化用文字控制，避免无谓拆分。
- 资产图片生成不应被固定为即梦网页端；不同工具可以执行同一单图任务，但任务输入和输出路径必须统一。
- 视频提示词需要 `duration_seconds` 与 `scene_id` 做合并判断，因此这两个字段必须保留。
- 强连续动作如果被拆成多次生成，容易造成动作、手部、道具位置和人物姿态穿帮，因此在同场景且总时长不超过 15 秒时应优先合并。

### Validation
- 待 CI 验证：`python scripts/validate_project.py examples/minimal_run --phase all`。

## 2026-07-04 - v1.0.2

### Changed
- [ci] 新增 GitHub Actions workflow：编译 `scripts/validate_project.py`、解析 `checkpoint.template.json` 与全部 schema JSON、运行最小样例 `examples/minimal_run --phase all`。
- [examples] 新增 `examples/minimal_run/`，提供一套可跑通的最小本地 run，用作回归测试基线。
- [schema] 扩展 `schemas/video_prompt.schema.json`，要求 `video_prompts.json` 输出结构化 `V###` 计划。
- [schema] 新增 `schemas/reference_media.schema.json`，沉淀多参素材的类型、角色和用途约束。
- [skill] 将 `video_prompt_generator` 升级到 2.2.0，要求同时输出 `outputs/video_prompts.md` 与 `outputs/video_prompts.json`。
- [script] `validate_project.py` 新增 `video_prompts.json` 校验：检查 `V###` 连续性、shot 覆盖完整性、重复覆盖、单条时长、操作对象声明、上一分镜站位锚点和风险提示。
- [config] 更新 `video_prompt_policy` 与最终交付清单，加入 `outputs/video_prompts.json`。

### Reason
- 仅有 Markdown 提示词无法可靠校验 shot 覆盖、任务类型、操作对象和素材声明关系；结构化 JSON 可作为机器可验证的生产计划。
- CI 与最小样例可以防止后续修改 Skill、schema 或脚本时破坏核心流程。

### Validation
- 已在本地构建并编译新版 `validate_project.py`。
- 已用本地最小样例跑通 `python scripts/validate_project.py examples/minimal_run --phase all`。

## 2026-07-04 - v1.0.1

### Changed
- [skill] 将 `video_prompt_generator` 升级到 2.1.0，补入 Seedance 2.0 多模态多参考任务体系。
- [skill] 新增任务类型规则：`pipeline_shot_generation`、`multimodal_reference`、`video_edit`、`video_extend`、`combined_task`、`track_stitch`。
- [skill] 新增素材角色识别：首帧、尾帧、关键帧、人物资产、场景资产、风格参考、声音参考、配乐参考、环境音参考、动作参考、整体参考、编辑对象、延长对象。
- [skill] 强化硬规则：编辑对象与延长对象正文中禁止写 `参考@资产名`，必须分别使用 `严格编辑 @资产名`、`向前延长 @资产名` 或 `向后延长 @资产名`。
- [script] `validate_project.py` 增加视频提示词静态检查：必需 `【自检通过项】`、`【资产声明区】`、`【中文视频提示词】`，禁止英文/中英对照，检查编辑/延长对象误用，检查高强度动作风险提示和防字幕/Logo/水印约束。
- [config] 更新 `video_prompt_policy`，记录多参考素材角色、操作对象规则、必需输出段落和高强度动作风险提示规则。
- [docs] 更新 `docs/flow.md` 的视频提示词阶段说明。

### Reason
- 即梦 / Seedance 2.0 的多参考素材任务中，最容易出错的是把待编辑/待延长视频误写成参考素材。本次更新把“参考类素材”和“操作对象类素材”拆成硬规则。
- 多图片、音频、视频输入会分别锁定不同维度，提示词应只补足未锁定维度，避免重复描述或互相冲突。

### Validation
- 已在本地构建新版 `validate_project.py` 并通过 Python 语法编译检查。

## 2026-07-04 - v1.0.0

### Changed
- [process] 将旧 13 阶段流程重构为 7 阶段即梦画布前置流程：`story_generation` → `art_direction` → `storyboard_director` → `asset_executor` → `asset_prompt_generation` → `storyboard_prompt_generator` → `video_prompt_generator`。
- [outputs] 将本地 run 输出目录改为扁平结构：`outputs/story.md`、`outputs/style_bible.md`、`outputs/storyboard.json`、`outputs/asset_manifest.json`、`outputs/shot_asset_map.json`、`outputs/assets/`、`outputs/storyboards/`、`outputs/video_prompts.md`。
- [skill] 新增 `skills/asset_executor.md`，作为资产清单和分镜资产映射的唯一来源。
- [skill] 新增 `skills/storyboard_prompt_generator.md`，负责把导演分镜转化为分镜参考图生图提示词。
- [skill] 新增 `skills/video_prompt_generator.md`，替代旧 `shot_video_prompt_generator`，支持同场景连续 shot 合并和上一分镜站位锚点规则。
- [skill] 精简 `storyboard_director`，删除资产草表、资产 ID 和音色职责。
- [skill] 精简 `art_direction`，只输出一页以内 `style_bible.md`，删除 `art_direction.json` 产物。
- [skill] 精简角色、场景、道具提示词生成器，改为单对象输入，避免上下文污染。
- [skill] 精简 `image_generation_executor`，只保留 `external_manual` 模式。
- [schema] 简化 `story.schema.json`、`storyboard.schema.json`、`asset_manifest.schema.json`，新增 `shot_asset_map.schema.json` 和 `video_prompt.schema.json`。
- [script] 重写 `validate_project.py`，按新扁平目录和新 schema 校验。
- [script] 更新 `init_local_run.ps1`，只初始化新流程所需目录和文件。
- [cleanup] 删除旧流程节点：分镜独立审查、静态帧变体、音色清单、外部交接、生成媒体审查、连续性审查、最终包构建和旧资产清单构建器。

### Reason
- 新目标是进入即梦画布生产，而不是在仓库内管理完整外部生成回流与最终审查。
- 原流程职责交叉：导演输出资产草表、资产清单阶段承担过多策略、视频提示词逐 shot 文件过重，导致输入冗余、交付路径过长。
- 新流程以最小必要输入、职责单一、流程精简和交付清晰为核心。

### Compatibility
- 旧 local run 与 v1.0.0 不兼容，建议重新执行 `scripts/init_local_run.ps1` 初始化。
- 旧目录 `outputs/01_story`、`outputs/02_art_direction` 等不再作为主流程路径。
- 旧 `CHAR_001`、`ENV_001`、`PROP_001` 资产 ID 不再作为资产主标识；资产名改用“特征 + 状态”。

### Validation
- 已在本地构建新版 `validate_project.py` 并通过 Python 语法编译检查。
- 已解析新版 `checkpoint.template.json` 与新增/修改 schema JSON。

## 2026-06-21 - v0.5.0

### Changed
- [process] 将流程升级为 13 阶段：新增 `image_generation_executor` 与 `generated_media_review`，外部生成结果审查位于交接之后、最终一致性审查之前。
- [schema] 新增 `schemas/`，覆盖故事、艺术方向、分镜、分镜审查、资产清单、音色清单、单 shot 视频提示词、图片结果、视频结果、生成媒体审查、连续性报告和最终包。
- [checkpoint] 升级 `checkpoint.template.json` 到 schema v1.1，加入项目元数据、阶段状态机、阶段顺序、质量门、已知缺口和阻塞问题。

## 2026-06-17 - v0.4.0

### Changed
- [process] 新增 `storyboard_sequence_review` 阶段，放在 `storyboard_director` 之后、`asset_manifest_builder` 之前。
- [skill] 新增 `skills/storyboard_sequence_review.md`，用 1-shot、2-shot、3-shot 滑动窗口检查分镜相邻逻辑。

## 2026-06-14 - v0.3.0

### Changed
- [process] 视频提示词生成改为逐 shot 循环：先生成 `shots/SHOT_XXX.md`，自检后再汇总 `shot_video_prompts.md`。
- [prompt_output_contract] 视频提示词资产声明改为：必 `@SHOT`、必 `@CHAR`、有声才 `@AUDIO`、条件 `@ENV`、默认不 `@PROP`。
