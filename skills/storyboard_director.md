# Skill: storyboard_director
**Version**: 1.0.0

## Source Prompt
`skills/raw_prompts/storyboard_director.source.md`

## Purpose
将已确认故事和视觉风格圣经转译为具备电影语法的分镜序列，并输出分镜级资产草表。

## Inputs
```json
{
  "story_markdown_path": "./outputs/01_story/story.md",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "shot_count_target": "auto",
  "duration_minutes": "2-5"
}
```

## Outputs
```json
{
  "storyboard_markdown_path": "./outputs/03_storyboard/storyboard.md",
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "draft_asset_sheet_path": "./outputs/03_storyboard/draft_asset_sheet.json"
}
```

## Procedure
1. 读取 `storyboard_director.source.md` 作为主提示词。
2. 将 `style_bible.md` 作为上游视觉锁定，不重新发明全片风格。
3. 输出叙事骨架、视觉基调微调、资产草表和分镜序列。
4. 分镜中所有人物、场景、道具必须使用资产 ID 引用。
5. 保存结构化 `storyboard.json`，供资产清单和视频提示词阶段使用。

## Quality Gate
- [ ] 分镜覆盖完整故事，不遗漏关键叙事节点。
- [ ] 每个镜头有时长、景别、引用资产、叙事功能、帧策略、运镜、转场和画面提示词。
- [ ] 资产 ID 格式稳定：`CHAR_001`、`ENV_001`、`PROP_001`。
- [ ] 母题资产在叙事骨架、资产草表、分镜引用中一致。
- [ ] 没有覆盖或冲突 `style_bible.md` 的核心视觉方向。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `storyboard_director`
- `completed_phases`: 追加 `storyboard_director`
- `artifacts.storyboard_markdown`: `./outputs/03_storyboard/storyboard.md`
- `artifacts.storyboard_json`: `./outputs/03_storyboard/storyboard.json`
- `next_phase.skill`: `asset_manifest_builder`

## Failure Handling
- 资产 ID 缺失或冲突：先修正分镜资产表，再进入资产清单阶段。
- 镜头数量过多：按短片时长压缩镜头。
- 风格漂移：返回 `art_direction` 或重跑本 Skill，不能在视频提示词阶段补救。

