# Skill: prop_prompt_generator
**Version**: 1.0.0

## Source Prompt
`skills/raw_prompts/prop_prompt_generator.source.md`

## Purpose
为 `asset_manifest.json` 中的道具资产生成可复现的中文视觉提示词，尤其是承担母题、剧情转折或镜头特写功能的道具。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "prop_id": "PROP_001"
}
```

## Outputs
```json
{
  "prop_prompt_path": "./outputs/04_assets/props/PROP_001.md",
  "prop_prompt_json_path": "./outputs/04_assets/props/PROP_001.json"
}
```

## Procedure
1. 读取 `prop_prompt_generator.source.md` 作为主提示词。
2. 读取道具资产定义、状态变体、出现镜头和叙事功能。
3. 描述道具形状、材质、尺度、磨损、颜色、可识别细节和状态变化。
4. 如果道具承担母题，明确其重复出现时应保持不变的视觉锚点和 `must_not_change` 元素。
5. 如果是文字类道具，明确要尝试生成的文字和后期修正留白。
6. 输出中文自然语言提示词和结构化 JSON。

## Quality Gate
- [ ] 道具在缩略图和特写中都可辨识。
- [ ] 材质、尺度、颜色和状态变体明确。
- [ ] 没有与角色或场景资产冲突。
- [ ] 母题道具的视觉锚点稳定。
- [ ] 文字类道具有生成文字要求和后期修正空间。
- [ ] 不产生未登记的新道具。

## Checkpoint Update
通过质量门后更新：
- `artifacts.props.PROP_001`: `./outputs/04_assets/props/PROP_001.md`

## Failure Handling
- 资产定义不足：返回 `asset_manifest_builder` 补充道具叙事功能、状态变体或连续性备注。
- 与场景/角色冲突：优先遵守已批准资产清单，不在道具阶段临时新增设定。

