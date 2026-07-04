# Skill: image_generation_executor
**Version**: 1.2.0

## Purpose
执行或辅助执行资产图片生成。

本 Skill 不限定生成工具。图片可以由即梦网页端、ChatGPT 网页端、Codex 直接生成，或其他外部图像工具生成。

本 Skill 不重新决定资产，不新增资产，不改名，不重写资产提示词。它只消费 `asset_executor` 固定下来的资产清单，以及 `asset_prompt_generation` 产出的单资产提示词。

## Core Rule

```text
一个 asset_image_task 只生成一张图片。
```

人物资产允许是一张 21:9 人物资产图。它可以在同一张图中包含：

```text
人物特写 / 正面 / 侧面 / 后视图
```

这仍然算一张人物资产图，不算多个输出。

禁止的是一次任务输出多张独立图片、多个文件、四宫格候选方案或对比方案。

## Position In Flow

```text
asset_executor
→ asset_prompt_generation
→ image_generation_executor
→ storyboard_prompt_generator
```

## Inputs

批量输入：

```json
{
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "asset_prompt_dir": "./outputs/assets",
  "generation_mode": "jimeng_web_manual | chatgpt_web | codex_direct | external_manual",
  "output_root": "./outputs/assets"
}
```

单个图片任务输入：

```json
{
  "task_id": "IMG_CHARACTER_林小满_雨夜接电话状态",
  "asset_name": "林小满_雨夜接电话状态",
  "asset_type": "character",
  "prompt_path": "./outputs/assets/characters/林小满_雨夜接电话状态.md",
  "generation_mode": "chatgpt_web",
  "output_path": "./outputs/assets/characters/林小满_雨夜接电话状态.png",
  "output_count": 1
}
```

## Task Expansion Rules

### Character

每个 `character` 资产只展开为一个图片任务。

输出是一张 21:9 人物资产图，建议包含人物特写、正面、侧面和后视图，用于稳定该人物状态。

### Scene

每个需要生成的 `scene` 资产只展开为一个图片任务，输出一张场景参考图。

### Prop

只有当 `generation_required=true` 且 `handling_policy=generate_independent_prop` 时，才展开为一个道具图片任务。

## Outputs

批量模式输出：

```json
{
  "image_generation_queue_path": "./outputs/image_generation_queue.json",
  "image_generation_queue_md_path": "./outputs/image_generation_queue.md"
}
```

单任务完成后的产物：

```json
{
  "task_id": "IMG_CHARACTER_林小满_雨夜接电话状态",
  "output_path": "./outputs/assets/characters/林小满_雨夜接电话状态.png",
  "status": "generated | pending_manual_generation | failed",
  "generation_mode": "chatgpt_web"
}
```

## Procedure

1. 读取 `asset_manifest.json`。
2. 读取 `outputs/assets/**/*.md` 中的资产提示词。
3. 每个有 `output_prompt_path` 的资产展开为一个 `asset_image_task`。
4. 确认每个 task 都有唯一 `prompt_path` 和唯一 `output_path`。
5. 确认每个 task 的 `output_count=1`。
6. 根据 `generation_mode` 输出对应执行队列或直接执行。
7. 生成或等待用户生成图片后，图片必须保存到 `output_path`。

## Quality Gate

- [ ] 每个任务只对应一个资产。
- [ ] 每个任务只生成一张图片文件。
- [ ] 人物资产图允许是 21:9 多视角资产图。
- [ ] 场景参考图是单张空间参考图。
- [ ] 道具只有符合独立生成条件时才生成。
- [ ] 不新增 `asset_manifest.json` 中不存在的资产。
- [ ] 不修改资产命名。

## Failure Handling

- 同一任务要求多个文件：拆回一个资产一个任务。
- 用户还未生成图片：标记为 `pending_manual_generation`，不伪造结果。
- 生成图与资产类型不符：重新生成该单图任务，不修改资产清单。
