# Changelog

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
