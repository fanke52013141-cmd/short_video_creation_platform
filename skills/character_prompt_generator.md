# Skill: character_prompt_generator
**Version**: 1.0.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
为 `asset_manifest.json` 中的角色资产生成可用于图像生成或美术生产的中文角色设计提示词。

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
  "character_prompt_json_path": "./outputs/04_assets/characters/CHAR_001.json"
}
```

## Procedure
1. 读取角色源提示词。
2. 读取角色资产信息、状态变体和视觉风格圣经。
3. 生成角色三视图提示词和单人全身立绘提示词。
4. 只输出中文提示词，遵守源提示词约束。

## Quality Gate
- [ ] 角色核心概念一句话清晰。
- [ ] 剪影可辨识。
- [ ] 形状语言、配色、服装、道具服务角色身份。
- [ ] 与 `style_bible.md` 风格一致。
- [ ] 不产生未登记的新角色。

## Checkpoint Update
通过质量门后更新：
- `artifacts.characters.CHAR_001`: `./outputs/04_assets/characters/CHAR_001.md`

## Failure Handling
- 信息不足：按源提示词追问，不强行输出最终提示词。
- 与风格圣经冲突：优先遵守 `style_bible.md`。

