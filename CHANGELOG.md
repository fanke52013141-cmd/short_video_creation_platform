# Changelog

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
