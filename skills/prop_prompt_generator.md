# Skill: prop_prompt_generator
**Version**: 2.1.0

## Source Prompt
`skills/raw_prompts/prop_prompt_generator.source.md`

## Purpose
为确实需要独立生成的核心剧情道具生成图片提示词。

普通背景小道具、参考素材自带道具、一次性无叙事功能物件，不在本阶段生成独立资产。它们要么默认沿用参考素材，要么在视频提示词正文中用文字控制。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "prop_asset_name": "旧皮箱"
}
```

## Outputs
```json
{
  "prop_prompt_path": "./outputs/assets/props/旧皮箱.md"
}
```

## Procedure

1. 读取 `story.md`。
2. 从 `asset_manifest.json` 中只切出本次道具资产。
3. 检查 `handling_policy` 与 `generation_required`。
4. 如果 `handling_policy` 是 `inherited_from_reference`，不输出独立道具图提示词，只记录沿用参考素材。
5. 如果 `handling_policy` 是 `text_prompt_control`，不输出独立道具图提示词，只记录后续正文控制方式。
6. 只有 `handling_policy=generate_independent_prop` 且 `generation_required=true` 时，输出单一物体图片提示词。
7. 不默认要求视频阶段使用 `@PROP`；道具通常写入视频提示词正文。

## 独立生成条件

只有满足以下至少一项，才建议生成独立道具资产：

- 剧情关键线索。
- 反复出现。
- 需要特写。
- 外形复杂，文字难以稳定控制。
- 状态变化明显且需要连续追踪。
- 用户明确要求道具图。

## Quality Gate

- [ ] 一次只处理一个道具。
- [ ] 只为 `generation_required=true` 且 `handling_policy=generate_independent_prop` 的道具生成独立图片提示词。
- [ ] 没有为普通背景物件强行生成独立道具资产。
- [ ] 参考素材自带道具默认沿用，不重复生成。
- [ ] 新增关键道具以文字控制或独立生成，二者边界清楚。
- [ ] 移除道具时只说明删除目标，不反向描述剩余所有道具。
- [ ] 不默认要求视频阶段使用 `@PROP`。

## Checkpoint Update
完成某道具后更新：
- `artifacts.assets.props.{asset_name}`: `./outputs/assets/props/{asset_name}.md`

全部道具完成后，`asset_prompt_generation` 的道具分支可标记完成。

## Failure Handling

- 普通道具被要求独立生成：返回 `asset_executor` 改为 `text_prompt_control` 或移出资产清单。
- 道具确实关键但定义不足：返回 `asset_executor` 补充状态、视角、生成理由或出现镜头。
- 文字策略缺失：返回 `asset_executor` 补充 `handling_policy`。
