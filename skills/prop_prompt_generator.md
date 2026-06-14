# Skill: prop_prompt_generator
**Version**: 0.1.0

## Source Prompt
待补充。MVP 阶段可临时复用 `scene_prompt_generator.source.md` 的物理描述原则，为关键道具生成静物资产描述。

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
1. 读取道具资产定义、状态变体、出现镜头和叙事功能。
2. 描述道具形状、材质、尺度、磨损、颜色、可识别细节和状态变化。
3. 如果道具承担母题，明确其重复出现时应保持不变的视觉锚点。
4. 输出中文自然语言提示词。

## Quality Gate
- [ ] 道具在缩略图和特写中都可辨识。
- [ ] 材质、尺度、颜色和状态变体明确。
- [ ] 没有与角色或场景资产冲突。
- [ ] 母题道具的视觉锚点稳定。

## Checkpoint Update
通过质量门后更新：
- `artifacts.props.PROP_001`: `./outputs/04_assets/props/PROP_001.md`

## Failure Handling
- 缺少独立道具源提示词：标记为 `needs_prompt_source_upgrade`，但不阻塞 MVP。

