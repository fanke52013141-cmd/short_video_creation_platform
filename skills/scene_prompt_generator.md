# Skill: scene_prompt_generator
**Version**: 2.2.0

## Source Prompt
`skills/raw_prompts/scene_prompt_generator.source.md`

## Purpose
为单个 Seedance 场景资产的单个参考角色生成提示词。它消费 `asset_executor` 产出的单个 `asset_prompt_task`，而不是读取完整剧本或完整资产清单。

本 Skill 不因为普通光线、时间、天气变化拆分新场景。场景资产以空间结构和环境主体为核心；光影、时段、天气通常由后续提示词文字控制。

## Inputs
```json
{
  "asset_prompt_task": {
    "task_id": "PROMPT_SCENE_雨夜客厅场景_REFERENCE",
    "parent_asset_name": "雨夜客厅场景",
    "asset_type": "scene",
    "prompt_role": "scene_reference",
    "style_bible_path": "./outputs/style_bible.md",
    "asset_payload": {
      "seedance_label": "雨夜客厅场景",
      "definition_sentence": "将生成的客厅场景参考图定义为雨夜客厅场景。",
      "visual_anchors": ["沙发", "茶几", "雨窗", "暖黄台灯"],
      "generation_brief": "客厅空间，沙发、茶几、窗户和台灯构成稳定空间结构。",
      "usage_context": "用于中景、近景和手部特写的家庭情绪戏。",
      "notes": "光线变化由后续提示词控制，不拆新场景"
    },
    "reference_bindings": [],
    "output_prompt_path": "./outputs/assets/scenes/雨夜客厅场景.md"
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
  "scene_prompt_path": "./outputs/assets/scenes/雨夜客厅场景.md"
}
```

## Procedure

1. 读取当前 `asset_prompt_task`。
2. 读取 `style_bible.md`，只继承画面风格、整体色调、光线风格和 AI 视觉执行要求。
3. 从 `asset_payload` 继承 `seedance_label`、`definition_sentence`、`visual_anchors`、`generation_brief`、`usage_context`。
4. 如果 `reference_bindings` 已有场景参考图，优先绑定现有素材，只补充空间用途和拍摄需求。
5. 如果缺少场景参考图，输出一个场景 Key Plate 图片提示词。
6. 不因为白天/夜晚、冷光/暖光、晴天/阴天、雨夜/清晨等普通光影变化拆新场景。
7. 不新增 `asset_prompt_task` 中不存在的场景。

## Quality Gate

- [ ] 一次只处理一个 `asset_prompt_task`。
- [ ] 场景名称概括环境，不使用复杂编码或 `ENV_001`。
- [ ] 没有读取完整 `story.md` 或完整 `asset_manifest.json`。
- [ ] 没有因为普通光线、时间、天气变化拆新场景。
- [ ] 场景提示词是单一场景参考图，不是拼贴、分屏或四宫格。
- [ ] 空间结构、入口/出口、可拍摄路径和尺度锚点明确。
- [ ] 与 `style_bible.md` 和 `asset_payload.usage_context` 一致。
- [ ] 不使用真实艺术家、摄影师、建筑师、设计师姓名。
- [ ] 不使用模型专属语法。

## Checkpoint Update
完成某 task 后更新：
- `artifacts.assets.scenes.{task_id}`: `output_prompt_path`

全部场景 task 完成后，`asset_prompt_generation` 的场景分支可标记完成。

## Failure Handling

- 输入不是单个 `asset_prompt_task`：返回 `asset_executor` 重新展开任务。
- task 缺少 `generation_brief`、`visual_anchors` 或稳定场景名：返回 `asset_executor` 补充。
- 场景因光线变化被拆分：返回 `asset_executor` 合并为同一场景资产。
- 输出成多个场景：拆回单个场景资产提示词。
