# Changelog

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
