# Skill: continuity_review
**Version**: 0.5.0

## Purpose
检查故事、视觉风格、分镜、资产提示词、图片结果、音色清单、Seedance 视频提示词和外部生成结果之间的一致性，发现会导致批量视频生成跑偏或最终误判完成的问题。

从 0.5.0 起，本 Skill 必须纳入 `shot_video_prompt_generator` 1.4.0 的 Seedance 任务类型规则，以及图片结果可用性、音色状态和生成结果 task-aware 审查状态。

## Inputs
```json
{
  "story_json_path": "./outputs/01_story/story.json",
  "art_direction_json_path": "./outputs/02_art_direction/art_direction.json",
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "storyboard_sequence_review_json_path": "./outputs/03_storyboard/storyboard_sequence_review.json",
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
  "shot_video_prompts_markdown_path": "./outputs/05_video_prompts/shot_video_prompts.md",
  "single_shot_prompt_dir": "./outputs/05_video_prompts/shots",
  "voice_reference_manifest_path": "./outputs/04_assets/audio/voice_reference_manifest.json",
  "video_prompt_asset_reference_path": "./outputs/05_video_prompts/video_prompt_asset_reference.md",
  "generated_media_review_json_path": "./outputs/06_external_results/generated_media_review.json"
}
```

## Outputs
```json
{
  "continuity_report_path": "./outputs/07_final_delivery/continuity_report.md",
  "continuity_report_json_path": "./outputs/07_final_delivery/continuity_report.json",
  "status": "pass | revise_required"
}
```

## Schema
`outputs/07_final_delivery/continuity_report.json` 必须满足 `schemas/continuity_report.schema.json`。

## Procedure
1. 检查故事核心是否在视觉、分镜和视频提示词中保持。
2. 检查风格圣经是否被所有下游阶段继承。
3. 检查资产 ID 是否完整、唯一、引用正确。
4. 读取 `storyboard_sequence_review.json`，确认早期分镜相邻逻辑审查已执行，`concretization_check_passed=true`，且 P0/P1 已处理。
5. 检查角色外观、场景状态、道具状态是否在镜头间连续。
6. 检查 `image_result_manifest.json`：任何声明为视频参考的图片必须 `used_as_video_reference=true` 且 `status=generated | approved`。
7. 检查每个 shot 是否有独立 `shots/SHOT_XXX.md`，并已汇总到总文件。
8. 检查每个 shot 是否声明 Seedance `task_type`。
9. 检查 `video_edit` 是否使用 `严格编辑 @视频N`。
10. 检查 `video_extend` 是否使用 `向前延长 @视频N` 或 `向后延长 @视频N`。
11. 检查视频提示词是否只输出中文，且每个 shot 都有建议时长和分镜图参考角色。
12. 检查有台词、旁白、录音留言或可听见人声的 shot 是否有 `@AUDIO`，且音色不是最终缺失状态。
13. 检查 `@ENV` 是否只在镜头运动需要空间拓展时出现，并有引用决策说明。
14. 检查视频提示词默认没有 `@PROP`，canonical prop 是否在正文里写出位置、状态、动作关系和可见细节。
15. 检查 Seedance 声音符号：台词 `{}`、环境音 `<>`、配乐 `（背景中播放着...）`、字幕/标题 `【...】`。
16. 读取 `generated_media_review.json`，确认 task-aware 审查已执行且没有未处理 P0。
17. 如果外部生成尚未执行，报告中明确标记为不可最终 `completed`，只可作为草稿交付。
18. 输出问题清单、严重级别、影响镜头和修正建议。

## Quality Gate
- [ ] 没有缺失资产引用。
- [ ] 没有同一角色在不同镜头中无理由变脸、换装或年龄漂移。
- [ ] 没有场景时空状态冲突。
- [ ] 没有道具状态前后矛盾。
- [ ] 没有风格漂移到与 `style_bible.md` 冲突。
- [ ] 分镜序列审查已执行，且 `concretization_check_passed=true`。
- [ ] 每个 shot 都有建议时长和 `@SHOT_XXX_STORYBOARD`。
- [ ] 每个 shot 都有独立单 shot 提示词文件。
- [ ] 每个 shot 都声明 `task_type`。
- [ ] `video_edit` 任务使用 `严格编辑 @视频N`。
- [ ] `video_extend` 任务使用 `向前延长 @视频N` 或 `向后延长 @视频N`。
- [ ] 每个被声明为视频参考图的图片都来自已生成或已批准的图片结果。
- [ ] 有人声的 shot 都有 `@AUDIO`，且最终状态不是 `missing | needed | placeholder`。
- [ ] `@ENV` 使用或不使用都有理由。
- [ ] 视频提示词不包含 `【English Prompt】`。
- [ ] 默认没有 `@PROP`。
- [ ] canonical prop 虽然不 `@`，但已在正文中明确位置、状态、动作关系和可见细节。
- [ ] 如果已执行外部生成结果审查，则 `task_type_review_passed=true` 且没有未处理 P0。
- [ ] 如果外部生成尚未执行，报告中明确标记为不可最终 `completed`，只可作为草稿交付。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `continuity_review`
- `completed_phases`: 追加 `continuity_review`
- `artifacts.continuity_report`: `./outputs/07_final_delivery/continuity_report.md`
- `quality_gates.continuity_seedance_task_type_check_passed`: true
- `quality_gates.continuity_reference_readiness_check_passed`: true
- `next_phase.skill`: `production_package_builder`

## Failure Handling
- P0/P1 问题：必须回到对应上游阶段修正。
- Seedance task_type 缺失或句式错误：返回 `shot_video_prompt_generator`。
- 声明了不可用图片参考：返回图片结果登记或视频提示词阶段修正。
- 外部生成 task-aware 审查未执行：最终不得 `completed`。
- P2 问题：允许记录为生产注意事项。
