# Skill: continuity_review
**Version**: 0.3.0

## Purpose
检查故事、视觉风格、分镜、资产提示词和视频提示词之间的一致性，发现会导致批量视频生成跑偏的问题。

## Inputs
```json
{
  "story_json_path": "./outputs/01_story/story.json",
  "art_direction_json_path": "./outputs/02_art_direction/art_direction.json",
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "storyboard_sequence_review_json_path": "./outputs/03_storyboard/storyboard_sequence_review.json",
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "shot_video_prompts_markdown_path": "./outputs/05_video_prompts/shot_video_prompts.md",
  "single_shot_prompt_dir": "./outputs/05_video_prompts/shots",
  "voice_reference_manifest_path": "./outputs/04_assets/audio/voice_reference_manifest.json",
  "video_prompt_asset_reference_path": "./outputs/05_video_prompts/video_prompt_asset_reference.md"
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

## Procedure
1. 检查故事核心是否在视觉、分镜和视频提示词中保持。
2. 检查风格圣经是否被所有下游阶段继承。
3. 检查资产 ID 是否完整、唯一、引用正确。
4. 读取 `storyboard_sequence_review.json`，确认早期分镜相邻逻辑审查已执行且 P0 已处理。
5. 检查角色外观、场景状态、道具状态是否在镜头间连续。
6. 检查每个 shot 是否有独立 `shots/SHOT_XXX.md`，并已汇总到总文件。
7. 检查视频提示词是否只输出中文，且每个 shot 都有建议时长和分镜图参考角色。
8. 检查有台词、旁白、录音留言或可听见人声的 shot 是否有 `@AUDIO`。
9. 检查 `@ENV` 是否只在镜头运动需要空间拓展时出现，并有引用决策说明。
10. 检查视频提示词默认没有 `@PROP`，道具只作为画面描述出现。
11. 输出问题清单、严重级别、影响镜头和修正建议。

## Quality Gate
- [ ] 没有缺失资产引用。
- [ ] 没有同一角色在不同镜头中无理由变脸、换装或年龄漂移。
- [ ] 没有场景时空状态冲突。
- [ ] 没有道具状态前后矛盾。
- [ ] 没有风格漂移到与 `style_bible.md` 冲突。
- [ ] 分镜序列审查已执行，且没有未处理 P0。
- [ ] 每个 shot 都有建议时长和 `@SHOT_XXX_STORYBOARD`。
- [ ] 每个 shot 都有独立单 shot 提示词文件。
- [ ] 有人声的 shot 都有 `@AUDIO`。
- [ ] `@ENV` 使用或不使用都有理由。
- [ ] 视频提示词不包含 `【English Prompt】`。
- [ ] 默认没有 `@PROP`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `continuity_review`
- `completed_phases`: 追加 `continuity_review`
- `artifacts.continuity_report`: `./outputs/07_final_delivery/continuity_report.md`
- `next_phase.skill`: `production_package_builder`

## Failure Handling
- P0/P1 问题：必须回到对应上游阶段修正。
- P2 问题：允许记录为生产注意事项。
