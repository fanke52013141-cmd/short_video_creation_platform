# Skill: character_prompt_generator
**Version**: 1.1.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
为 `asset_manifest.json` 中的角色资产生成可用于图像生成或美术生产的中文角色设计提示词。主要人物的每个状态变体必须输出三视图要求。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "character_id": "CHAR_001"
}
```

## Outputs
```json
{
  "character_prompt_path": "./outputs/04_assets/characters/CHAR_001.md",
  "character_prompt_json_path": "./outputs/04_assets/characters/CHAR_001.json",
  "three_view_output_dir": "./outputs/04_assets/final_images/characters/CHAR_001_A/"
}
```

## Procedure
1. 读取角色源提示词。
2. 读取角色资产信息、状态变体和视觉风格圣经。
3. 对主要人物的每个状态变体分别生成三视图提示词：正视图、侧视图、后视图。
4. 次要或背景人物可生成单图，但必须在输出中标记是否需要三视图。
5. 只输出中文提示词，遵守源提示词约束。

## Quality Gate
- [ ] 角色核心概念一句话清晰。
- [ ] 剪影可辨识。
- [ ] 形状语言、配色、服装、道具服务角色身份。
- [ ] 主要人物每个状态变体都有正视图、侧视图、后视图要求。
- [ ] 同一状态三视图的年龄、服装、发型、体态一致。
- [ ] 不把多个年龄或职业状态放进同一张最终人物资产图。
- [ ] 与 `style_bible.md` 风格一致。
- [ ] 不产生未登记的新角色。

## Checkpoint Update
通过质量门后更新：
- `artifacts.characters.CHAR_001`: `./outputs/04_assets/characters/CHAR_001.md`

## Failure Handling
- 信息不足：按源提示词追问，不强行输出最终提示词。
- 与风格圣经冲突：优先遵守 `style_bible.md`。
