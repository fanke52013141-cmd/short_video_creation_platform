# Schema Contracts

本项目的 Markdown 产物服务于人类阅读，JSON 产物服务于下游 Skill 和校验脚本读取。凡是进入下游的核心 JSON，都必须满足 `schemas/` 中对应 schema。

## 核心 schema

| 产物 | Schema |
|---|---|
| `outputs/01_story/story.json` | `schemas/story.schema.json` |
| `outputs/02_art_direction/art_direction.json` | `schemas/art_direction.schema.json` |
| `outputs/03_storyboard/storyboard.json` | `schemas/storyboard.schema.json` |
| `outputs/03_storyboard/storyboard_sequence_review.json` | `schemas/storyboard_sequence_review.schema.json` |
| `outputs/04_assets/asset_manifest.json` | `schemas/asset_manifest.schema.json` |
| `outputs/04_assets/image_generation_queue.json` | queue contract defined by `docs/generation_mode_protocol.md` |
| `outputs/04_assets/audio/voice_reference_manifest.json` | `schemas/voice_reference_manifest.schema.json` |
| `outputs/05_video_prompts/shots/SHOT_XXX.json` | `schemas/shot_video_prompt.schema.json` |
| `outputs/06_external_results/image_result_manifest.json` | `schemas/image_result_manifest.schema.json` |
| `outputs/06_external_results/shot_result_manifest.json` | `schemas/shot_result_manifest.schema.json` |
| `outputs/06_external_results/generated_media_review.json` | `schemas/generated_media_review.schema.json` |
| `outputs/07_final_delivery/continuity_report.json` | `schemas/continuity_report.schema.json` |
| `outputs/07_final_delivery/final_package_manifest.json` | `schemas/final_package_manifest.schema.json` |

## 图片结果契约

`image_result_manifest.json` 必须记录每个图片队列项的：

- `asset_id`
- `image_role`
- `generation_priority`
- `status`
- `blocking_if_missing`
- `used_as_video_reference`
- `prompt_source` 或 `prompt_file`
- `expected_output_path` 或 `result_file_or_url`

`generation_priority` 只能是：

- `must_generate`
- `optional_generate`
- `skip_generation`

`status` 只能是：

- `missing`
- `generated`
- `approved`
- `rejected`
- `needs_regeneration`
- `not_required`

`blocking_if_missing=true` 且状态为 `missing | rejected | needs_regeneration` 时，最终包不得标记为 `completed`。

## 原则

- Markdown 可以灵活，JSON 字段必须稳定。
- 下游 Skill 不得依赖未写入 JSON 的关键事实。
- 如果新增字段会影响下游读取，应同步更新 schema、Skill 文档和 `scripts/validate_project.py`。
- 旧项目不满足 schema 时，应先做迁移或标记为 legacy，不要伪装通过。
