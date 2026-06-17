# Storyboard Sequence Review Protocol

分镜序列审查用于在资产生成和视频提示词生成之前，检查相邻镜头之间的逻辑连续性。

它不是重新创作分镜，而是发现会导致穿帮、跳戏、视频生成跑偏的问题，并给出可执行修正建议。

## 触发时机

必须在 `storyboard_director` 之后、`asset_manifest_builder` 之前执行。

推荐顺序：

```text
storyboard_director
storyboard_sequence_review
asset_manifest_builder
asset_prompt_generation
```

如果分镜已生成图片，则在分镜图生成后再执行一次视觉版审查。

## 审查窗口

逐 shot 审查不足以发现连续性问题。必须使用滑动窗口：

- `1-shot`: 检查单镜头内部是否自洽。
- `2-shot`: 检查当前镜头与上一个镜头的直接承接。
- `3-shot`: 检查当前镜头与前后镜头组成的小段落逻辑。
- `sequence`: 检查全片母题、时间线、人物状态和空间规则。

## 必查维度

### 空间连续性

- 同一场景中的物件位置是否突然变化。
- 某个道具是否在没有镜头交代的情况下凭空出现或消失。
- 相邻镜头的景别变化是否合理。
- 固定空间内的门、窗、桌、椅、电话、电视等锚点是否稳定。

### 道具连续性

- 道具状态是否前后矛盾，例如未点燃/已点燃、完整/破损、未拿起/已拿起。
- 关键母题道具是否被误放到错误空间。
- 文本类道具是否需要单独图片资产支持。

### 人物连续性

- 人物年龄、服装、发型、伤痕、情绪状态是否前后合理。
- 人物是否在相邻镜头中无交代地改变位置或姿态。
- 视线方向和动作方向是否接得上。

### 时间与因果

- 镜头顺序是否能解释事件发生先后。
- 电话、门铃、新闻、录像等触发事件是否先出现再产生反应。
- 情绪反应是否有铺垫，不突然跳到结果。

### 声音连续性

- 有电话、旁白、台词、录音、电视新闻时，声音来源是否明确。
- 声音是否从前一镜头自然延续或被切断。
- 有人声镜头是否需要后续 `@AUDIO`。

### 视觉母题

- 空椅子、警号、警帽、旧盒子等母题是否在正确位置、正确状态出现。
- 母题是否被误用成普通装饰，或过度出现在不该出现的镜头里。

## 输出格式

输出到：

```text
outputs/03_storyboard/storyboard_sequence_review.md
outputs/03_storyboard/storyboard_sequence_review.json
```

Markdown 必须包含：

```markdown
# Storyboard Sequence Review

Status: pass | revise_required

## Summary

## P0 必须修正

## P1 建议修正

## P2 生产注意

## Adjacent Window Checks

| Window | Shots | Issue | Severity | Fix |
|---|---|---|---|---|

## Global Continuity Checks
```

JSON 必须包含：

```json
{
  "status": "pass | revise_required",
  "issues": [
    {
      "id": "SEQ_001",
      "severity": "P0 | P1 | P2",
      "shots": ["SHOT_001", "SHOT_002"],
      "category": "space | prop | character | time | sound | motif | style",
      "issue": "",
      "fix": ""
    }
  ]
}
```

## 严重级别

- `P0`: 会造成明显穿帮或因果断裂，必须修正后才能进入资产生成。
- `P1`: 会削弱叙事清晰度或造成生成风险，建议修正。
- `P2`: 可进入生产，但需要在图片/视频提示词中注意。

质量门：

- 有任何 `P0` 时，不能进入 `asset_manifest_builder`。
- 有任何未处理 `P1` 时，必须由用户确认是否接受。
- 只有 `status=pass` 或用户明确接受 P1 风险，才能继续。
