# Skill: image_generation_executor
**Version**: 0.2.0

## Purpose
统一管理图片资产生成阶段的队列、优先级、执行模式和结果登记。

本 Skill 不重新决定角色、场景、道具是否需要生成。它只消费上游资产提示词阶段已经明确的规则：

- 角色：`generation_required=true` 的角色状态变体，尤其 `three_view_required=true` 的主要角色状态。
- 场景：每个 `ENV_XXX` 的 Key Plate 必需；Scene Sheet 只在 `scene_sheet_required=true` 时生成。
- 道具：只生成 `asset_tier=canonical_prop` 且 `generation_required=true` 的道具；普通一次性物件不生成独立图片。

该 Skill 输出图片生成队列和 `image_result_manifest.json`。在 `external_manual` 模式下，它不调用图片生成能力，只输出外部生成所需队列和登记表；在 `internal_codex` 模式下，它按同一队列生成或整理本地图片资产。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "asset_prompt_dir": "./outputs/04_assets",
  "generation_mode": "internal_codex | external_manual",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json"
}
```

## Outputs
```json
{
  "image_generation_queue_path": "./outputs/04_assets/image_generation_queue.json",
  "generated_image_index_path": "./outputs/generated_image_index.md",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
  "final_image_dir": "./outputs/04_assets/final_images"
}
```

## Generation Priority Classes

### must_generate
缺失会阻断最终 `completed`，并可能阻断视频参考声明：

- `generation_required=true` 的主要角色状态变体转面参考图。
- `three_view_required=true` 的角色转面参考图。
- 每个 `ENV_XXX` 的 `ENV_XXX_KEY_PLATE`。
- `asset_tier=canonical_prop` 且 `generation_required=true` 的道具标准资产图。
- `detail_prompt_required=true` 的 text_prop、motif_prop、close_up prop 或 state_change prop 的细节/特写图。

### optional_generate
缺失不阻断流程，但应记录为 known gap 或待补充：

- 角色单人全身立绘。
- `scene_sheet_required=true` 的 Scene Sheet 四宫格概览图。
- 次要角色补充图。
- 非关键道具的细节图。

### skip_generation
不生成独立图片，只在分镜、场景或视频提示词正文中描述：

- `asset_tier=scene_dressing`。
- `asset_tier=shot_description_only`。
- `generation_required=false` 的普通道具。
- 未在 `asset_manifest.json` 登记的临时物件。

## Image Roles
图片队列中的 `image_role` 必须使用稳定名称：

- `character_turnaround`
- `character_full_body`
- `scene_key_plate`
- `scene_sheet`
- `prop_standard_asset`
- `prop_detail_closeup`

## Queue Item Contract
每个图片队列项至少包含：

```json
{
  "queue_id": "IMG_0001",
  "asset_id": "CHAR_001_A",
  "parent_asset_id": "CHAR_001",
  "asset_type": "character_variant",
  "image_role": "character_turnaround",
  "generation_priority": "must_generate",
  "prompt_source": "./outputs/04_assets/characters/CHAR_001_A.md",
  "expected_output_path": "./outputs/04_assets/final_images/characters/CHAR_001_A/turnaround.png",
  "blocking_if_missing": true,
  "used_as_video_reference": true,
  "status": "missing"
}
```

## Procedure
1. 读取 `checkpoint.generation_modes.image_generation`。
2. 如果模式仍为 `ask_user`，停止并要求用户选择 `internal_codex` 或 `external_manual`。
3. 读取 `asset_manifest.json`、角色提示词、场景提示词、道具提示词。
4. 构建图片生成队列：角色 → 场景 → 道具。
5. 为每个队列项标记 `must_generate | optional_generate | skip_generation`。
6. 为每个队列项写入 `blocking_if_missing` 和 `used_as_video_reference`。
7. 如果是 `external_manual`，输出 `image_generation_queue.json` 与 `image_result_manifest.json` 空登记表，等待用户在外部生成并填写结果。
8. 如果是 `internal_codex`，按队列顺序生成或整理图片，保存到 `outputs/04_assets/final_images/`。
9. 为每张图片记录结果文件、状态、问题、是否选中、是否可作为视频参考。
10. 输出 `generated_image_index.md` 供人类检查。

## Generation Order
图片生成队列必须按以下顺序排序：

1. 主要角色状态变体转面参考图。
2. 主要角色状态变体单人立绘。
3. 场景 Key Plate。
4. 场景 Scene Sheet。
5. 必需道具标准资产图。
6. 必需道具细节 / 特写图。
7. 次要角色、次要场景、可选补充图。

## Image Result Status
`image_result_manifest.json` 中每个结果状态只能使用：

- `missing`
- `generated`
- `approved`
- `rejected`
- `needs_regeneration`
- `not_required`

## Blocking Rules
- `blocking_if_missing=true` 且状态为 `missing | rejected | needs_regeneration` 时，最终包不得标记为 `completed`。
- 必需角色转面参考图缺失时，不得把该角色状态声明为可稳定视频参考。
- 必需场景 Key Plate 缺失时，后续视频提示词不得默认声明该场景参考图。
- 必需 canonical prop 图片缺失时，可以继续写视频正文描述，但不得声称已有道具参考图。
- 可选图片缺失时，可以继续推进，但必须写入 known gaps。

## Quality Gate
- [ ] 图片生成模式已明确，不是 `ask_user`。
- [ ] `image_generation_queue.json` 存在并覆盖所有应生成图片。
- [ ] 每个队列项有 `generation_priority`、`image_role`、`prompt_source`、`expected_output_path`、`blocking_if_missing`。
- [ ] `must_generate` 队列项在结果 manifest 中都有记录。
- [ ] `skip_generation` 项不会生成独立图片。
- [ ] 每个需要图片的资产都有 `missing | generated | approved | rejected | needs_regeneration | not_required` 状态。
- [ ] 主要人物转面参考图有独立状态记录。
- [ ] 场景 Key Plate 必需，Scene Sheet 只在条件满足时生成。
- [ ] 道具图片只覆盖 canonical prop，不覆盖普通一次性物件。
- [ ] 文字类道具如果文字不稳定，标记后期修正或留白策略。
- [ ] 所有生成媒体只保存在 local run，不提交仓库。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `image_generation_executor`
- `completed_phases`: 追加 `image_generation_executor`
- `artifacts.image_generation_queue`: `./outputs/04_assets/image_generation_queue.json`
- `artifacts.image_result_manifest`: `./outputs/06_external_results/image_result_manifest.json`
- `artifacts.generated_image_index`: `./outputs/generated_image_index.md`
- `next_phase.skill`: `voice_reference_manifest_builder`

## Failure Handling
- 模式未确认：停止并询问用户。
- 队列无法构建：返回资产提示词阶段补齐缺失提示词。
- 生成失败：记录到 `image_result_manifest.json`，不覆盖已通过图片。
- 必需图片缺失：允许草稿继续，但最终包不得标记 `completed`。
- 可选图片缺失：记录 known gap，不阻断后续阶段。
