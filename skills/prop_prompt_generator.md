# Skill: prop_prompt_generator
**Version**: 1.1.0

## Source Prompt
`skills/raw_prompts/prop_prompt_generator.source.md`

## Purpose
为 `asset_manifest.json` 中已登记且 `generation_required=true` 的 canonical 道具资产生成可复现的中文视觉提示词。

本 Skill 不决定哪些道具需要做出来。道具是否进入 `PROP_XXX`、是否需要生成、是否有状态变体，只由 `asset_manifest_builder` 决定。

普通一次性物件、无叙事功能的背景陈设、只在单个镜头中出现且没有状态变化的物件，不应在本阶段生成道具资产图；它们应保留在分镜提示词、场景提示词或单镜头视频提示词中。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "prop_id": "PROP_001",
  "variant_id": "PROP_001_A"
}
```

`variant_id` 可省略。省略时，遍历该道具所有 `generation_required=true` 的状态变体；如果没有状态变体，则为道具母体生成提示词。

## Outputs
```json
{
  "prop_prompt_path": "./outputs/04_assets/props/PROP_001.md",
  "prop_prompt_json_path": "./outputs/04_assets/props/PROP_001.json",
  "variant_prompt_paths": [
    "./outputs/04_assets/props/PROP_001_A.md",
    "./outputs/04_assets/props/PROP_001_B.md"
  ]
}
```

## Required Prop Input
每个需要生成的道具应从 `asset_manifest.json` 读取：

```json
{
  "id": "PROP_001",
  "type": "prop",
  "name": "旧怀表",
  "prop_category": "motif_prop",
  "asset_tier": "canonical_prop",
  "generation_required": true,
  "detail_prompt_required": true,
  "reason_to_generate": ["repeated_appearance", "story_motif", "close_up"],
  "appears_in_shots": ["SHOT_003", "SHOT_009"],
  "narrative_function": "连接父亲记忆的母题道具",
  "must_not_change": ["银色外壳", "表盖右下角裂痕", "表链缺一节"],
  "variants": []
}
```

## Generation Policy
- 只为 `asset_tier=canonical_prop` 且 `generation_required=true` 的道具生成提示词。
- `asset_tier=scene_dressing` 的物件应进入场景提示词，不生成独立道具图。
- `asset_tier=shot_description_only` 的物件应进入分镜或视频提示词，不生成独立道具图。
- 若一个道具只出现一次、没有叙事功能、没有状态变化、没有特写需求，则不得强行生成独立道具资产。

## Procedure
1. 读取 `prop_prompt_generator.source.md` 作为主提示词。
2. 读取 `asset_manifest.json` 中指定道具的 `prop_category`、`asset_tier`、`generation_required`、`reason_to_generate`、`must_not_change`、状态变体、出现镜头和叙事功能。
3. 如果道具不是 `canonical_prop` 或 `generation_required` 不是 true，输出“不生成独立道具资产”的原因，不生成最终图像提示词。
4. 描述道具形状、材质、尺度、磨损、颜色、可识别细节、状态变化和稳定视觉锚点。
5. 如果道具承担母题或反复出现，明确其重复出现时必须保持不变的 `must_not_change` 元素。
6. 如果道具有状态变体，分别为每个 `generation_required=true` 的 `PROP_XXX_A/B/C` 生成提示词。
7. 如果是文字类道具，明确 `text_content`、`text_visibility`、`text_generation_strategy` 和是否需要后期修正留白。
8. 输出中文自然语言提示词和结构化 JSON。

## Prompt Outputs
需要生成的道具至少输出：

1. **道具标准资产图提示词**
   - 单一物体。
   - 中性或纯白背景。
   - 清晰展示形状、材质、颜色、尺寸、磨损、标志细节。
   - 用于建立道具稳定外观。

2. **道具细节 / 特写提示词**
   - 仅当 `detail_prompt_required=true` 时输出。
   - 用于特写镜头、母题道具、文字道具、状态变化道具。

## Quality Gate
- [ ] 只处理 `asset_manifest.json` 已登记的 `PROP_XXX`。
- [ ] 只为 `generation_required=true` 的 canonical prop 生成提示词。
- [ ] 没有为一次性普通背景物件生成独立道具资产。
- [ ] 道具在缩略图和特写中都可辨识。
- [ ] 材质、尺度、颜色、状态变体明确。
- [ ] `reason_to_generate` 明确说明为什么要做这个道具。
- [ ] `must_not_change` 明确说明跨镜头稳定视觉锚点。
- [ ] 母题道具的视觉锚点稳定。
- [ ] 文字类道具有文字内容、可读性策略和后期修正空间。
- [ ] 没有与角色或场景资产冲突。
- [ ] 不产生未登记的新道具。
- [ ] 不默认要求视频阶段使用 `@PROP`；视频阶段默认只在正文描述道具。

## Checkpoint Update
通过质量门后更新：
- `artifacts.props.PROP_001`: `./outputs/04_assets/props/PROP_001.md`
- `artifacts.prop_prompt_json.PROP_001`: `./outputs/04_assets/props/PROP_001.json`
- `artifacts.prop_variants.PROP_001_A`: `./outputs/04_assets/props/PROP_001_A.md`

## Failure Handling
- 资产定义不足：返回 `asset_manifest_builder` 补充道具叙事功能、状态变体、生成理由、连续性备注或文字策略。
- 道具不应生成：返回 `asset_manifest_builder` 将其改为 `scene_dressing` 或 `shot_description_only`，并从 `prop_ids` 中移除。
- 与场景/角色冲突：优先遵守已批准资产清单，不在道具阶段临时新增设定。
- 文字道具缺少后期处理策略：返回 `asset_manifest_builder` 补充 `text_generation_strategy`。
