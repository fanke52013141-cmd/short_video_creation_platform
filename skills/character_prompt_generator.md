# Skill: character_prompt_generator
**Version**: 2.3.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
根据锁定剧本、风格圣经和单个人物资产，生成一份人物参考图提示词。

本 Skill 不重新决定人物资产，不改名，不新增人物，不按表情、动作、姿态拆资产。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_type": "character",
  "asset_name": "林小满",
  "output_prompt_path": "./outputs/assets/characters/林小满_人脸大头特写.md"
}
```

## Minimal Input Boundary

必须输入：

- `story.md`：用于理解人物在剧情里的身份、性格、情绪基调和叙事功能。
- `style_bible.md`：用于继承全片画面风格、色调、光线和 AI 视觉执行要求。
- `asset_type`：必须为 `character`。
- `asset_name`：资产执行官固定的人物名。
- `output_prompt_path`：本次要写出的提示词位置。

不得输入：

- `task_id`
- `asset_payload`
- 完整任务队列
- 其他人物、场景或道具任务

图片用途由 `output_prompt_path` 的文件名判断，例如：

```text
林小满_人脸大头特写.md
林小满_全身妆造.md
```

## Outputs
```json
{
  "character_prompt_path": "./outputs/assets/characters/林小满_人脸大头特写.md"
}
```

## Procedure

1. 读取 `story.md`，理解 `asset_name` 在剧情里的角色身份、性格、情绪基调和叙事功能。
2. 读取 `style_bible.md`，继承画面风格、整体色调、光线风格和 AI 视觉执行要求。
3. 根据 `asset_name` 和 `output_prompt_path` 判断本次是人脸大头特写还是全身妆造。
4. 如果是人脸大头特写，只写单张面部参考图提示词。
5. 如果是全身妆造，只写单张全身参考图提示词。
6. 不为表情、动作、姿态、常规情绪单独生成新人物资产。
7. 不新增 `asset_name` 之外的人物。

## Quality Gate

- [ ] 一次只处理一个人物资产和一个输出位置。
- [ ] 使用稳定人物名，例如 `主体1`、`林小满`、`警察`，不使用 `CHAR_001`。
- [ ] 输入只有 `story.md`、`style_bible.md`、`asset_type`、`asset_name`、`output_prompt_path`。
- [ ] 没有 `task_id` 或 `asset_payload`。
- [ ] 没有因为表情、动作、姿态拆成多个人物资产。
- [ ] 每份提示词只对应一张人物参考图。
- [ ] 不使用真实艺术家姓名。
- [ ] 不使用模型专属语法：无 `--ar`、无权重括号、无 EasyNegative。

## Checkpoint Update
完成某个输出位置后更新：
- `artifacts.assets.characters.{asset_name}`: `output_prompt_path`

## Failure Handling

- 输入包含多个资产：拆成单资产调用。
- 输入缺少 `story.md`：停止，因为人物设定需要完整剧情上下文。
- 角色状态被拆成多个资产：返回 `asset_executor` 合并为一个人物主体。
- 提示词混入其他角色：删除混入信息并重写。
