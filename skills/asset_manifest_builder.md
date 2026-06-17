# Skill: asset_manifest_builder
**Version**: 0.2.0

## Purpose
把分镜输出的资产草表规范化为唯一资产注册表，作为角色、场景、道具和视频提示词阶段的共同数据源。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "draft_asset_sheet_path": "./outputs/03_storyboard/draft_asset_sheet.json",
  "storyboard_sequence_review_json_path": "./outputs/03_storyboard/storyboard_sequence_review.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md"
}
```

## Outputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "asset_manifest_markdown_path": "./outputs/04_assets/asset_manifest.md"
}
```

## Procedure
1. 读取分镜中的人物、场景、道具、音频资产。
2. 读取 `storyboard_sequence_review.json`；如存在 P0 问题，停止进入资产注册表生成。
3. 去重并统一 ID：`CHAR_001`、`ENV_001`、`PROP_001`、`AUDIO_001`。
4. 保留状态变体：A/B/C。
5. 将 P1/P2 连续性风险写入对应资产备注，例如“座机只能出现在墙边小柜，不进入餐桌构图”。
6. 为每个资产记录出现镜头、叙事功能、母题标记、视觉依赖和后续生成状态。
7. 输出 JSON 注册表和人类可读 Markdown。

## Quality Gate
- [ ] 所有分镜引用资产都存在于 `asset_manifest.json`。
- [ ] 没有重复 ID。
- [ ] 没有同一资产被拆成多个无必要 ID。
- [ ] 状态变体有清晰触发条件。
- [ ] 母题资产标记与叙事骨架一致。
- [ ] `storyboard_sequence_review.json` 中没有未处理 P0。
- [ ] P1/P2 连续性注意事项已写入相关资产备注或后续生产注意。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `asset_manifest_builder`
- `completed_phases`: 追加 `asset_manifest_builder`
- `artifacts.asset_manifest`: `./outputs/04_assets/asset_manifest.json`
- `next_phase.skill`: `character_prompt_generator | scene_prompt_generator | prop_prompt_generator`

## Failure Handling
- 引用不存在：返回分镜阶段修正。
- ID 冲突：在资产清单阶段统一重编号，并生成映射表。
- 状态变体过细：合并只影响动作、不影响外观连续性的变体。
