# Skill: character_prompt_generator
**Version**: 1.2.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
为 `asset_manifest.json` 中已登记的角色资产和角色状态变体生成可用于图像生成或美术生产的中文角色设计提示词。

本 Skill 不决定角色是否需要拆分状态。角色状态拆分只由 `asset_manifest_builder` 决定。这里必须严格读取 `CHAR_XXX` 与 `CHAR_XXX_A/B/C`，并为每个 `generation_required=true` 的状态变体生成：

1. **角色转面参考图提示词**：面部特写 + 正面全身 + 侧面全身 + 背面全身，用于建立多角度一致性。
2. **单人全身立绘提示词**：用于角色展示和立绘生成。

主要人物的每个 `generation_required=true` 状态变体必须输出转面参考图要求；当 `three_view_required=true` 时不得降级为单图。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "character_id": "CHAR_001",
  "variant_id": "CHAR_001_A"
}
```

`variant_id` 可省略。省略时，必须遍历该角色所有 `generation_required=true` 的状态变体。

## Outputs
```json
{
  "character_prompt_path": "./outputs/04_assets/characters/CHAR_001.md",
  "character_prompt_json_path": "./outputs/04_assets/characters/CHAR_001.json",
  "variant_prompt_paths": [
    "./outputs/04_assets/characters/CHAR_001_A.md",
    "./outputs/04_assets/characters/CHAR_001_B.md"
  ],
  "three_view_output_dir": "./outputs/04_assets/final_images/characters/CHAR_001_A/"
}
```

## Required Character Variant Input
每个要生成的角色状态变体应从 `asset_manifest.json` 读取：

```json
{
  "variant_id": "CHAR_001_A",
  "name": "干净日常状态",
  "trigger": "故事开场至 SHOT_006",
  "appearance_change_type": ["base_wardrobe"],
  "visual_changes": "深灰连帽衫，干净牛仔裤，无明显伤痕",
  "appears_in_shots": ["SHOT_001", "SHOT_002"],
  "generation_required": true,
  "three_view_required": true,
  "must_keep": ["脸型", "左眼下方小痣", "肩颈姿态"],
  "must_not_mix_with": ["CHAR_001_B"]
}
```

## Procedure
1. 读取角色源提示词。
2. 读取 `asset_manifest.json` 中的角色母体 `CHAR_XXX`、`identity_anchors`、状态变体、出现镜头、叙事功能和连续性备注。
3. 读取 `style_bible.md`，继承上游画风领域和视觉系统，不重新发明全片画风。
4. 如果指定 `variant_id`，只为该状态变体生成提示词。
5. 如果未指定 `variant_id`，遍历该角色所有 `generation_required=true` 的状态变体。
6. 对每个状态变体分别生成两个中文提示词：
   - `角色转面参考图`：面部特写 + 正面全身 + 侧面全身 + 背面全身。
   - `单人全身立绘`：单一角色全身像。
7. 两个提示词中的角色核心描述、身份锚点、年龄、脸型、体态、发型、服装、配色、标志性元素必须一致；只允许布局、视角、姿态和光照规格不同。
8. 对不同状态变体，必须保留同一角色的 `must_keep` 身份锚点，同时准确体现 `visual_changes`。
9. 不得把 `must_not_mix_with` 中的状态混入当前提示词。
10. 只输出中文提示词，可在中文提示词中嵌入必要英文标签作为图像模型触发词。

## Quality Gate
- [ ] 角色核心概念一句话清晰。
- [ ] 剪影可辨识。
- [ ] 形状语言、配色、服装、道具服务角色身份。
- [ ] 只处理 `asset_manifest.json` 已登记的角色和状态变体。
- [ ] 不新增未登记角色、年龄阶段、服装、伤痕、道具或状态。
- [ ] 每个 `generation_required=true` 的主要角色状态变体都有角色转面参考图提示词。
- [ ] `three_view_required=true` 的状态变体包含面部特写、正面全身、侧面全身、背面全身。
- [ ] 同一状态转面参考图和全身立绘的年龄、服装、发型、体态、配色、标志性元素一致。
- [ ] 不把多个年龄、职业装束、战损状态、伤痕状态或脏污状态放进同一张最终人物资产图。
- [ ] 不把 `must_not_mix_with` 中的状态混入当前状态。
- [ ] 每个状态变体保留 `must_keep` 身份锚点，避免生成成另一个人。
- [ ] 与 `style_bible.md` 风格一致。
- [ ] 不使用真实艺术家姓名。
- [ ] 不使用模型专属语法：无 `--ar`、无权重括号、无 EasyNegative。

## Checkpoint Update
通过质量门后更新：
- `artifacts.characters.CHAR_001`: `./outputs/04_assets/characters/CHAR_001.md`
- `artifacts.character_variants.CHAR_001_A`: `./outputs/04_assets/characters/CHAR_001_A.md`
- `artifacts.character_variant_prompt_json.CHAR_001_A`: `./outputs/04_assets/characters/CHAR_001_A.json`

## Failure Handling
- 信息不足：返回 `asset_manifest_builder` 补充 `identity_anchors`、状态触发条件、视觉变化或出现镜头，不在本阶段强行发明。
- 与风格圣经冲突：优先遵守 `style_bible.md`。
- 发现应该拆分但未拆分的状态：返回 `asset_manifest_builder`，不得在角色提示词阶段临时拆分。
- 发现状态过细且只影响动作、表情、光线、镜头角度：返回 `asset_manifest_builder` 合并状态。
