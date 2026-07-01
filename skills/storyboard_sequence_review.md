# Skill: storyboard_sequence_review
**Version**: 0.4.0

## Purpose
在分镜生成后，对全片分镜做镜头边界、单镜头时长、相邻镜头逻辑、全片连续性和画面具体化程度审查，发现会导致穿帮、空间跳变、道具凭空出现、人物状态断裂、声音来源不明、母题误用、镜头边界伪拆分、抽象提示词空泛和 AI 视频生成不一致的问题。

该 Skill 不重写故事，不替代分镜导演，不生成图片。它只输出审查报告和可执行修正建议。

## Inputs
```json
{
  "story_json_path": "./outputs/01_story/story.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "storyboard_markdown_path": "./outputs/03_storyboard/storyboard.md",
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "storyboard_keyframe_dir": "./outputs/03_storyboard/keyframes",
  "max_shot_duration_seconds": 15,
  "concretization_translation_required": true
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

## Schema
`outputs/03_storyboard/storyboard_sequence_review.json` 必须满足 `schemas/storyboard_sequence_review.schema.json`。

## Procedure
1. 读取 `docs/storyboard_sequence_review_protocol.md`。
2. 读取故事、风格圣经和完整分镜。
3. 建立 shot 顺序表，包含每个 shot 的时长、场景、景别、人物、道具、声音、帧策略、镜头边界类型、镜头边界理由、画面提示词和四译法证据。
4. 对每个 shot 做单镜头自洽检查。
5. 对每个 shot 做时长检查：`duration_seconds` 必须 `> 0` 且 `<= 15`。
6. 对每个 shot 做镜头边界检查：确认它是独立镜头单位，而不是连续镜头硬拆。
7. 对每个 shot 做四译法检查：确认抽象情绪、氛围、事件和关系已转译为画面证据。
8. 用 `SHOT_N-1 + SHOT_N` 做 2-shot 相邻检查。
9. 用 `SHOT_N-1 + SHOT_N + SHOT_N+1` 做 3-shot 小段落检查。
10. 检查全片母题、时间线、人物状态、道具位置、声音来源和抽象提示词残留是否连续。
11. 给每个问题标记 `P0`、`P1` 或 `P2`。
12. 输出 Markdown 审查报告和 JSON 机器可读报告。

## Required Checks
- 时长：任何 shot 超过 15 秒，标记 `P0`。
- 镜头边界：同一机位、同一景别、同一空间、同一运动路径中的连续动作被硬拆，标记 `P0` 或 `P1`。
- 分镜叙事力：每个 shot 是否有独立叙事功能；如果只是漂亮画面或机械复述剧情，标记 `P1`。
- 四译法：`prompt_cn` 是否把抽象词转译为微表情、动作、光影、声音、环境元素、物体细节、空间距离、视线和身体朝向。
- 抽象词残留：如果出现“疲惫、压抑、紧张、孤独、温馨、神秘、犹豫、亲密、疏离、对峙”等词，但没有对应画面证据，标记 `P1`。
- 关键转折：如果关键转折镜头只有抽象心理或气氛，没有可见证据，标记 `P0` 或 `P1`。
- 空间：相邻镜头是否把同一物件放到不同位置。
- 道具：道具是否凭空出现、消失或状态倒退。
- 人物：年龄、服装、伤痕、情绪、动作方向是否接得上。
- 时间：事件触发和人物反应顺序是否合理。
- 声音：电话、门铃、电视新闻、录像、旁白、台词是否有明确来源。
- 母题：空椅子、警号、警帽、旧盒子等是否位置和功能正确。
- 风格：相邻镜头是否突然跳出风格圣经。

## Severity Rules
- `P0`: 会造成明显穿帮、因果断裂、AI 生成片段无法接续，或违反硬规则。包括：shot 超过 15 秒；连续镜头硬拆；关键人物/场景/道具状态断裂；关键转折镜头只有抽象情绪、没有任何可见画面证据。
- `P1`: 会削弱叙事清晰度、镜头表达力或造成较高生成风险。包括：镜头叙事功能弱、边界理由不足、相邻镜头信息重复、抽象词未充分转译。
- `P2`: 可继续生产，但需要在图片/视频提示词中注意。

## Quality Gate
- [ ] 每个 shot 都被纳入审查。
- [ ] 每个 shot 都完成时长检查。
- [ ] 每个 shot 都完成镜头边界检查。
- [ ] 每个 shot 都完成四译法检查。
- [ ] 每组相邻 2-shot 窗口都被审查。
- [ ] 每组相邻 3-shot 窗口都被审查。
- [ ] 报告中没有未解释的 `P0`。
- [ ] 所有 `P1` 都有明确修正建议或用户接受说明。
- [ ] 每个 P1 在 JSON 中包含 `fix_applied=true`、`accepted_by_user=true` 或等价已解决状态。
- [ ] 发现人声但无音色准备的镜头被标记给后续音色阶段。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `storyboard_sequence_review`
- `completed_phases`: 追加 `storyboard_sequence_review`
- `artifacts.storyboard_sequence_review`: `./outputs/03_storyboard/storyboard_sequence_review.md`
- `artifacts.storyboard_sequence_review_json`: `./outputs/03_storyboard/storyboard_sequence_review.json`
- `artifacts.concretization_translation_review`: `passed`
- `next_phase.skill`: `asset_manifest_builder`

## Failure Handling
- P0 问题：停止进入资产清单阶段，回到 `storyboard_director` 或人工修正分镜。
- 分镜超过 15 秒：必须重设镜头设计，不允许继续。
- 连续镜头硬拆：必须合并或改为真实镜头边界，例如反应镜头、插入镜头、视角变化、景别变化或蒙太奇切换。
- 抽象词未落地：必须回到 `storyboard_director` 重写 `prompt_cn`，补充微表情、动作、光影、声音、物体细节或空间关系。
- P1 问题：列出风险并请求用户确认是否修正。
- P2 问题：允许继续，但必须写入后续资产或视频提示词注意事项。
