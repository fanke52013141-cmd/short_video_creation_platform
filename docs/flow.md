# Workflow

路径约定：仓库根目录保存流程资产；真实创作在 `local_runs/YYYY-MM-DD/project_slug/` 中执行。下文的 `RUN` 代表这个 active run 目录。

执行边界：CodeX 负责前期文本资产、提示词、分镜、图片生成分支选择、交接清单和一致性检查。图片生成可以选择外部手动生成或 CodeX 内部生成；视频生成和剪辑默认在外部工具中手动完成。

## 1. Idea To Story
- Skill: `story_generation`
- Source prompt: `skills/raw_prompts/story_generation.source.md`
- Input: `RUN/inputs/idea_brief.md`
- Output:
  - `RUN/outputs/01_story/story.md`
  - `RUN/outputs/01_story/story.json`

## 2. Story To Visual Direction
- Skill: `art_direction`
- Source prompt: `skills/raw_prompts/art_direction.source.md`
- Input:
  - `RUN/outputs/01_story/story.md`
  - `RUN/outputs/01_story/story.json`
- Output:
  - `RUN/outputs/02_art_direction/style_bible.md`
  - `RUN/outputs/02_art_direction/art_direction.json`

## 3. Story And Style To Storyboard
- Skill: `storyboard_director`
- Primary source prompt: `skills/raw_prompts/storyboard_director.source.md`
- Optional variant: `skills/raw_prompts/storyboard_static_frame_variant.source.md`
- Input:
  - `RUN/outputs/01_story/story.md`
  - `RUN/outputs/02_art_direction/style_bible.md`
- Output:
  - `RUN/outputs/03_storyboard/storyboard.md`
  - `RUN/outputs/03_storyboard/storyboard.json`

## 4. Storyboard To Canonical Asset Manifest
- Skill: `asset_manifest_builder`
- Input:
  - `RUN/outputs/03_storyboard/storyboard.json`
- Output:
  - `RUN/outputs/04_assets/asset_manifest.json`

## 5. Asset Prompt Generation
- Character Skill: `character_prompt_generator`
- Scene Skill: `scene_prompt_generator`
- Prop Skill: `prop_prompt_generator`
- Input:
  - `RUN/outputs/04_assets/asset_manifest.json`
  - `RUN/outputs/02_art_direction/style_bible.md`
- Output:
  - `RUN/outputs/04_assets/characters/*.md`
  - `RUN/outputs/04_assets/scenes/*.md`
  - `RUN/outputs/04_assets/props/*.md`

## 6. Image Generation Mode Selection
- Protocol: `docs/generation_mode_protocol.md`
- Required decision:
  - `external_manual`: 只输出提示词和交接说明，由用户在外部网页端生成图片。
  - `internal_codex`: CodeX 使用同一批图片提示词直接生成图片并保存到本地 run。
- Internal output when selected:
  - `RUN/outputs/04_assets/final_images/characters/*.png`
  - `RUN/outputs/04_assets/final_images/scenes/*.png`
  - `RUN/outputs/04_assets/final_images/props/*.png`
  - `RUN/outputs/generated_image_index.md`
- External output when selected:
  - `RUN/outputs/06_external_results/image_generation_handoff.md`
- Note:
  - 文字类画面仍要生成图片，不因后期叠字困难而跳过。
  - 所有图片和外部生成结果都属于本地 run，不进入仓库。

## 7. Shot Video Prompt Generation
- Skill: `shot_video_prompt_generator`
- Source prompt: `skills/raw_prompts/seedance_video_prompt.source.md`
- Input:
  - `RUN/outputs/03_storyboard/storyboard.json`
  - `RUN/outputs/03_storyboard/keyframes/*.png` when available
  - `RUN/outputs/04_assets/asset_manifest.json`
  - `RUN/outputs/04_assets/**/*.md`
  - optional reference media
- Output:
  - `RUN/outputs/05_video_prompts/shot_video_prompts.md`
  - `RUN/outputs/05_video_prompts/video_prompt_asset_reference.md`
- Rules:
  - 只输出中文视频提示词。
  - 每个 shot 必须包含建议时长。
  - 分镜图作为首帧、尾帧或关键帧参考写入资产声明。
  - 视频提示词默认只 `@` 分镜图、人物、场景；道具只写入画面描述，不 `@PROP`。

## 8. External Generation Handoff
- Skill: `external_generation_handoff`
- Image generation: only included when `generation_modes.image_generation = external_manual`.
- Video generation: manually execute shot prompts in Jimeng / Seedance web or selected video platform.
- Editing: manually assemble clips in Jianying / CapCut.
- Handoff outputs:
  - `RUN/outputs/06_external_results/external_generation_handoff.md`
  - `RUN/outputs/06_external_results/shot_result_manifest.template.json`
  - `RUN/outputs/06_external_results/edit_notes.md`
- Optional local notes after external execution:
  - `RUN/outputs/06_external_results/external_generation_notes.md`
  - `RUN/outputs/06_external_results/shot_result_manifest.json`

## 9. Review And Final Package
- Review Skill: `continuity_review`
- Input:
  - `RUN/outputs/05_video_prompts/shot_video_prompts.md`
  - optional external generation notes
- Final output:
  - `RUN/outputs/07_final_delivery/final_package_manifest.json`
  - `RUN/outputs/07_final_delivery/continuity_report.md`
