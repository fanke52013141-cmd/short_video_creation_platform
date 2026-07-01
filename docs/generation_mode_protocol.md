# Generation Mode Protocol

图片生成阶段分为两个执行分支，但两种分支必须共享同一个图片生成队列和结果登记表。

## 模式

| 模式 | 说明 | Codex 动作 | 用户动作 |
|---|---|---|---|
| `external_manual` | 用户在外部网页端生成图片。 | 输出图片生成队列、提示词、资产清单、复制说明和结果登记表。 | 复制提示词到外部工具生成图片，并回填结果路径/URL/状态。 |
| `internal_codex` | Codex 直接调用图片生成能力。 | 按图片生成队列生成图片并保存到本地 run。 | 审看结果，决定是否重生或进入下一阶段。 |

视频生成默认仍然是 `external_manual`。剪辑默认在剪映 / CapCut 等外部工具完成。

## 必问问题

进入图片资产生成前，如果用户没有明确说明生成模式，询问：

```text
这一步图片资产你希望怎么生成：外部生成，还是由 Codex 直接生成？
```

不要在用户未确认时默认执行大批量图片生成。

## 共同流程

无论选择哪种模式，都必须先完成图片生成队列：

1. 读取 `asset_manifest.json`、角色提示词、场景提示词、道具提示词。
2. 构建 `outputs/04_assets/image_generation_queue.json`。
3. 将每个图片项标记为 `must_generate`、`optional_generate` 或 `skip_generation`。
4. 为每个图片项写入 `image_role`、`prompt_source`、`expected_output_path`、`blocking_if_missing`、`used_as_video_reference`。
5. 生成或初始化 `outputs/06_external_results/image_result_manifest.json`。
6. 更新 `checkpoint.generation_modes.image_generation`。

## 生成优先级

### must_generate

必须生成。缺失、被拒绝或需要重生时，最终包不得标记为 `completed`。

- `generation_required=true` 的主要角色状态变体转面参考图。
- `three_view_required=true` 的角色转面参考图。
- 每个 `ENV_XXX` 的 Key Plate。
- `asset_tier=canonical_prop` 且 `generation_required=true` 的道具标准资产图。
- `detail_prompt_required=true` 的 text_prop、motif_prop、close_up prop 或 state_change prop 的细节/特写图。

### optional_generate

可选生成。缺失不阻断流程，但应记录 known gap。

- 角色单人全身立绘。
- `scene_sheet_required=true` 的 Scene Sheet 四宫格概览图。
- 次要角色补充图。
- 非关键道具的细节图。

### skip_generation

不生成独立图片。

- `asset_tier=scene_dressing`。
- `asset_tier=shot_description_only`。
- `generation_required=false` 的普通道具。
- 未在 `asset_manifest.json` 登记的临时物件。

## 图片角色

图片队列中的 `image_role` 必须使用稳定名称：

- `character_turnaround`
- `character_full_body`
- `scene_key_plate`
- `scene_sheet`
- `prop_standard_asset`
- `prop_detail_closeup`

## 生成顺序

图片生成队列必须按以下顺序排序：

1. 主要角色状态变体转面参考图。
2. 主要角色状态变体单人立绘。
3. 场景 Key Plate。
4. 场景 Scene Sheet。
5. 必需道具标准资产图。
6. 必需道具细节 / 特写图。
7. 次要角色、次要场景、可选补充图。

## external_manual 分支

输出：

- `outputs/04_assets/image_generation_queue.json`
- `outputs/04_assets/characters/*.md`
- `outputs/04_assets/scenes/*.md`
- `outputs/04_assets/props/*.md`
- `outputs/06_external_results/image_result_manifest.json`
- 可选：`outputs/06_external_results/image_generation_handoff.md`

不得调用图片生成工具。`image_result_manifest.json` 初始可全部为 `missing` 或 `not_required`，等待用户回填结果。

## internal_codex 分支

输出：

- 上述图片提示词文件。
- `outputs/04_assets/image_generation_queue.json`
- `outputs/04_assets/final_images/characters/**/*.png`
- `outputs/04_assets/final_images/scenes/**/*.png`
- `outputs/04_assets/final_images/props/**/*.png`
- `outputs/generated_image_index.md`
- `outputs/06_external_results/image_result_manifest.json`

要求：

- 图片生成只按队列执行，不临时新增资产。
- 人物的不同年龄、服装、状态必须使用资产清单中的角色状态变体，不放在同一张资产图里。
- 场景图片优先生成 Key Plate；Scene Sheet 只按条件生成。
- 道具图片只生成 canonical prop，普通一次性物件不生成独立道具图。
- 生成图片只属于本地 run，不提交仓库。

## image_result_manifest 状态

每项状态只能使用：

- `missing`
- `generated`
- `approved`
- `rejected`
- `needs_regeneration`
- `not_required`

`blocking_if_missing=true` 且状态为 `missing | rejected | needs_regeneration` 时，最终包不得标记为 `completed`。

## Checkpoint 字段

建议写入：

```json
{
  "generation_modes": {
    "image_generation": "external_manual | internal_codex",
    "video_generation": "external_manual",
    "editing": "external_manual"
  },
  "artifacts": {
    "image_generation_queue": "./outputs/04_assets/image_generation_queue.json",
    "image_result_manifest": "./outputs/06_external_results/image_result_manifest.json"
  }
}
```

## 失败处理

- 外部生成失败：记录到 `outputs/06_external_results/generation_log.csv`，保留提示词，标记重试原因。
- 内部生成失败：保留提示词，记录失败资产 ID，不覆盖已确认图片。
- 文字生成错误：优先使用留白或后期叠字策略，不把错误文字结果标记为 approved。
- 主要人物转面参考图未批准：允许草稿继续，但最终包不得标记为 `completed`。
- 场景 Key Plate 缺失：后续视频提示词不得默认声明该场景参考图。
