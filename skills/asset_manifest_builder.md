# Skill: asset_manifest_builder
**Version**: 0.4.0

## Purpose
把分镜输出的资产草表规范化为唯一资产注册表，作为角色、场景、道具、音频、图片提示词和视频提示词阶段的共同数据源。

本阶段必须先决定角色资产的状态变体。下游 `character_prompt_generator` 只按本阶段登记的 `CHAR_XXX_A/B/C` 生成角色转面参考图和单人全身立绘，不得在角色提示词阶段临时拆分、合并或新增角色状态。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "draft_asset_sheet_path": "./outputs/03_storyboard/draft_asset_sheet.json",
  "storyboard_sequence_review_json_path": "./outputs/03_storyboard/storyboard_sequence_review.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md"
}
```

## Outputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "asset_manifest_markdown_path": "./outputs/04_assets/asset_manifest.md"
}
```

## Schema
`outputs/04_assets/asset_manifest.json` 必须满足 `schemas/asset_manifest.schema.json`。

## Character Identity Model
角色资产分为两层：

- `CHAR_001`: 同一角色的身份母体。
- `CHAR_001_A / CHAR_001_B / CHAR_001_C`: 同一角色在不同持续性视觉状态下的可生成资产变体。

`CHAR_001` 必须记录身份锚点，`CHAR_001_A/B/C` 必须记录视觉状态变化、触发条件、出现镜头、是否需要生成、是否需要三视图、必须保持不变的身份锚点。

## Character Variant Split Policy

### Must Split Into Separate Character Variants
以下变化必须创建独立角色状态变体：

1. **明显年龄阶段变化**
   - 儿童、少年、青年、中年、老年等影响脸型、体态、发型、皱纹、身高比例或气质的变化。

2. **完整服装变化**
   - 日常服到制服、校服到礼服、普通衣服到战斗装备、现代服装到古装、外套/裙装/盔甲/防护服整体变化。

3. **职业或身份装束变化**
   - 学生、医生、警察、士兵、演员、祭司、婚礼状态、工作制服、戏服、伪装身份等。

4. **持续性脏污、湿透、血迹或破损**
   - 大面积泥污、雨水浸透、烧焦、衣服撕裂、明显血迹、战损状态等，只要跨多个镜头持续出现，必须拆分。

5. **可见且持续的伤痕或身体状态变化**
   - 刀伤、枪伤、烧伤、绷带、旧疤、新鲜血痕、眼罩、断肢、机械义肢、怪物化、机械化、变异状态。

6. **明显发型、发色、妆容或体态变化**
   - 长发到短发、黑发到白发、素颜到浓妆、正常体态到严重消瘦或强壮、普通人到非人形状态。

7. **剧情转折后的新视觉身份**
   - 角色经历事件后，其外观成为新的稳定叙事状态，例如逃亡状态、战后状态、仪式状态、伪装状态、重生状态。

### Do Not Split Into Character Variants
以下变化通常不创建新角色状态变体：

- 表情变化：笑、哭、皱眉、惊讶、愤怒、恐惧。
- 动作变化：站立、奔跑、坐下、回头、伸手、弯腰。
- 镜头变化：近景、远景、侧面、背影、俯视、仰视。
- 光线变化：冷光、暖光、逆光、阴影遮挡。
- 单镜头短暂状态：汗水、轻微灰尘、短暂凌乱、瞬间小伤。
- 临时持有道具：拿杯子、拿手机、拿刀、拿书；道具应归 `PROP_XXX`，不是角色状态。
- 只影响姿态或构图、不影响角色可持续视觉身份的变化。

### Borderline Rule
若不确定是否拆分，使用以下判断：

> 这个变化是否需要 AI 在多个镜头中稳定记住？

如果答案是“是”，创建角色状态变体。
如果只是一帧、一镜、一个表情或一个动作，写入对应 shot 的画面提示词，不创建角色状态变体。

## Required Character Variant Fields
每个角色状态变体至少包含：

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

## Appearance Change Types
`appearance_change_type` 使用以下枚举值或语义等价值：

- `base_wardrobe`
- `wardrobe_change`
- `age_change`
- `identity_uniform`
- `dirty_clothes`
- `wet_clothes`
- `damaged_wardrobe`
- `blood`
- `visible_wound`
- `scar`
- `bandage`
- `hair_change`
- `makeup_change`
- `body_shape_change`
- `nonhuman_transformation`
- `mechanical_transformation`
- `disguise`
- `ritual_state`
- `post_event_state`
- `other_persistent_visual_change`

## Procedure
1. 读取分镜中的人物、场景、道具、音频资产。
2. 读取 `storyboard_sequence_review.json`；如存在未处理 P0 或 P1，停止进入资产注册表生成。
3. 去重并统一 ID：`CHAR_001`、`ENV_001`、`PROP_001`、`AUDIO_001`。
4. 对每个角色建立身份母体 `CHAR_XXX`，记录 `identity_anchors`、叙事功能和出现镜头。
5. 扫描分镜中每个角色的年龄、服装、身份装束、脏污、血迹、伤痕、发型、体态、变异和剧情转折后外观。
6. 根据 Character Variant Split Policy 创建 `CHAR_XXX_A/B/C` 状态变体。
7. 为每个角色变体记录 `trigger`、`appearance_change_type`、`visual_changes`、`appears_in_shots`、`generation_required`、`three_view_required`、`must_keep`、`must_not_mix_with`。
8. 合并只影响动作、表情、光线、构图或单镜头短暂状态的伪变体。
9. 保留场景、道具、音频的状态变体，但不得与角色状态混用。
10. 将 P1/P2 连续性风险写入对应资产备注，例如“座机只能出现在墙边小柜，不进入餐桌构图”。
11. 为每个资产记录出现镜头、叙事功能、母题标记、视觉依赖和后续生成状态。
12. 输出 JSON 注册表和人类可读 Markdown。

## Quality Gate
- [ ] 所有分镜引用资产都存在于 `asset_manifest.json`。
- [ ] 没有重复 ID。
- [ ] 没有同一资产被拆成多个无必要 ID。
- [ ] 每个主要角色都有 `identity_anchors`。
- [ ] 每个角色状态变体都有 `variant_id`、`trigger`、`appearance_change_type`、`visual_changes` 和 `appears_in_shots`。
- [ ] 必须拆分的角色状态已经拆分：年龄、完整服装、身份装束、持续脏污/血迹/破损、持续伤痕、明显发型/体态/变异。
- [ ] 不应拆分的短暂表情、动作、光线、镜头角度、临时持有道具没有被错误拆成角色状态。
- [ ] `generation_required=true` 的主要角色状态变体必须 `three_view_required=true`。
- [ ] 每个角色状态变体都有 `must_keep` 身份锚点，避免状态变化后生成成另一个人。
- [ ] `must_not_mix_with` 标明不可混用的其他状态。
- [ ] 母题资产标记与叙事骨架一致。
- [ ] `storyboard_sequence_review.json` 中没有未处理 P0。
- [ ] `storyboard_sequence_review.json` 中没有未处理 P1。
- [ ] P1/P2 连续性注意事项已写入相关资产备注或后续生产注意。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `asset_manifest_builder`
- `completed_phases`: 追加 `asset_manifest_builder`
- `artifacts.asset_manifest`: `./outputs/04_assets/asset_manifest.json`
- `artifacts.character_variant_policy`: `enabled`
- `next_phase.skill`: `asset_prompt_generation`

## Failure Handling
- 引用不存在：返回分镜阶段修正。
- ID 冲突：在资产清单阶段统一重编号，并生成映射表。
- 状态变体过细：合并只影响动作、表情、光线、镜头角度或单镜头短暂状态的变体。
- 状态变体过粗：若年龄、完整服装、身份装束、持续伤痕、持续脏污或剧情转折后视觉身份被混在同一变体中，必须拆分。
- 角色身份锚点缺失：返回资产清单补充，不允许进入角色提示词最终生成。
