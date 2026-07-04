# Skill: character_prompt_generator
**Version**: 2.0.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
为单个角色的全部状态生成即梦图片资产提示词。

一次只处理一个角色，不混入其他角色信息。角色状态拆分只来自 `asset_manifest.json`，本阶段不得新增、合并或重命名资产。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "character_base_name": "少女",
  "character_assets": [
    "少女_默然_正面",
    "少女_哭泣_侧面"
  ]
}
```

## Outputs
```json
{
  "character_prompt_paths": [
    "./outputs/assets/characters/少女_默然_正面.md",
    "./outputs/assets/characters/少女_哭泣_侧面.md"
  ]
}
```

## Procedure
1. 读取 `story.md`。
2. 从 `asset_manifest.json` 中只切出本次角色的全部状态资产。
3. 不读取其他角色的外貌、服装或状态，避免信息污染。
4. 为每个角色状态输出一个中文图片生成提示词。
5. 每条提示词必须包含：角色身份锚点、外貌特征、服装/状态、角度、画面背景要求、禁止项。
6. 文件名必须与 `asset_name` 一致。

## Quality Gate
- [ ] 一次只处理一个角色。
- [ ] 没有混入其他角色信息。
- [ ] 不新增 `asset_manifest.json` 中不存在的角色状态。
- [ ] 每个提示词可以直接复制到即梦生成角色资产图。
- [ ] 同一角色不同状态保留稳定身份锚点。
- [ ] 不使用真实艺术家姓名。
- [ ] 不使用模型专属语法：无 `--ar`、无权重括号、无 EasyNegative。

## Checkpoint Update
完成某角色后更新：
- `artifacts.assets.characters.{asset_name}`: `./outputs/assets/characters/{asset_name}.md`

全部角色完成后，`asset_prompt_generation` 的角色分支可标记完成。

## Failure Handling
- 角色状态缺少稳定身份锚点：返回 `asset_executor` 补充资产信息。
- 发现应该拆分但未拆分的状态：返回 `asset_executor`，不得在本阶段临时拆分。
- 提示词混入其他角色：删除混入信息并重写。
