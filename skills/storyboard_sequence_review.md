# Skill: storyboard_sequence_review
**Version**: 0.1.0

## Purpose
在分镜生成后，对全片分镜做相邻镜头逻辑审查，发现穿帮、空间跳变、道具凭空出现、人物状态断裂、声音来源不明和母题误用等问题。

该 Skill 不重写故事，不替代分镜导演，不生成图片。它只输出审查报告和可执行修正建议。

## Inputs
```json
{
  "story_json_path": "./outputs/01_story/story.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "storyboard_markdown_path": "./outputs/03_storyboard/storyboard.md",
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "storyboard_keyframe_dir": "./outputs/03_storyboard/keyframes"
}
```

## Outputs
```json
{
  "storyboard_sequence_review_markdown_path": "./outputs/03_storyboard/storyboard_sequence_review.md",
  "storyboard_sequence_review_json_path": "./outputs/03_storyboard/storyboard_sequence_review.json",
  "status": "pass | revise_required"
}
```

## Procedure
1. 读取 `docs/storyboard_sequence_review_protocol.md`。
2. 读取故事、风格圣经和完整分镜。
3. 建立 shot 顺序表，包含每个 shot 的时长、场景、景别、人物、道具、声音、帧策略和画面提示词。
4. 对每个 shot 做单镜头自洽检查。
5. 用 `SHOT_N-1 + SHOT_N` 做 2-shot 相邻检查。
6. 用 `SHOT_N-1 + SHOT_N + SHOT_N+1` 做 3-shot 小段落检查。
7. 检查全片母题、时间线、人物状态、道具位置和声音来源是否连续。
8. 给每个问题标记 `P0`、`P1` 或 `P2`。
9. 输出 Markdown 审查报告和 JSON 机器可读报告。

## Required Checks
- 空间：相邻镜头是否把同一物件放到不同位置。
- 道具：道具是否凭空出现、消失或状态倒退。
- 人物：年龄、服装、伤痕、情绪、动作方向是否接得上。
- 时间：事件触发和人物反应顺序是否合理。
- 声音：电话、门铃、电视新闻、录像、旁白、台词是否有明确来源。
- 母题：空椅子、警号、警帽、旧盒子等是否位置和功能正确。
- 风格：相邻镜头是否突然跳出风格圣经。

## Quality Gate
- [ ] 每个 shot 都被纳入审查。
- [ ] 每组相邻 2-shot 窗口都被审查。
- [ ] 每组相邻 3-shot 窗口都被审查。
- [ ] 报告中没有未解释的 `P0`。
- [ ] 所有 `P1` 都有明确修正建议或用户接受说明。
- [ ] 发现人声但无音色准备的镜头被标记给后续音色阶段。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `storyboard_sequence_review`
- `completed_phases`: 追加 `storyboard_sequence_review`
- `artifacts.storyboard_sequence_review`: `./outputs/03_storyboard/storyboard_sequence_review.md`
- `artifacts.storyboard_sequence_review_json`: `./outputs/03_storyboard/storyboard_sequence_review.json`
- `next_phase.skill`: `asset_manifest_builder`

## Failure Handling
- P0 问题：停止进入资产清单阶段，回到 `storyboard_director` 或人工修正分镜。
- P1 问题：列出风险并请求用户确认是否修正。
- P2 问题：允许继续，但必须写入后续资产或视频提示词注意事项。
