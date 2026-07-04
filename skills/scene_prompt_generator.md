# Skill: scene_prompt_generator
**Version**: 2.1.0

## Source Prompt
`skills/raw_prompts/scene_prompt_generator.source.md`

## Purpose
为单个 Seedance 场景资产生成场景参考图提示词。

本 Skill 不因为普通光线、时间、天气变化拆分新场景。场景资产以空间结构和环境主体为核心；光影、时段、天气通常由后续提示词文字控制。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "scene_asset_name": "雨夜客厅场景"
}
```

## Outputs
```json
{
  "scene_prompt_path": "./outputs/assets/scenes/雨夜客厅场景.md"
}
```

## Procedure

1. 读取 `story.md` 与 `style_bible.md`。
2. 从 `asset_manifest.json` 中只切出本次场景资产。
3. 继承 `asset_name`、`seedance_label`、`definition_sentence`、`reference_bindings`、`visual_anchors`。
4. 如果已有场景参考图，优先绑定现有素材，只补充空间用途和拍摄需求。
5. 如果缺少场景参考图，输出一个场景 Key Plate 图片提示词。
6. 不因为白天/夜晚、冷光/暖光、晴天/阴天、雨夜/清晨等普通光影变化拆新场景。
7. 只有空间结构、建筑布局、地点或叙事空间发生实质变化时，才由 `asset_executor` 新建场景资产。

## Quality Gate

- [ ] 一次只处理一个场景。
- [ ] 场景名称概括环境，不使用复杂编码或 `ENV_001`。
- [ ] 没有因为普通光线、时间、天气变化拆新场景。
- [ ] 场景提示词是单一场景参考图，不是拼贴、分屏或四宫格。
- [ ] 空间结构、入口/出口、可拍摄路径和尺度锚点明确。
- [ ] 与 `style_bible.md` 和分镜用途一致。
- [ ] 不使用真实艺术家、摄影师、建筑师、设计师姓名。
- [ ] 不使用模型专属语法。

## Checkpoint Update
完成某场景后更新：
- `artifacts.assets.scenes.{asset_name}`: `./outputs/assets/scenes/{asset_name}.md`

全部场景完成后，`asset_prompt_generation` 的场景分支可标记完成。

## Failure Handling

- 场景因光线变化被拆分：返回 `asset_executor` 合并为同一场景资产。
- 场景定义过抽象：返回 `asset_executor` 补充空间结构、尺度锚点或使用方式。
- 场景空间不支持分镜用途：返回 `storyboard_director` 或 `asset_executor` 修正。
- 输出成多个场景：拆回单个场景资产提示词。
