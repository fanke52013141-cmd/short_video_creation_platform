# Gap Audit

## 已覆盖能力
- 想法到短片故事：已有源提示词 `story_generation.source.md`。
- 故事到视觉风格系统：已有源提示词 `art_direction.source.md`。
- 故事到分镜与资产草表：已有两个分镜源提示词。
- 角色提示词：已有源提示词 `character_prompt_generator.source.md`。
- 场景/文生图画面描述：已有源提示词 `scene_prompt_generator.source.md`。
- Seedance 视频提示词：已有源提示词 `seedance_video_prompt.source.md`。
- 图片生成分支：已补 `external_manual` / `internal_codex` 协议。
- 视频提示词资产引用：已补分镜图、人物必 `@`，音色和场景条件 `@`，道具默认不 `@PROP` 的规则。
- 视频提示词生成方式：已补逐 shot 循环生成协议。
- 人物资产稳定性：已补主要人物三视图协议。
- 音色参考：已补有声镜头音色参考协议。

## 发现的重复或边界重叠
- 分镜提示词已经输出资产表，但资产表不是最终资产注册表。建议保留分镜资产草表，再由 `asset_manifest_builder` 做规范化。
- 艺术总监提示词与分镜提示词都会输出视觉基调。建议以 `art_direction` 的 `style_bible.md` 为上游锁定版本，分镜中的视觉基调只允许做镜头层面的微调。
- 两个分镜提示词职责接近。建议：
  - `storyboard_director.source.md` 作为主版本，适合视频生产。
  - `storyboard_static_frame_variant.source.md` 作为静态帧或关键帧生产变体。

## 当前缺口
- `asset_manifest_builder`：需要把分镜资产草表转成稳定 JSON 注册表。
- `prop_prompt_generator`：当前没有独立道具提示词专家。MVP 可用场景画面描述 Skill 临时适配道具静物，但建议后续补一个专门道具 Skill。
- `continuity_review`：需要检查故事、风格、资产、分镜、视频提示词之间是否一致。
- `production_package_builder`：需要最终打包目录、清单和版本信息。
- `media_reference_registry`：如果后续使用大量参考图、音频、视频，需要管理素材角色、路径、授权状态和被哪些镜头引用。
- `image_generation_executor`：当前已有 `internal_codex` 分支规则，但还没有独立执行 Skill 包装层；可在多次内部生成稳定后补。
- `media_reference_registry`：后续可统一管理分镜图、人物三视图、音色、动作参考、授权状态和被哪些镜头引用。

## MVP 结论
当前提示词已经足够支撑第一版流程。必须新增的是三个胶水层：
1. `asset_manifest_builder`
2. `voice_reference_manifest_builder`
3. `continuity_review`
4. `external_generation_handoff`
5. `production_package_builder`

不建议在当前阶段实现 `video_generation_executor`。视频生成和剪辑仍然外部手动完成；图片生成允许用户选择 `internal_codex` 或 `external_manual`，但生成媒体都只保存在本地 run。
