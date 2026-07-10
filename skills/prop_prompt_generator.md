# Skill: prop_prompt_generator
**Version**: 3.0.0

## Source Prompt
`skills/raw_prompts/prop_prompt_generator.source.md`

## Purpose
根据锁定剧本、风格圣经和单个核心道具资产，生成一份独立道具参考图提示词。

本 Skill 只处理已经由 `asset_executor` 判定为需要独立生成的核心剧情道具。普通道具不进入本 Skill。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_type": "prop",
  "asset_name": "旧皮箱",
  "output_prompt_path": "./outputs/assets/props/prompts/旧皮箱_打开.md"
}
```

## Minimal Input Boundary

必须输入：

- `story.md`：用于理解道具在剧情里的功能、出现方式和象征意义。
- `style_bible.md`：用于继承全片画面风格、色调、光线和 AI 视觉执行要求。
- `asset_type`：必须为 `prop`。
- `asset_name`：资产执行官固定的道具名。
- `output_prompt_path`：本次要写出的提示词位置。

不得输入：

- `task_id`
- `asset_payload`
- 完整任务队列
- 其他人物、场景或道具任务

## Outputs
```json
{
  "prop_prompt_path": "./outputs/assets/props/旧皮箱.md"
}
```

## Procedure

1. 读取 `story.md`，理解 `asset_name` 在剧情里的功能、出现方式和象征意义。
2. 读取 `style_bible.md`，继承必要的画面风格和 AI 视觉执行要求。
3. 输出一张单物体 2x2 参考图提示词：标准三分之四视角、侧面/背面、关键细节、比例或交互视图。
4. 有重要外观状态变化时使用 `物品名_变体名`，禁止添加“状态”二字。
4. 不默认要求视频阶段使用 `@PROP`；道具通常写入视频提示词正文。
5. 不新增 `asset_name` 之外的道具。

## 独立生成条件

只有已经由 `asset_executor` 判定为独立生成的道具，才进入本 Skill。通常满足以下至少一项：

- 剧情关键线索。
- 反复出现。
- 需要特写。
- 外形复杂，文字难以稳定控制。
- 状态变化明显且需要连续追踪。
- 用户明确要求道具图。

## Quality Gate

- [ ] 一次只处理一个道具资产和一个输出位置。
- [ ] 输入只有 `story.md`、`style_bible.md`、`asset_type`、`asset_name`、`output_prompt_path`。
- [ ] 没有 `task_id` 或 `asset_payload`。
- [ ] 没有为普通背景物件强行生成独立道具资产。
- [ ] 输出是单一物体图片提示词。
- [ ] 四格没有改变物品身份、材质、比例或指定变体状态。
- [ ] 不默认要求视频阶段使用 `@PROP`。

## Checkpoint Update
完成某个输出位置后更新：
- `artifacts.assets.props.{asset_name}`: `output_prompt_path`

## Failure Handling

- 输入包含多个资产：拆成单资产调用。
- 输入缺少 `story.md`：停止，因为道具设定需要完整剧情上下文。
- 普通道具被要求独立生成：返回 `asset_executor` 改为 `text_prompt_control` 或移出资产清单。
- 道具确实关键但定义不足：返回 `asset_executor` 补充道具名称或独立生成理由。
