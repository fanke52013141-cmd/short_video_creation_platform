# Skill: storyboard_director
**Version**: 1.2.0

## Source Prompt
`skills/raw_prompts/storyboard_director.source.md`

## Purpose
将已确认故事和视觉风格圣经转译为具备电影语法的分镜序列，并输出分镜级资产草表。

本 Skill 的核心不是把剧本平均切段，而是用镜头讲故事。好的分镜必须通过景别、构图、视角、运动、节奏、转场和画面信息层级，让故事变得更清晰、更有情绪、更有电影表达力。

## Hard Shot Rules

### 1. Shot Duration Limit
- 每个镜头 `duration_seconds` 必须 `> 0` 且 `<= 15`。
- 推荐常规镜头 3-8 秒；情绪停顿或信息读取镜头 8-12 秒；12-15 秒只能用于有明确叙事理由的长停留镜头。
- 不允许输出超过 15 秒的镜头。

### 2. Atomic Shot Boundary Rule
- 一个 shot 必须是一个真实的镜头单位，而不是把同一个连续镜头按时长硬拆成两份。
- 只有发生真实镜头边界时，才可以新建 shot。
- 合法镜头边界包括：景别变化、机位/角度变化、焦段或构图逻辑变化、主体/叙事焦点变化、空间/时间变化、蒙太奇关系变化、反应镜头、插入镜头、信息揭示镜头。
- 如果一个连续动作在同一机位、同一景别、同一空间、同一运动路径中延续，不能拆成两个 shot。
- 如果某个连续镜头预计超过 15 秒，必须重新设计为真正不同的镜头组合，例如切到反应、细节、道具、环境、主观视角或新的机位，而不是简单拆分。

### 3. AI Video Consistency Rule
- 分镜拆分必须考虑后续 AI 视频生成的一致性。
- 不能为了时长把同一场景、同一构图、同一运动中的连续动作拆成多个近似镜头；这会导致 AI 生成时角色、场景、光线和空间锚点漂移。
- 每个 shot 都必须说明 `boundary_reason`，证明它为什么是一个独立镜头。

## Inputs
```json
{
  "story_markdown_path": "./outputs/01_story/story.md",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "shot_count_target": "auto",
  "duration_minutes": "2-5",
  "max_shot_duration_seconds": 15
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

## Schema
`outputs/03_storyboard/storyboard.json` 必须满足 `schemas/storyboard.schema.json`。

## Procedure
1. 读取 `storyboard_director.source.md` 作为主提示词。
2. 读取 `story.md` 和 `style_bible.md`，将 `style_bible.md` 作为上游视觉锁定，不重新发明全片风格。
3. 先建立叙事骨架：明线、暗线、情绪弧线、关键转折、母题资产和节奏意图。
4. 再把故事拆成真正的镜头单位。不得把同一个连续镜头按时长硬拆。
5. 为每个 shot 指定 `duration_seconds`，且不得超过 15 秒。
6. 为每个 shot 写明 `shot_boundary_type` 和 `boundary_reason`。
7. 输出叙事骨架、视觉基调微调、资产草表和分镜序列。
8. 分镜中所有人物、场景、道具必须使用资产 ID 引用。
9. 保存结构化 `storyboard.json`，供资产清单、审查和视频提示词阶段使用。

## Quality Gate
- [ ] 分镜覆盖完整故事，不遗漏关键叙事节点。
- [ ] 每个镜头是独立镜头单位，不是连续镜头硬拆。
- [ ] 每个镜头 `duration_seconds <= 15`。
- [ ] 每个镜头有明确 `shot_boundary_type` 和 `boundary_reason`。
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
- `next_phase.skill`: `storyboard_sequence_review`

## Failure Handling
- 镜头超过 15 秒：必须重设镜头设计，不允许直接拉长。
- 连续镜头被硬拆：合并为一个镜头，或重新设计为真实的反应镜头、插入镜头、视角变化、景别变化或蒙太奇切换。
- 资产 ID 缺失或冲突：先修正分镜资产表，再进入资产清单阶段。
- 镜头数量过多：按叙事功能压缩无意义镜头，不压缩关键叙事转折。
- 风格漂移：返回 `art_direction` 或重跑本 Skill，不能在视频提示词阶段补救。
