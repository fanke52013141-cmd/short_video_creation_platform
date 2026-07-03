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

## 分镜具体化契约

`storyboard.json` 的每个 shot 必须记录：

- `abstract_terms_detected`
- `concretization_evidence`
- `prompt_cn`

如果 `prompt_cn` 中存在抽象情绪、氛围、事件或人物关系，必须能在 `concretization_evidence` 中找到对应的画面证据。

`storyboard_sequence_review.json` 必须记录：

- `concretization_check_passed`
- `key_turning_point_visual_evidence_check_passed`
- `abstract_prompt_issues`

`concretization_check_passed` 不是说明性字段，而是下游资产清单和视频提示词阶段的质量门。

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

## Seedance 视频提示词契约

`SHOT_XXX.json` 必须记录：

- `shot_id`
- `duration_seconds`
- `task_type`
- `storyboard_reference`
- `character_references`
- `audio_reference_decision`
- `env_reference_decision`
- `prop_policy`
- `prompt_cn`
- `self_check`

`task_type` 只能是：

- `pipeline_shot_generation`
- `multimodal_reference`
- `video_edit`
- `video_extend`
- `combined_task`

Markdown 版 `SHOT_XXX.md` 必须包含：

- `【引用决策】`
- `【资产声明区】`
- `【中文视频提示词】`
- `【自检通过项】`

编辑任务必须使用 `严格编辑 @视频N`；延长任务必须使用 `向前延长 @视频N` 或 `向后延长 @视频N`。

## 外部结果契约

`shot_result_manifest.json` 必须支持每个 shot 的多 take 记录：

- `shot_id`
- `task_type`
- `takes`
- `best_take_id`
- `selected_for_edit`
- `review_status`
- `blocking_issues`

被选入剪辑的 take 必须能追溯到 `take_id`。

`generated_media_review.json` 必须记录：

- `task_type_review_passed`
- `edit_preservation_check_passed`
- `extend_continuity_check_passed`
- `reference_dimension_check_passed`
- `dialogue_audio_sync_check_passed`
- `text_logo_watermark_check_passed`
- `selected_take_check_passed`

外部生成尚未审查时，最终包不得标记为 `completed`。

## 最终包契约

`outputs/05_video_prompts/video_prompt_review.json` 必须满足 `schemas/video_prompt_review.schema.json`。它属于现有视频提示词阶段内部产物，必须由 AI 完成并覆盖全部镜头及全部相邻镜头。

`status=completed` 时还必须存在 `outputs/07_final_delivery/resource_package/`，其中按故事、分镜、人物、场景、道具、音频、视频提示词和质检报告分目录保存。

`final_package_manifest.json` 必须包含 `quality_gates`，至少记录：

- `storyboard_concretization_check_passed`
- `image_required_references_ready`
- `audio_references_ready_for_final`
- `seedance_task_type_check_passed`
- `seedance_prompt_surface_check_passed`
- `external_handoff_preserved_task_type`
- `generated_media_task_type_review_passed`
- `generated_media_no_unresolved_p0`
- `continuity_review_passed`
- `completed_blockers_checked`

`status=completed` 只有在关键质量门全部通过时才允许。

## 原则

- Markdown 可以灵活，JSON 字段必须稳定。
- 下游 Skill 不得依赖未写入 JSON 的关键事实。
- 如果新增字段会影响下游读取，应同步更新 schema、Skill 文档和 `scripts/validate_project.py`。
- 旧项目不满足 schema 时，应先做迁移或标记为 legacy，不要伪装通过。
