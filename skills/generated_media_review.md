# Skill: generated_media_review
**Version**: 0.2.0

## Purpose
审查外部平台或内部工具生成的图片、视频结果是否符合故事、分镜、资产、图片结果、音色参考和 Seedance 视频提示词要求。该 Skill 不重新生成内容，只输出问题清单、严重级别和返修建议。

从 0.2.0 起，本 Skill 必须执行 Seedance task-aware 审查：不仅检查画面是否好看，还要检查外部生成结果是否真正遵守 `pipeline_shot_generation | multimodal_reference | video_edit | video_extend | combined_task` 的任务类型约束。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "shot_video_prompts_markdown_path": "./outputs/05_video_prompts/shot_video_prompts.md",
  "single_shot_prompt_dir": "./outputs/05_video_prompts/shots",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
  "shot_result_manifest_path": "./outputs/06_external_results/shot_result_manifest.json",
  "voice_reference_manifest_path": "./outputs/04_assets/audio/voice_reference_manifest.json",
  "external_generation_notes_path": "./outputs/06_external_results/external_generation_notes.md"
}
```

## Outputs
```json
{
  "generated_media_review_path": "./outputs/06_external_results/generated_media_review.md",
  "generated_media_review_json_path": "./outputs/06_external_results/generated_media_review.json",
  "status": "pass | revise_required | not_executed"
}
```

## Procedure
1. 读取图片结果、视频结果、单 shot 提示词和人工备注。
2. 对照 `asset_manifest.json` 检查角色、场景、道具是否稳定。
3. 对照 `storyboard.json` 和视频提示词检查每个 shot 的动作、运镜、情绪和声音是否执行到位。
4. 读取每个 shot 的 `task_type`，执行任务类型专属审查。
5. 对 `pipeline_shot_generation` 检查分镜图、角色资产、场景条件引用、道具正文描述是否被执行。
6. 对 `multimodal_reference` 检查是否只参考指定维度，未误用参考素材中的其他内容。
7. 对 `video_edit` 检查是否只修改指定区域或主体，未重生成整个视频，未破坏原视频动作、运镜和节奏。
8. 对 `video_extend` 检查人物外观、场景光线、镜头节奏、声音氛围是否连续。
9. 对 `combined_task` 检查参考素材维度与编辑/延长目标是否同时执行。
10. 检查 Seedance 声音符号是否被正确执行：台词、环境音、配乐和字幕/标题。
11. 检查是否误生成字幕、Logo、水印、无关文字或额外人物。
12. 标记角色变脸、服装漂移、道具丢失、场景穿帮、音色缺失、运镜错误、文字错误、任务类型执行错误等问题。
13. 为每个问题标记 `P0`、`P1`、`P2`。
14. 输出可执行返修建议，并更新对应 shot 的后续动作建议。

## Required Checks
- task_type_execution_check：结果是否符合对应 Seedance 任务类型。
- edit_preservation_check：编辑任务是否保留未要求修改的主体、动作、镜头和节奏。
- extend_continuity_check：延长任务是否保持原视频人物、场景、光线、动作节奏和声音连续。
- reference_dimension_check：参考任务是否只参考指定维度。
- dialogue_audio_sync_check：台词、音色、停顿、语速和伴随动作是否对应。
- text_logo_watermark_check：是否误生成字幕、Logo、水印或无关文字。
- selected_take_check：每个进入剪辑的 shot 是否有明确 best_take 或 selected_for_edit。

## Quality Gate
- [ ] 每个已生成的 shot 都被审查。
- [ ] 每个被审查 shot 都能追溯到 `task_type`。
- [ ] `video_edit` 任务没有被整体重生成，也没有破坏原视频保留部分。
- [ ] `video_extend` 任务保持人物、场景、光线、动作节奏和声音连续。
- [ ] `combined_task` 同时执行参考素材维度和编辑/延长目标。
- [ ] 被选为 best take 的镜头没有未处理 P0。
- [ ] P1 问题有修复建议或用户接受说明。
- [ ] 没有把未生成的镜头伪装为通过。
- [ ] 所有外部结果问题能追溯到 shot_id、take_id 或 asset_id。
- [ ] 没有误生成字幕、Logo、水印或无关文字，除非用户明确要求。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `generated_media_review`
- `completed_phases`: 追加 `generated_media_review`
- `artifacts.generated_media_review`: `./outputs/06_external_results/generated_media_review.md`
- `artifacts.generated_media_review_json`: `./outputs/06_external_results/generated_media_review.json`
- `quality_gates.generated_media_task_type_review_passed`: true
- `next_phase.skill`: `continuity_review`

## Failure Handling
- 外部结果尚未生成：输出 `status=not_executed`，不阻塞草稿复盘，但最终打包不得标记 `completed`。
- 发现 P0：返回外部生成或上游提示词阶段返修。
- 发现任务类型执行错误：返回外部生成重新生成，必要时返回视频提示词阶段修正。
- 缺少 manifest：先生成模板并要求用户补填。
