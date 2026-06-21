# Gap Audit

## 已覆盖能力

- 想法到短片故事：已有源提示词 `story_generation.source.md`。
- 故事到视觉风格系统：已有源提示词 `art_direction.source.md`。
- 故事到分镜与资产草表：已有主分镜源提示词和静态帧变体。
- 分镜相邻逻辑审查：已有 `storyboard_sequence_review`，在资产生成前检查 1-shot、2-shot、3-shot 窗口中的空间、道具、人物、时间、声音和母题连续性。
- 角色提示词：已有源提示词 `character_prompt_generator.source.md`，支持主要人物三视图。
- 场景提示词：已有源提示词 `scene_prompt_generator.source.md`。
- 道具提示词：已补 `prop_prompt_generator.source.md`，支持母题道具、文字类道具和状态变体。
- Seedance 视频提示词：已有源提示词 `seedance_video_prompt.source.md`。
- 图片生成分支：已有 `external_manual` / `internal_codex` 协议，并新增 `image_generation_executor` 包装层。
- 视频提示词资产引用：已补分镜图、人物必 `@`，音色和场景条件 `@`，道具默认不 `@PROP` 的规则。
- 视频提示词生成方式：已补逐 shot 循环生成协议。
- 音色参考：已补有声镜头音色参考协议。
- 外部结果记录：已补 `image_result_manifest` 与 `shot_result_manifest` 模板。
- 外部生成结果审查：已补 `generated_media_review` Skill 和协议。
- 结构化契约：已新增 `schemas/` 与 `docs/schema_contracts.md`。
- 状态机：已新增 `docs/phase_state_machine.md`，并升级 `checkpoint.template.json`。
- 阶段式校验：`scripts/validate_project.py` 支持 `--phase`。

## 仍需持续完善的能力

- `asset_manifest_builder` 的实际生成质量仍依赖 Agent 执行，后续可增加更严格的资产合并/拆分规则。
- `image_generation_executor` 目前是流程包装层；真实内部图片生成仍依赖运行环境能力。
- `generated_media_review` 目前以人工记录和 manifest 为主；后续可增强对截图/视频文件的视觉检查。
- `production_package_builder` 已定义更严格状态，但后续可补自动汇总脚本。
- `media_reference_registry` 仍可作为后续增强项，用于统一管理参考图、音频、动作参考、授权状态和被哪些镜头引用。

## 当前 MVP 结论

当前仓库已从“提示词流程骨架”升级为“带状态机、schema、校验、外部结果回流”的生产流程骨架。

仍不建议在当前阶段实现 `video_generation_executor`。视频生成和剪辑继续外部手动完成；仓库负责提示词、资产声明、结果记录、审查和最终交付包。
