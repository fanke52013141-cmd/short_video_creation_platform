# Skill: character_prompt_generator
**Version**: 2.1.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
为单个 Seedance 人物主体生成身份锁定资产组提示词，而不是为表情、动作、姿态拆分多份人物资产。

一个人物主体通常只需要：

1. 人脸大头特写图：锁定面部 ID。
2. 全身妆造图：锁定体型、服装、整体造型。

常规喜怒哀乐、站立、坐下、抬手、回头、拿东西等状态，后续由视频提示词文字控制，不在本阶段拆成新人物资产。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "character_asset_name": "林小满"
}
```

## Outputs
```json
{
  "character_prompt_paths": [
    "./outputs/assets/characters/林小满_人脸大头特写.md",
    "./outputs/assets/characters/林小满_全身妆造.md"
  ]
}
```

## Procedure

1. 读取 `story.md` 与 `style_bible.md`。
2. 从 `asset_manifest.json` 中只切出本次人物主体。
3. 继承 `asset_manifest.json` 中的 `asset_name`、`seedance_label`、`definition_sentence`、`reference_bindings` 和 `visual_anchors`。
4. 如果人物已有足够用户参考素材，输出素材绑定说明和必要补充提示，不重新发明人物外观。
5. 如果人物缺少稳定参考素材，则输出两条图片生成提示词：
   - 人脸大头特写图。
   - 全身妆造图。
6. 不为表情、动作、姿态、常规情绪单独生成新人物资产。
7. 不新增 `asset_manifest.json` 中不存在的人物。

## Quality Gate

- [ ] 一次只处理一个人物主体。
- [ ] 使用稳定人物名，例如 `主体1`、`林小满`、`警察`，不使用 `CHAR_001`。
- [ ] 同一人物的所有参考图绑定到同一个 `asset_name`。
- [ ] 没有因为表情、动作、姿态拆成多个人物资产。
- [ ] 如需生成，输出人脸大头特写图和全身妆造图。
- [ ] 每条提示词可直接用于生成人物参考图。
- [ ] 不使用真实艺术家姓名。
- [ ] 不使用模型专属语法：无 `--ar`、无权重括号、无 EasyNegative。

## Checkpoint Update
完成某人物后更新：
- `artifacts.assets.characters.{asset_name}`: `./outputs/assets/characters/{asset_name}_*.md`

全部角色完成后，`asset_prompt_generation` 的角色分支可标记完成。

## Failure Handling

- 角色状态被拆成多个资产：返回 `asset_executor` 合并为一个人物主体。
- 人物缺少面部 ID 或全身妆造锚点：返回 `asset_executor` 补充 `required_reference_set` 或参考素材缺口。
- 提示词混入其他角色：删除混入信息并重写。
