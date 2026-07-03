# Changelog

## 2026-07-03 - v0.5.1

- 保持原有 13 阶段不变。
- 强化现有分镜 AI 审查：必须覆盖全部镜头和全部相邻镜头。
- 每镜头视频提示词增加上一镜、连续关系、生成策略和首尾状态；连续动作禁止独立生成。
- 视频提示词步骤内部新增 `video_prompt_review.json`，不新增 Skill 或阶段。
- 修复最终清单缺失、连续性报告失败、生成结果审查缺失仍可能通过的问题。
- 新增单一 `build_resource_package.py`，按故事、分镜、人物、场景、道具、音频、提示词和质检报告生成最终目录。

## 2026-06-21 - v0.5.0

### Changed
- [process] 将流程升级为 13 阶段：新增 `image_generation_executor` 与 `generated_media_review`，外部生成结果审查位于交接之后、最终一致性审查之前。
- [schema] 新增 `schemas/`，覆盖故事、艺术方向、分镜、分镜审查、资产清单、音色清单、单 shot 视频提示词、图片结果、视频结果、生成媒体审查、连续性报告和最终包。
- [checkpoint] 升级 `checkpoint.template.json` 到 schema v1.1，加入项目元数据、阶段状态机、阶段顺序、质量门、已知缺口和阻塞问题。
- [script] `init_local_run.ps1` 现在会写入真实 `project_slug`、`created_at`、`run_dir`，并初始化图片/视频外部结果 manifest。
- [check] `validate_project.py` 改为阶段式校验，支持 `--phase initialized|story|art|storyboard|assets|audio|video_prompts|external|media_review|final|all`。
- [skill] 新增 `skills/image_generation_executor.md`，包装内部/外部图片生成结果记录流程。
- [skill] 新增 `skills/generated_media_review.md`，审查外部生成视频/图片结果。
- [skill] 补齐 `skills/raw_prompts/prop_prompt_generator.source.md`，道具提示词不再临时复用场景提示词。
- [template] 新增 `image_result_manifest.template.json` 和 `shot_result_manifest.template.json`。
- [docs] 新增 `phase_state_machine.md`、`schema_contracts.md`、`generated_media_review_protocol.md` 和 `quality_gate_matrix.md`。

### Reason
- 上一轮审核发现流程已经具备创作骨架，但缺少机器契约、状态机、外部结果回流和最终交付硬门槛。
- 如果不把外部生成结果纳入 manifest 和审查，角色变脸、道具丢失、空间穿帮等问题会停留在人工聊天记录里，无法进入最终质量门。
- 如果 checkpoint 只是模板复制，流程阶段顺序和项目真实状态容易失真。

### Compatibility
- 旧 local run 的 `checkpoint.json` 不包含 `phases`、`known_gaps`、`blocking_issues` 等字段，建议重新初始化或手动迁移到 v1.1。
- 旧项目没有 `image_result_manifest.json`、`shot_result_manifest.json` 和 `generated_media_review.json`，最终包不应直接标记为 `completed`。
- 旧 `production_status.csv` 可继续阅读，但建议按新模板升级字段。

### Validation
- 已运行 `python -m py_compile scripts/validate_project.py`。
- 已解析所有 `schemas/*.json`、`templates/*.json` 和 `checkpoint.template.json`。
- 已使用临时 local run 执行初始化脚本。
- 已对临时 local run 执行 `--phase initialized` 与音色清单校验并通过。

## 2026-06-17 - v0.4.0

### Changed
- [process] 新增 `storyboard_sequence_review` 阶段，放在 `storyboard_director` 之后、`asset_manifest_builder` 之前。
- [skill] 新增 `skills/storyboard_sequence_review.md`，用 1-shot、2-shot、3-shot 滑动窗口检查分镜相邻逻辑。
- [check] 新增 `docs/storyboard_sequence_review_protocol.md`，定义空间、道具、人物、时间、声音和母题连续性审查规则。
- [schema] `asset_manifest_builder` 升级到 v0.2.0，读取分镜序列审查结果；有 P0 时不得进入资产注册表生成。
- [check] `validate_project.py` 增加 `storyboard_sequence_review.json` 校验，存在未处理 P0 时失败。
- [template] `production_status.template.csv` 增加分镜连续性状态字段。
- [config] 项目版本升级到 v0.4.0，新增 `require_storyboard_sequence_review_before_assets` 质量门。

### Reason
- 本地创作中出现相邻分镜穿帮：座机在上一镜未建立，却在下一镜凭空进入生日餐桌构图。
- 这类问题如果等到视频提示词阶段才发现，会连带污染资产清单、分镜图和视频提示词。

### Compatibility
- 旧项目需要补 `outputs/03_storyboard/storyboard_sequence_review.md` 与 `.json`，或重新从分镜阶段运行审查。
- 旧 `production_status.csv` 可继续使用，但建议按新模板增加分镜连续性字段。

### Validation
- 已对项目文件做静态检查；该阶段需要在下一个完整 local run 中验证。

## 2026-06-14 - v0.3.0

### Changed
- [process] 视频提示词生成改为逐 shot 循环：先生成 `shots/SHOT_XXX.md`，自检后再汇总 `shot_video_prompts.md`。
- [prompt_output_contract] 视频提示词资产声明改为：必 `@SHOT`、必 `@CHAR`、有声才 `@AUDIO`、条件 `@ENV`、默认不 `@PROP`。
- [prompt_output_contract] `@ENV` 只在镜头运动需要扩展分镜图外空间时使用，并必须写明原因。
- [audio_reference] 新增音色参考协议和 `voice_reference_manifest_builder` Skill；有台词、旁白、留言或人声的 shot 必须绑定音色参考。
- [character_view] 主要人物每个状态变体必须生成三视图：正视图、侧视图、后视图。
- [template] 升级 `production_status.template.csv`，新增音色状态、场景引用决策、单 shot 提示词文件、三视图状态字段。
- [check] 升级 `validate_project.py`，检查单 shot 文件、引用决策、音色、中文-only、无 `@PROP`。
- [config] 升级项目版本到 v0.3.0，并新增 per-shot loop、音色、三视图质量门。

### Reason
- 批量一次性生成视频提示词容易变成静态画面描述，缺少逐镜头动作、声音和引用决策。
- Seedance 支持音频作为声音参考，有台词镜头必须管理音色。
- 人物单张图不足以稳定视频生成中的转身、侧身、背影和多镜头连续性。
- 场景引用不应默认出现，应根据分镜图覆盖范围和镜头运动决定。

### Compatibility
- v0.2.0 的 `shot_video_prompts.md` 可作为草稿，但不满足 v0.3.0 的逐 shot 文件要求。
- 旧项目需要补 `outputs/05_video_prompts/shots/`、`outputs/04_assets/audio/voice_reference_manifest.json` 和升级版 `production_status.csv`。

### Validation
- 已对项目文件做静态检查；v0.3.0 规则需要在下一个新 local run 中完整验证。

## 2026-06-14 - v0.2.0

### Changed
- [process] 增加图片生成双分支：`external_manual` 和 `internal_codex`，进入图片阶段前必须确认模式。
- [skill] `shot_video_prompt_generator` 升级到 v1.1.0，视频提示词统一只输出中文。
- [skill] `external_generation_handoff` 升级到 v0.2.0，按图片生成模式区分交接内容。
- [skill] `continuity_review` 升级到 v0.2.0，检查中文-only、分镜图引用、建议时长和无 `@PROP`。
- [prompt_output_contract] 视频提示词默认声明分镜图、人物和场景；道具只写入正文，不 `@PROP`。
- [prompt_output_contract] 分镜图作为首帧、尾帧或关键帧参考写入逐镜头提示词。
- [check] 增加 `scripts/validate_project.py`，检查 shot 数、建议时长、分镜图引用、中文-only 和无 `@PROP`。
- [config] 更新默认输出语言为中文，并记录图片/视频/剪辑生成模式。
- [template] 新增 `templates/production_status.template.csv`，新 local run 自动复制为 `production_status.csv`。

### Reason
- 真实创作中发现图片生成可能在外部网页端或 CodeX 内部执行，需要明确分支。
- 视频提示词中英双语导致体量过大，实际生产只需要中文。
- 分镜图已生成，应作为首帧、尾帧或关键帧参考进入视频提示词。
- 道具图需要生成用于确认和参考，但不应默认作为视频多参 `@PROP` 输入。

### Compatibility
- 旧项目的视频提示词如含 `【English Prompt】`，需要按 v1.1.0 重新生成或手动删除英文段。
- 旧 checkpoint 可继续使用，但建议补充 `generation_modes` 和 `production_status` 字段。

### Validation
- 使用本地项目 `he-finally-present` 的 25 镜头流程验证了中文-only、分镜图引用、建议时长和无 `@PROP` 规则。

## 2026-06-13 - v0.1.0

### Changed
- [process] 建立 AI 短片从想法到视频提示词的 Skill-Oriented 流程。
- [skill] 接入故事、艺术总监、分镜、角色、场景、Seedance 视频提示词源文件。
- [skill] 增加外部生成交接 Skill，明确 CodeX 不执行图片、视频和剪辑。
- [config] 定义本地 run 目录、Skill 版本、路径和外部服务配置。
- [check] 增加一致性检查清单。
- [repo] 增加仓库边界、迭代协议和 `.gitignore`。

### Reason
- 将经过优化的提示词从单次对话使用，升级为可复用、可迁移、可迭代的项目流程。

### Compatibility
- 初始版本，无历史兼容负担。

### Validation
- 已检查 `config/config.yaml` 中声明的原始提示词源文件均存在。
