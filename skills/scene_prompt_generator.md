# Skill: scene_prompt_generator
**Version**: 1.1.0

## Source Prompt
`skills/raw_prompts/scene_prompt_generator.source.md`

## Purpose
为 `asset_manifest.json` 中的场景资产生成可复用的中文场景设计提示词。该 Skill 的目标不是生成普通背景图，而是把 `ENV_XXX` 定义成可被后续图片生成、镜头参考和视频提示词阶段稳定引用的空间资产。

场景资产输出分为两类：

1. **Key Plate 中景图提示词**：必需。用于生成单一、干净、可被后续视频镜头引用的主场景参考图。
2. **Scene Sheet 四宫格概览图提示词**：条件生成。用于复杂场景、核心反复出现的场景、存在角色移动路径的场景或多角度拍摄场景的设计审查。

## Scene Reference Policy
- `key_plate_required`: `true` for every scene asset.
- `scene_sheet_required`: `true` only when the scene is complex, recurring, spatially important, has multiple shot angles, or requires character movement through space.
- `reference_priority`: `key_plate` by default.
- 四宫格概览图不得作为后续视频生成的默认引用图，除非明确需要空间布局审查；视频生成优先引用 Key Plate。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "scene_id": "ENV_001",
  "scene_reference_policy": {
    "key_plate_required": true,
    "scene_sheet_required": "auto",
    "reference_priority": "key_plate"
  }
}
```

## Outputs
```json
{
  "scene_prompt_path": "./outputs/04_assets/scenes/ENV_001.md",
  "scene_prompt_json_path": "./outputs/04_assets/scenes/ENV_001.json",
  "key_plate_prompt_field": "key_plate_prompt_cn",
  "scene_sheet_prompt_field": "scene_sheet_prompt_cn"
}
```

## Expected JSON Fields
`ENV_001.json` 应至少包含：

```json
{
  "scene_id": "ENV_001",
  "key_plate_required": true,
  "scene_sheet_required": false,
  "reference_priority": "key_plate",
  "key_plate_prompt_cn": "",
  "scene_sheet_prompt_cn": "",
  "spatial_structure": "",
  "lighting_system": "",
  "material_rules": [],
  "continuity_anchors": [],
  "appears_in_shots": []
}
```

## Procedure
1. 读取 `scene_prompt_generator.source.md`。
2. 读取 `asset_manifest.json` 中指定 `scene_id` 的场景资产、状态变体、出现镜头、连续性备注和叙事功能。
3. 读取 `style_bible.md`，继承上游视觉风格，不重新发明场景风格。
4. 判断场景类型、空间复杂度、是否反复出现、是否存在角色移动路径、是否需要多角度拍摄。
5. 始终生成 `Key Plate 中景图提示词`。
6. 当场景复杂、核心、反复出现、多角度拍摄或空间路径重要时，生成 `Scene Sheet 四宫格概览图提示词`；否则写入空值或 `not_required`，并说明原因。
7. 输出 Markdown 提示词资产和结构化 JSON。

## Quality Gate
- [ ] Key Plate 必须存在，并且是单一正常镜头图，不是拼贴、分屏或四宫格。
- [ ] Scene Sheet 是否需要必须有明确判断。
- [ ] 如果 Scene Sheet 生成，四格必须是同一场景的不同视角，不能变成四个不同场景。
- [ ] 场景有前景、中景、背景三层。
- [ ] 光源有来源、方向、色温、强弱和阴影逻辑。
- [ ] 场景有尺度锚点，例如门、椅子、桌子、台阶、栏杆、人物剪影或可识别道具。
- [ ] 场景有使用痕迹、材质时间感和可拍摄路径，除非用户或资产明确要求全新、无人、极简或抽象。
- [ ] 与 `style_bible.md`、分镜用途和角色资产风格一致。
- [ ] 不出现真实艺术家、摄影师、建筑师、设计师姓名。
- [ ] 不使用模型专属语法：无 `--ar`、无权重括号、无 EasyNegative。

## Checkpoint Update
通过质量门后更新：
- `artifacts.scenes.ENV_001`: `./outputs/04_assets/scenes/ENV_001.md`
- `artifacts.scenes_json.ENV_001`: `./outputs/04_assets/scenes/ENV_001.json`
- `artifacts.scene_reference_policy.ENV_001.key_plate_required`: `true`
- `artifacts.scene_reference_policy.ENV_001.scene_sheet_required`: `true | false`

## Failure Handling
- 场景定义过抽象：返回 `asset_manifest_builder` 补充场景类型、叙事功能、出现镜头或空间用途。
- 与风格圣经冲突：优先遵守 `style_bible.md`，不得在场景阶段重设全片风格。
- 场景空间不支持分镜用途：返回 `asset_manifest_builder` 或 `storyboard_director` 修正空间设定。
- 四宫格概览图被误用为视频引用图：改用 Key Plate 作为默认视频参考。
