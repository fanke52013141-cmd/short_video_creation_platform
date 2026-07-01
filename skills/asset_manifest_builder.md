# Skill: asset_manifest_builder
**Version**: 0.5.0

## Purpose
把分镜输出的资产草表规范化为唯一资产注册表，作为角色、场景、道具、音频、图片提示词和视频提示词阶段的共同数据源。

本阶段必须决定两类核心资产策略：

1. **角色状态变体策略**：决定哪些角色状态需要成为 `CHAR_XXX_A/B/C`。
2. **道具资产生成策略**：决定哪些道具需要成为独立 `PROP_XXX` 并生成资产图，哪些普通物件只应保留在分镜或场景提示词中。

下游 `character_prompt_generator` 和 `prop_prompt_generator` 只消费本阶段登记的资产，不得临时拆分、合并或新增资产。

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

如果答案是“是”，创建角色状态变体。如果只是一帧、一镜、一个表情或一个动作，写入对应 shot 的画面提示词，不创建角色状态变体。

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

## Prop Asset Registration Policy
道具资产不是画面中所有物体的集合。只有需要跨镜头稳定、承担叙事功能、反复出现、被特写展示、发生状态变化，或承载文字 / 符号 / 母题信息的道具，才创建独立 `PROP_XXX`。

### Prop Categories
道具可分类为：

- `hero_prop`: 关键剧情道具。
- `motif_prop`: 视觉母题或暗线道具。
- `text_prop`: 带关键文字、照片、符号、图案的道具。
- `identity_prop`: 与角色身份绑定或长期携带的道具。
- `functional_prop`: 影响剧情动作的功能性道具。
- `background_prop`: 背景陈设道具，通常不独立生成。
- `temporary_prop`: 一次性临时物件，通常不进入 `PROP_XXX`。

### Must Register As PROP_XXX
满足任一条件，必须创建独立 `PROP_XXX`：

1. **反复出现**：出现 2 次及以上，且需要保持同一外观。
2. **明线或暗线道具**：承担剧情推进、线索、秘密、记忆、承诺、冲突或转折。
3. **视觉母题**：反复出现以串联主题、人物关系或情绪。
4. **角色身份绑定**：角色长期携带或能定义身份的道具，如戒指、项链、武器、录音机、旧照片、怀表。
5. **特写展示**：被镜头特写、插入镜头或关键构图强调。
6. **状态变化**：完整/破损、干净/带血、关闭/打开、干燥/湿透、未燃烧/燃烧、文字清晰/晕开等。
7. **文字、照片、符号、图案**：道具上有需要保持一致或后期处理的可读信息。
8. **造型复杂**：普通文本描述难以在多个镜头中稳定复现。

### Do Not Register As PROP_XXX
满足以下条件的普通物件，通常不创建独立 `PROP_XXX`，只写入分镜提示词、场景提示词或单镜头视频提示词：

- 只出现一次。
- 只是背景陈设。
- 没有叙事功能。
- 没有状态变化。
- 没有特写镜头。
- 不需要跨镜头保持一致。
- 可以直接在分镜提示词中自然描述。

示例：普通水杯、一次性餐具、背景书本、路边垃圾袋、墙角杂物、普通椅子、普通盆栽、模糊广告牌。

### Prop Asset Tiers
- `canonical_prop`: 必须进入 `PROP_XXX`，并在道具提示词阶段生成资产提示词。
- `scene_dressing`: 作为场景陈设写入 `ENV_XXX`，不单独生成道具资产。
- `shot_description_only`: 只写入具体 shot 的画面描述，不进入 `PROP_XXX`。

推荐做法：`scene_dressing` 和 `shot_description_only` 通常不要进入 `prop_ids`，除非为了审计而临时记录。真正进入 `prop_ids` 的应主要是 `canonical_prop`。

## Prop Variant Policy
道具状态只在外观、文字、破损、污渍、开合、发光、功能状态发生持续变化时拆分。

### Must Split Prop Variants
以下变化必须创建 `PROP_XXX_A/B/C`：

- 完整状态 / 破损状态。
- 干净状态 / 带血状态 / 沾泥状态 / 烧焦状态。
- 未打开 / 打开 / 撕开 / 被折叠。
- 文字清晰 / 文字晕开 / 文字被划掉。
- 未点燃 / 点燃 / 熄灭 / 烧剩一半。
- 功能关闭 / 发光 / 故障 / 断裂。
- 剧情转折后持续出现的新外观。

### Do Not Split Prop Variants
以下变化不创建道具状态变体：

- 单镜头角度变化。
- 拿法变化。
- 被遮挡。
- 光线变化。
- 镜头远近变化。
- 临时摆放位置变化，除非位置本身是剧情线索。

## Required Prop Fields
每个独立道具资产至少包含：

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

## Text Prop Policy
文字类道具必须记录：

- `text_content`: 准确文字内容。
- `text_visibility`: `must_be_readable | suggestive_only | not_readable`。
- `text_generation_strategy`: `generate_directly | post_production_overlay | blank_space_for_text`。
- `blank_area_required`: 是否需要留白给后期加字。

重要文字不应完全依赖图像模型直接生成。优先策略是留白或后期叠字。

## Appearance Change Types
角色 `appearance_change_type` 可使用：

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

道具状态变体可使用 `visual_changes` 自然语言描述，也可在 `appearance_change_type` 中使用语义等价短语。

## Procedure
1. 读取分镜中的人物、场景、道具、音频资产。
2. 读取 `storyboard_sequence_review.json`；如存在未处理 P0 或 P1，停止进入资产注册表生成。
3. 去重并统一 ID：`CHAR_001`、`ENV_001`、`PROP_001`、`AUDIO_001`。
4. 对每个角色建立身份母体 `CHAR_XXX`，记录 `identity_anchors`、叙事功能和出现镜头。
5. 根据 Character Variant Split Policy 创建 `CHAR_XXX_A/B/C` 状态变体。
6. 扫描分镜中的道具候选项，判断其是否满足 Prop Asset Registration Policy。
7. 只将 `canonical_prop` 注册为独立 `PROP_XXX`。普通一次性物件应从 `prop_ids` 中移除，转写进对应 shot 或场景描述。
8. 为每个 `PROP_XXX` 记录 `prop_category`、`asset_tier`、`generation_required`、`reason_to_generate`、`must_not_change`、`detail_prompt_required`、`appears_in_shots` 和 `narrative_function`。
9. 根据 Prop Variant Policy 创建 `PROP_XXX_A/B/C` 状态变体。
10. 文字类道具补充 `text_content`、`text_visibility`、`text_generation_strategy`、`blank_area_required`。
11. 将 P1/P2 连续性风险写入对应资产备注，例如“座机只能出现在墙边小柜，不进入餐桌构图”。
12. 为每个资产记录出现镜头、叙事功能、母题标记、视觉依赖和后续生成状态。
13. 输出 JSON 注册表和人类可读 Markdown。

## Quality Gate
- [ ] 所有分镜引用资产都存在于 `asset_manifest.json`。
- [ ] 没有重复 ID。
- [ ] 没有同一资产被拆成多个无必要 ID。
- [ ] 每个主要角色都有 `identity_anchors`。
- [ ] 每个角色状态变体都有 `variant_id`、`trigger`、`appearance_change_type`、`visual_changes` 和 `appears_in_shots`。
- [ ] 必须拆分的角色状态已经拆分。
- [ ] 不应拆分的短暂表情、动作、光线、镜头角度、临时持有道具没有被错误拆成角色状态。
- [ ] `generation_required=true` 的主要角色状态变体必须 `three_view_required=true`。
- [ ] 每个角色状态变体都有 `must_keep` 身份锚点。
- [ ] `PROP_XXX` 只用于需要稳定资产化的 canonical prop。
- [ ] 反复出现、承载明线/暗线、母题、特写、状态变化、角色身份绑定、文字/照片/符号道具已经注册为 `PROP_XXX`。
- [ ] 一次性、无叙事功能、无状态变化、无特写的普通物件没有被注册为独立 `PROP_XXX`。
- [ ] 每个 `generation_required=true` 的道具都有 `reason_to_generate` 和 `must_not_change`。
- [ ] 每个文字类道具都有文字处理策略，重要文字优先留白或后期叠字。
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
- `artifacts.prop_generation_policy`: `enabled`
- `next_phase.skill`: `asset_prompt_generation`

## Failure Handling
- 引用不存在：返回分镜阶段修正。
- ID 冲突：在资产清单阶段统一重编号，并生成映射表。
- 角色状态变体过细：合并只影响动作、表情、光线、镜头角度或单镜头短暂状态的变体。
- 角色状态变体过粗：若年龄、完整服装、身份装束、持续伤痕、持续脏污或剧情转折后视觉身份被混在同一变体中，必须拆分。
- 道具资产过细：只出现一次且没有叙事功能的普通物件，移出 `PROP_XXX`，写回分镜或场景描述。
- 道具资产过粗：若同一道具有明确状态变化，必须拆成 `PROP_XXX_A/B/C`。
- 文字道具缺少文字内容或后期处理策略：返回资产清单补充。
