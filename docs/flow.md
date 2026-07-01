# Workflow

路径约定：仓库根目录保存流程资产；真实创作在 `local_runs/YYYY-MM-DD/project_slug/` 中执行。下文的 `RUN` 代表这个 active run 目录。

执行边界：CodeX 负责前期文本资产、提示词、分镜、图片生成分支选择、交接清单、生成结果记录和一致性检查。图片生成可以选择外部手动生成或 CodeX 内部生成；视频生成和剪辑默认在外部工具中手动完成。

运行状态：真实项目状态写入 `RUN/checkpoint.json`，阶段状态遵守 `docs/phase_state_machine.md`。核心 JSON 产物必须符合 `docs/schema_contracts.md` 中列出的 schema。

## 0. Initialize Local Run

- Script: `scripts/init_local_run.ps1`
- Output:
  - `RUN/checkpoint.json`
  - `RUN/inputs/idea_brief.md`
  - `RUN/production_status.csv`
  - `RUN/outputs/04_assets/audio/voice_reference_manifest.json`
  - `RUN/outputs/06_external_results/image_result_manifest.json`
  - `RUN/outputs/06_external_results/shot_result_manifest.template.json`

## 1. Idea To Story

- Skill: `story_generation`
- Source prompt: `skills/raw_prompts/story_generation.source.md`
- Input: `RUN/inputs/idea_brief.md`
- Output:
  - `RUN/outputs/01_story/story.md`
  - `RUN/outputs/01_story/story.json`
- Schema: `schemas/story.schema.json`

## 2. Story To Visual Direction

- Skill: `art_direction`
- Source prompt: `skills/raw_prompts/art_direction.source.md`
- Input:
  - `RUN/outputs/01_story/story.md`
  - `RUN/outputs/01_story/story.json`
- Output:
  - `RUN/outputs/02_art_direction/style_bible.md`
  - `RUN/outputs/02_art_direction/art_direction.json`
- Schema: `schemas/art_direction.schema.json`

## 3. Story And Style To Storyboard

- Skill: `storyboard_director`
- Primary source prompt: `skills/raw_prompts/storyboard_director.source.md`
- Optional variant: `skills/raw_prompts/storyboard_static_frame_variant.source.md`
- Input:
  - `RUN/outputs/01_story/story.md`
  - `RUN/outputs/01_story/story.json`
  - `RUN/outputs/02_art_direction/style_bible.md`
  - `RUN/outputs/02_art_direction/art_direction.json`
- Output:
  - `RUN/outputs/03_storyboard/storyboard.md`
  - `RUN/outputs/03_storyboard/storyboard.json`
  - `RUN/outputs/03_storyboard/draft_asset_sheet.json`
- Schema: `schemas/storyboard.schema.json`
- Next phase: `storyboard_sequence_review`

## 4. Storyboard Sequence Review

- Skill: `storyboard_sequence_review`
- Protocol: `docs/storyboard_sequence_review_protocol.md`
- Input:
  - `RUN/outputs/01_story/story.json`
  - `RUN/outputs/02_art_direction/style_bible.md`
  - `RUN/outputs/03_storyboard/storyboard.md`
  - `RUN/outputs/03_storyboard/storyboard.json`
  - `RUN/outputs/03_storyboard/keyframes/*.png` when available
- Output:
  - `RUN/outputs/03_storyboard/storyboard_sequence_review.md`
  - `RUN/outputs/03_storyboard/storyboard_sequence_review.json`
- Schema: `schemas/storyboard_sequence_review.schema.json`
- Rules:
  - 必须检查 1-shot、2-shot、3-shot 滑动窗口。
  - 有未处理 P0 时不能进入资产清单阶段。
  - 有 P1 时必须修正或由用户明确接受风险。

## 5. Storyboard To Canonical Asset Manifest

- Skill: `asset_manifest_builder`
- Input:
  - `RUN/outputs/03_storyboard/storyboard.json`
  - `RUN/outputs/03_storyboard/draft_asset_sheet.json`
  - `RUN/outputs/03_storyboard/storyboard_sequence_review.json`
  - `RUN/outputs/02_art_direction/style_bible.md`
- Output:
  - `RUN/outputs/04_assets/asset_manifest.json`
  - `RUN/outputs/04_assets/asset_manifest.md`
- Schema: `schemas/asset_manifest.schema.json`

## 6. Asset Prompt Generation

- Character Skill: `character_prompt_generator`
- Scene Skill: `scene_prompt_generator`
- Prop Skill: `prop_prompt_generator`
- Prop source prompt: `skills/raw_prompts/prop_prompt_generator.source.md`
- Input:
  - `RUN/outputs/04_assets/asset_manifest.json`
  - `RUN/outputs/02_art_direction/style_bible.md`
- Output:
  - `RUN/outputs/04_assets/characters/*.md`
  - `RUN/outputs/04_assets/characters/*.json`
  - `RUN/outputs/04_assets/scenes/*.md`
  - `RUN/outputs/04_assets/scenes/*.json`
  - `RUN/outputs/04_assets/props/*.md`
  - `RUN/outputs/04_assets/props/*.json`
- Scene prompt rules:
  - 每个 `ENV_XXX` 必须生成 Key Plate 中景图提示词，作为后续视频镜头默认引用图。
  - Scene Sheet 四宫格概览图只在复杂、核心、反复出现、多角度拍摄或有角色移动路径的场景中生成。
  - 四宫格用于场景设计审查和空间布局确认，不作为默认视频引用图。
- Rules:
  - 主要人物的每个状态变体必须按三视图生产。
  - 道具提示词必须生成，尤其是文字类道具和母题道具。
  - 角色、场景、道具所需提示词都完成后，才将 checkpoint 阶段 `asset_prompt_generation` 标记为完成。

## 7. Image Generation Mode And Image Results

- Skill: `image_generation_executor`
- Protocol: `docs/generation_mode_protocol.md`
- Required decision:
  - `external_manual`: 只输出提示词和交接说明，由用户在外部网页端生成图片。
  - `internal_codex`: CodeX 使用同一批图片提示词直接生成图片并保存到本地 run。
- Output:
  - `RUN/outputs/04_assets/final_images/**/*.png` when generated
  - `RUN/outputs/generated_image_index.md` when generated
  - `RUN/outputs/06_external_results/image_result_manifest.json`
- Schema: `schemas/image_result_manifest.schema.json`
- Note:
  - 所有图片和外部生成结果都属于本地 run，不进入仓库。
  - 主要人物三视图缺失时允许草稿继续，但最终包不得标记为 `completed`。
  - 场景图片生成优先生成 `ENV_XXX_KEY_PLATE`；`ENV_XXX_SCENE_SHEET` 只在 `scene_sheet_required=true` 时生成。

## 8. Audio Reference Collection

- Skill: `voice_reference_manifest_builder`
- Protocol: `docs/audio_reference_protocol.md`
- Input:
  - `RUN/outputs/03_storyboard/storyboard.json`
  - `RUN/outputs/04_assets/asset_manifest.json`
  - user-provided audio references when available
- Output:
  - `RUN/outputs/04_assets/audio/voice_reference_manifest.json`
  - `RUN/outputs/04_assets/audio/voice_reference_assets.md`
- Schema: `schemas/voice_reference_manifest.schema.json`
- Rules:
  - 有台词、旁白、录音留言或可听见人声的 shot 必须绑定 `@AUDIO`。
  - 缺少音色参考时，必须向用户索要或标记 `missing`，不得假装最终完成。

## 9. Shot Video Prompt Generation

- Skill: `shot_video_prompt_generator`
- Source prompt: `skills/raw_prompts/seedance_video_prompt.source.md`
- Input:
  - `RUN/outputs/03_storyboard/storyboard.json`
  - `RUN/outputs/03_storyboard/keyframes/*.png` when available
  - `RUN/outputs/04_assets/asset_manifest.json`
  - `RUN/outputs/04_assets/audio/voice_reference_manifest.json`
  - `RUN/outputs/04_assets/**/*.md`
  - optional reference media
- Output:
  - `RUN/outputs/05_video_prompts/shots/SHOT_XXX.md`
  - `RUN/outputs/05_video_prompts/shots/SHOT_XXX.json` when structured prompt output is available
  - `RUN/outputs/05_video_prompts/shot_video_prompt_index.md`
  - `RUN/outputs/05_video_prompts/shot_video_prompts.md`
  - `RUN/outputs/05_video_prompts/video_prompt_asset_reference.md`
- Schema: `schemas/shot_video_prompt.schema.json`
- Rules:
  - 必须逐 shot 循环生成单文件，再汇总总文件。
  - 只输出中文视频提示词。
  - 有人声时必须 `@AUDIO`，无人声时不 `@AUDIO`。
  - `@ENV` 只在镜头运动需要扩展分镜图外空间时使用，并写明原因。
  - 道具只写入画面描述，不 `@PROP`。

## 10. External Generation Handoff

- Skill: `external_generation_handoff`
- Image generation: only included when `generation_modes.image_generation = external_manual`.
- Video generation: manually execute shot prompts in Jimeng / Seedance web or selected video platform.
- Editing: manually assemble clips in Jianying / CapCut.
- Handoff outputs:
  - `RUN/outputs/06_external_results/external_generation_handoff.md`
  - `RUN/outputs/06_external_results/image_result_manifest.json`
  - `RUN/outputs/06_external_results/shot_result_manifest.template.json`
  - `RUN/outputs/06_external_results/edit_notes.md`
- Optional local notes after external execution:
  - `RUN/outputs/06_external_results/external_generation_notes.md`
  - `RUN/outputs/06_external_results/shot_result_manifest.json`

## 11. Generated Media Review

- Skill: `generated_media_review`
- Protocol: `docs/generated_media_review_protocol.md`
- Input:
  - `RUN/outputs/06_external_results/image_result_manifest.json`
  - `RUN/outputs/06_external_results/shot_result_manifest.json`
  - optional external generation notes and local screenshots/videos
- Output:
  - `RUN/outputs/06_external_results/generated_media_review.md`
  - `RUN/outputs/06_external_results/generated_media_review.json`
- Schema: `schemas/generated_media_review.schema.json`
- Rule:
  - 被选为 best take 的镜头不得有未处理 P0。

## 12. Continuity Review

- Review Skill: `continuity_review`
- Input:
  - `RUN/outputs/05_video_prompts/shot_video_prompts.md`
  - `RUN/outputs/06_external_results/generated_media_review.json` when available
  - optional external generation notes
- Output:
  - `RUN/outputs/07_final_delivery/continuity_report.md`
  - `RUN/outputs/07_final_delivery/continuity_report.json`
- Schema: `schemas/continuity_report.schema.json`

## 13. Production Package

- Skill: `production_package_builder`
- Input:
  - `RUN/checkpoint.json`
  - `RUN/outputs/07_final_delivery/continuity_report.md`
  - `RUN/outputs/06_external_results/generated_media_review.md` when available
- Output:
  - `RUN/outputs/07_final_delivery/final_package_manifest.json`
  - `RUN/outputs/07_final_delivery/README.md`
- Schema: `schemas/final_package_manifest.schema.json`
- Status:
  - `completed`
  - `completed_with_known_gaps`
  - `revise_required`
