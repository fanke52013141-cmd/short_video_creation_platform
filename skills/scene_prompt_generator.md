# Skill: scene_prompt_generator
**Version**: 3.0.0

## Source Prompt
`skills/raw_prompts/scene_prompt_generator.source.md`

## Purpose
根据锁定剧本、风格圣经和单个场景资产，生成一份场景参考图提示词。

本 Skill 不重新决定场景资产，不改名，不新增场景，不按普通光线、时间、天气变化拆场景。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_type": "scene",
  "asset_name": "雨夜客厅场景",
  "output_prompt_path": "./outputs/assets/scenes/prompts/雨夜客厅场景.md"
}
```

## Minimal Input Boundary

必须输入：

- `story.md`：用于理解场景在剧情里的用途、人物活动方式和空间气质。
- `style_bible.md`：用于继承全片画面风格、色调、光线和 AI 视觉执行要求。
- `asset_type`：必须为 `scene`。
- `asset_name`：资产执行官固定的场景名。
- `output_prompt_path`：本次要写出的提示词位置。

不得输入：

- `task_id`
- `asset_payload`
- 完整任务队列
- 其他人物、场景或道具任务

## Outputs
```json
{
  "scene_prompt_path": "./outputs/assets/scenes/雨夜客厅场景.md"
}
```

## Procedure

1. 读取 `story.md`，理解 `asset_name` 在剧情里的空间用途、人物活动方式和叙事气质。
2. 读取 `style_bible.md`，继承画面风格、整体色调、光线风格和 AI 视觉执行要求。
3. 根据 `asset_name` 和剧情用途，输出一张 2x2 空间参考图提示词：建立全景、人眼高度主拍摄方向、反向/侧向、俯视布局。
4. 四格必须共享完全一致的门窗、固定家具、尺度、通道和空间结构。
4. 不因为白天/夜晚、冷光/暖光、晴天/阴天、雨夜/清晨等普通光影变化拆新场景。
5. 不新增 `asset_name` 之外的场景。

## Quality Gate

- [ ] 一次只处理一个场景资产和一个输出位置。
- [ ] 场景名称概括环境，不使用复杂编码或 `ENV_001`。
- [ ] 输入只有 `story.md`、`style_bible.md`、`asset_type`、`asset_name`、`output_prompt_path`。
- [ ] 没有 `task_id` 或 `asset_payload`。
- [ ] 没有因为普通光线、时间、天气变化拆新场景。
- [ ] 场景提示词是一张单文件四宫格空间参考图，不是四个不同场景。
- [ ] 四格分别覆盖建立全景、主方向、反向/侧向和俯视布局。
- [ ] 空间结构、入口/出口、可拍摄路径和尺度锚点明确。
- [ ] 不使用真实艺术家、摄影师、建筑师、设计师姓名。
- [ ] 不使用模型专属语法。

## Checkpoint Update
完成某个输出位置后更新：
- `artifacts.assets.scenes.{asset_name}`: `output_prompt_path`

## Failure Handling

- 输入包含多个资产：拆成单资产调用。
- 输入缺少 `story.md`：停止，因为场景设定需要完整剧情上下文。
- 场景因光线变化被拆分：返回 `asset_executor` 合并为同一场景资产。
- 输出成多个场景：拆回单个场景资产提示词。
