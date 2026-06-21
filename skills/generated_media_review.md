# Skill: generated_media_review
**Version**: 0.1.0

## Purpose
审查外部平台或内部工具生成的图片、视频结果是否符合故事、分镜、资产和视频提示词要求。该 Skill 不重新生成内容，只输出问题清单、严重级别和返修建议。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "shot_video_prompts_markdown_path": "./outputs/05_video_prompts/shot_video_prompts.md",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
  "shot_result_manifest_path": "./outputs/06_external_results/shot_result_manifest.json",
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
1. 读取图片结果、视频结果和人工备注。
2. 对照 `asset_manifest.json` 检查角色、场景、道具是否稳定。
3. 对照 `storyboard.json` 和视频提示词检查每个 shot 的动作、运镜、情绪和声音是否执行到位。
4. 标记角色变脸、服装漂移、道具丢失、场景穿帮、音色缺失、运镜错误、文字错误等问题。
5. 为每个问题标记 `P0`、`P1`、`P2`。
6. 输出可执行返修建议，并更新对应 shot 的后续动作建议。

## Quality Gate
- [ ] 每个已生成的 shot 都被审查。
- [ ] 被选为 best take 的镜头没有未处理 P0。
- [ ] P1 问题有修复建议或用户接受说明。
- [ ] 没有把未生成的镜头伪装为通过。
- [ ] 所有外部结果问题能追溯到 shot_id 或 asset_id。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `generated_media_review`
- `completed_phases`: 追加 `generated_media_review`
- `artifacts.generated_media_review`: `./outputs/06_external_results/generated_media_review.md`
- `artifacts.generated_media_review_json`: `./outputs/06_external_results/generated_media_review.json`
- `next_phase.skill`: `continuity_review`

## Failure Handling
- 外部结果尚未生成：输出 `status=not_executed`，不阻塞草稿复盘，但最终打包不得标记 `completed`。
- 发现 P0：返回外部生成或上游提示词阶段返修。
- 缺少 manifest：先生成模板并要求用户补填。
