# Skill: image_generation_executor
**Version**: 1.1.0

## Purpose
执行或辅助执行资产图片生成。

本 Skill 不限定生成工具。图片可以由即梦网页端、ChatGPT 网页端、Codex 直接生成，或其他外部图像工具生成。

本 Skill 不重新决定资产，不新增资产，不改名，不重写资产提示词。它只消费 `asset_executor` 固定下来的资产清单，以及 `asset_prompt_generation` 产出的单资产提示词。

硬性规则：

```text
一个 asset_image_task 只生成一张图片。
禁止拼接图、四宫格、对比图、角色设定表、scene sheet、contact sheet。
```

如果一个人物需要“人脸大头特写 + 全身妆造”两类参考，它们是两个独立 `asset_image_task`，分别生成两张图片，不合成到一张图里。

## Position In Flow

```text
asset_executor
→ asset_prompt_generation
→ image_generation_executor
→ storyboard_prompt_generator
```

`asset_prompt_generation` 只负责写提示词。`image_generation_executor` 才负责把这些提示词变成图片或生成队列。

## Inputs

批量输入：

```json
{
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "asset_prompt_dir": "./outputs/assets",
  "style_bible_path": "./outputs/style_bible.md",
  "generation_mode": "jimeng_web_manual | chatgpt_web | codex_direct | external_manual",
  "output_root": "./outputs/assets"
}
```

单个图片任务输入：

```json
{
  "task_id": "IMG_CHARACTER_林小满_FACE",
  "parent_asset_name": "林小满",
  "asset_type": "character",
  "reference_role": "face_closeup",
  "prompt_path": "./outputs/assets/characters/林小满_人脸大头特写.md",
  "generation_mode": "chatgpt_web",
  "reference_bindings": [],
  "output_path": "./outputs/assets/characters/林小满_人脸大头特写.png",
  "output_count": 1,
  "no_collage": true
}
```

字段说明：

- `task_id`: 单张图片任务编号。
- `parent_asset_name`: 来自 `asset_manifest.json` 的稳定资产名。
- `asset_type`: `character | scene | prop`。
- `reference_role`: 这张图的用途，例如 `face_closeup`、`full_body_styling`、`scene_reference`、`independent_prop_reference`。
- `prompt_path`: 对应的单资产提示词 Markdown。
- `generation_mode`: 本次使用的图片生成方式。
- `reference_bindings`: 可选，用户已有图片/视频素材绑定；没有则为空数组。
- `output_path`: 生成后的单张图片保存位置。
- `output_count`: 必须为 `1`。
- `no_collage`: 必须为 `true`。

## Task Expansion Rules

从 `asset_manifest.json` 展开 `asset_image_task`：

### Character

如果人物 `required_reference_set` 包含：

```json
["face_closeup", "full_body_styling"]
```

则展开为两个任务：

```text
林小满_人脸大头特写.png
林小满_全身妆造.png
```

每个任务各生成一张图片。

### Scene

如果场景需要 `scene_reference`，展开为一个任务：

```text
雨夜客厅场景.png
```

只生成单张场景参考图，不生成四宫格，不生成拼贴图。

### Prop

只有当：

```json
{
  "generation_required": true,
  "handling_policy": "generate_independent_prop"
}
```

才展开为一个独立道具图片任务。

`text_prompt_control`、`inherited_from_reference`、`remove_by_instruction` 不生成图片任务。

## Outputs

批量模式输出：

```json
{
  "image_generation_queue_path": "./outputs/image_generation_queue.json",
  "image_generation_queue_md_path": "./outputs/image_generation_queue.md",
  "asset_output_dirs": {
    "characters": "./outputs/assets/characters",
    "scenes": "./outputs/assets/scenes",
    "props": "./outputs/assets/props"
  }
}
```

单任务完成后的产物：

```json
{
  "task_id": "IMG_CHARACTER_林小满_FACE",
  "output_path": "./outputs/assets/characters/林小满_人脸大头特写.png",
  "status": "generated | pending_manual_generation | failed",
  "generation_mode": "chatgpt_web"
}
```

## Procedure

1. 读取 `asset_manifest.json`。
2. 读取 `outputs/assets/characters/*.md`、`outputs/assets/scenes/*.md`、`outputs/assets/props/*.md`。
3. 根据 `required_reference_set`、`generation_required` 和 `handling_policy` 展开 `asset_image_task`。
4. 确认每个 task 都有唯一 `prompt_path` 和唯一 `output_path`。
5. 确认每个 task 的 `output_count=1` 且 `no_collage=true`。
6. 根据 `generation_mode`：
   - `jimeng_web_manual`: 输出人工复制队列。
   - `chatgpt_web`: 输出可直接复制到 ChatGPT 图片生成的单图任务。
   - `codex_direct`: 输出可由 Codex 执行的单图任务。
   - `external_manual`: 输出通用人工生成队列。
7. 生成或等待用户生成图片后，图片必须保存到 `output_path`。
8. 不维护外部生成结果审查，不伪造缺失图片。

## Quality Gate

- [ ] 每个任务只对应一个父资产和一个参考角色。
- [ ] 每个任务只生成一张图片。
- [ ] 没有拼接图、四宫格、设定表、对比图、contact sheet。
- [ ] 人物的人脸大头特写和全身妆造是两个独立任务。
- [ ] 场景参考图是单张空间参考图。
- [ ] 道具只有 `generation_required=true` 且 `handling_policy=generate_independent_prop` 才生成。
- [ ] 每个任务有唯一 `prompt_path`。
- [ ] 每个任务有唯一 `output_path`。
- [ ] 不新增 `asset_manifest.json` 中不存在的资产。
- [ ] 不修改资产命名。

## Checkpoint Update
本 Skill 是图片生成执行节点。若执行，通过后可更新：

- `artifacts.image_generation_queue_json`: `./outputs/image_generation_queue.json`
- `artifacts.image_generation_queue_md`: `./outputs/image_generation_queue.md`
- `artifacts.generated_asset_images`: `./outputs/assets/**.png`

## Failure Handling

- 资产提示词缺失：返回对应的角色、场景或道具提示词生成器。
- 任务要求拼图、四宫格或设定表：拆成多个单图任务。
- 同一任务要求多张图：拆成多个 task，每个 task 一个 `output_path`。
- 用户还未生成图片：停止在生成点，标记为 `pending_manual_generation`，不伪造结果。
- 生成图与资产类型不符：重新生成该单图任务，不修改资产清单。
