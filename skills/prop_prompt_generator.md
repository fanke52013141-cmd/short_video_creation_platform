# Skill: prop_prompt_generator
**Version**: 2.2.0

## Source Prompt
`skills/raw_prompts/prop_prompt_generator.source.md`

## Purpose
为确实需要独立生成的核心剧情道具生成单物体图片提示词，或为正文控制道具输出不生成说明。

它消费 `asset_executor` 产出的单个 `asset_prompt_task`，而不是读取完整剧本或完整资产清单。

普通背景小道具、参考素材自带道具、一次性无叙事功能物件，不在本阶段生成独立资产。它们要么默认沿用参考素材，要么在视频提示词正文中用文字控制。

## Inputs
```json
{
  "asset_prompt_task": {
    "task_id": "PROMPT_PROP_旧皮箱_REFERENCE",
    "parent_asset_name": "旧皮箱",
    "asset_type": "prop",
    "prompt_role": "independent_prop_reference",
    "style_bible_path": "./outputs/style_bible.md",
    "asset_payload": {
      "seedance_label": "旧皮箱",
      "definition_sentence": null,
      "visual_anchors": ["棕色旧皮革", "金属扣", "磨损边角"],
      "generation_brief": "棕色旧皮箱，金属扣，边角磨损，是剧情反复出现的线索道具。",
      "usage_context": "需要多次出现和特写，外形需要稳定。",
      "handling_policy": "generate_independent_prop",
      "prompt_scope": "single_prop_reference"
    },
    "reference_bindings": [],
    "output_prompt_path": "./outputs/assets/props/旧皮箱.md"
  }
}
```

## Minimal Input Boundary

必须输入：

- 当前 `asset_prompt_task`
- `style_bible.md`
- 当前 task 的 `asset_payload`
- 当前 task 的 `reference_bindings`

不得输入：

- 完整 `story.md`
- 完整 `storyboard.json`
- 完整 `shot_asset_map.json`
- 完整 `asset_manifest.json`
- 其他人物、场景或道具任务

## Outputs
```json
{
  "prop_prompt_path": "./outputs/assets/props/旧皮箱.md"
}
```

## Procedure

1. 读取当前 `asset_prompt_task`。
2. 读取 `style_bible.md`，只继承必要的画面风格和 AI 视觉执行要求。
3. 从 `asset_payload` 继承 `seedance_label`、`visual_anchors`、`generation_brief`、`usage_context`、`handling_policy`。
4. 如果 `handling_policy` 是 `inherited_from_reference`，不输出独立道具图提示词，只记录沿用参考素材。
5. 如果 `handling_policy` 是 `text_prompt_control`，不输出独立道具图提示词，只记录后续正文控制方式。
6. 只有 `handling_policy=generate_independent_prop` 且 `prompt_role=independent_prop_reference` 时，输出单一物体图片提示词。
7. 不默认要求视频阶段使用 `@PROP`；道具通常写入视频提示词正文。
8. 不新增 `asset_prompt_task` 中不存在的道具。

## 独立生成条件

只有满足以下至少一项，才建议生成独立道具资产：

- 剧情关键线索。
- 反复出现。
- 需要特写。
- 外形复杂，文字难以稳定控制。
- 状态变化明显且需要连续追踪。
- 用户明确要求道具图。

## Quality Gate

- [ ] 一次只处理一个 `asset_prompt_task`。
- [ ] 没有读取完整 `story.md` 或完整 `asset_manifest.json`。
- [ ] 只为 `handling_policy=generate_independent_prop` 的道具生成独立图片提示词。
- [ ] 没有为普通背景物件强行生成独立道具资产。
- [ ] 参考素材自带道具默认沿用，不重复生成。
- [ ] 新增关键道具以文字控制或独立生成，二者边界清楚。
- [ ] 移除道具时只说明删除目标，不反向描述剩余所有道具。
- [ ] 不默认要求视频阶段使用 `@PROP`。

## Checkpoint Update
完成某 task 后更新：
- `artifacts.assets.props.{task_id}`: `output_prompt_path`

全部道具 task 完成后，`asset_prompt_generation` 的道具分支可标记完成。

## Failure Handling

- 输入不是单个 `asset_prompt_task`：返回 `asset_executor` 重新展开任务。
- 普通道具被要求独立生成：返回 `asset_executor` 改为 `text_prompt_control` 或移出资产清单。
- 道具确实关键但定义不足：返回 `asset_executor` 补充 `generation_brief`、`visual_anchors` 或 `usage_context`。
- 文字策略缺失：返回 `asset_executor` 补充 `handling_policy`。
