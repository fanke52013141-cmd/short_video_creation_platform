# Skill: character_prompt_generator
**Version**: 2.2.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
为单个 Seedance 人物主体的单个参考角色生成提示词。它消费 `asset_executor` 产出的单个 `asset_prompt_task`，而不是读取完整剧本或完整资产清单。

人物通常会展开为两个独立任务：

1. `face_closeup`: 人脸大头特写图，锁定面部 ID。
2. `full_body_styling`: 全身妆造图，锁定体型、服装、整体造型。

常规喜怒哀乐、站立、坐下、抬手、回头、拿东西等状态，后续由视频提示词文字控制，不在本阶段拆成新人物资产。

## Inputs
```json
{
  "asset_prompt_task": {
    "task_id": "PROMPT_CHARACTER_林小满_FACE",
    "parent_asset_name": "林小满",
    "asset_type": "character",
    "prompt_role": "face_closeup",
    "style_bible_path": "./outputs/style_bible.md",
    "asset_payload": {
      "seedance_label": "林小满",
      "definition_sentence": "将生成的人脸大头特写图和全身妆造图统一定义为林小满。",
      "visual_anchors": ["黑色中长发", "深色针织衫"],
      "generation_brief": "年轻女性林小满，黑色中长发，深色针织衫，气质克制安静。",
      "usage_context": "家庭情绪短片主角。",
      "notes": "常规表情和动作不拆新人物资产"
    },
    "reference_bindings": [],
    "output_prompt_path": "./outputs/assets/characters/林小满_人脸大头特写.md"
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
  "character_prompt_path": "./outputs/assets/characters/林小满_人脸大头特写.md"
}
```

## Procedure

1. 读取当前 `asset_prompt_task`。
2. 读取 `style_bible.md`，只继承画面风格、整体色调、光线风格和 AI 视觉执行要求。
3. 从 `asset_payload` 继承 `seedance_label`、`definition_sentence`、`visual_anchors`、`generation_brief`、`usage_context`。
4. 如果 `reference_bindings` 已有用户素材，优先绑定现有素材，不重新发明人物外观。
5. 如果 `prompt_role=face_closeup`，只输出人脸大头特写图提示词。
6. 如果 `prompt_role=full_body_styling`，只输出全身妆造图提示词。
7. 不为表情、动作、姿态、常规情绪单独生成新人物资产。
8. 不新增 `asset_prompt_task` 中不存在的人物。

## Quality Gate

- [ ] 一次只处理一个 `asset_prompt_task`。
- [ ] 使用稳定人物名，例如 `主体1`、`林小满`、`警察`，不使用 `CHAR_001`。
- [ ] 没有读取完整 `story.md` 或完整 `asset_manifest.json`。
- [ ] 没有因为表情、动作、姿态拆成多个人物资产。
- [ ] 输出与 `prompt_role` 一致：人脸大头特写或全身妆造，只能二选一。
- [ ] 每条提示词可直接用于生成单张人物参考图。
- [ ] 不使用真实艺术家姓名。
- [ ] 不使用模型专属语法：无 `--ar`、无权重括号、无 EasyNegative。

## Checkpoint Update
完成某 task 后更新：
- `artifacts.assets.characters.{task_id}`: `output_prompt_path`

全部角色 task 完成后，`asset_prompt_generation` 的角色分支可标记完成。

## Failure Handling

- 输入不是单个 `asset_prompt_task`：返回 `asset_executor` 重新展开任务。
- task 缺少 `generation_brief`、`visual_anchors` 或稳定命名：返回 `asset_executor` 补充。
- 角色状态被拆成多个资产：返回 `asset_executor` 合并为一个人物主体。
- 提示词混入其他角色：删除混入信息并重写。
