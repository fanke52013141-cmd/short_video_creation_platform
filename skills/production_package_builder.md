# Skill: production_package_builder
**Version**: 0.3.0

## Purpose
汇总最终短片生产包，形成可交接、可归档、可复用的项目交付清单。

从 0.3.0 起，本 Skill 不只检查文件是否存在，还必须检查关键质量门是否真正通过。任何缺图、缺音色、分镜具体化审查缺失、Seedance 视频提示词未校验、外部生成结果未 task-aware 审查、或外部结果存在未处理 P0 的项目，都不得标记为 `completed`。

## Inputs
```json
{
  "checkpoint_path": "./checkpoint.json",
  "output_dir": "./outputs",
  "continuity_report_path": "./outputs/07_final_delivery/continuity_report.md",
  "continuity_report_json_path": "./outputs/07_final_delivery/continuity_report.json",
  "generated_media_review_path": "./outputs/06_external_results/generated_media_review.md",
  "generated_media_review_json_path": "./outputs/06_external_results/generated_media_review.json",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
  "voice_reference_manifest_path": "./outputs/04_assets/audio/voice_reference_manifest.json"
}
```

## Outputs
```json
{
  "final_manifest_path": "./outputs/07_final_delivery/final_package_manifest.json",
  "final_readme_path": "./outputs/07_final_delivery/README.md",
  "status": "completed | completed_with_known_gaps | revise_required"
}
```

## Schema
`outputs/07_final_delivery/final_package_manifest.json` 必须满足 `schemas/final_package_manifest.schema.json`。

## Procedure
1. 读取 `checkpoint.json` 和所有阶段产物路径。
2. 检查关键产物是否存在。
3. 检查 `checkpoint.known_gaps` 和 `checkpoint.blocking_issues`。
4. 检查分镜审查、四译法、音色、主要人物三视图、图片结果、视频提示词、外部生成结果审查和连续性审查状态。
5. 检查 `image_result_manifest.json`：所有 `blocking_if_missing=true` 的图片不得为 `missing | rejected | needs_regeneration`。
6. 检查 `voice_reference_manifest.json`：所有最终有声镜头音色不得为 `missing | needed | placeholder`。
7. 检查 `generated_media_review.json`：`status` 必须为 `pass`，且 `task_type_review_passed=true`，没有未处理 P0。
8. 检查 `continuity_report.json`：`status` 必须为 `pass`。
9. 生成最终交付清单，包含版本、Skill 源、产物路径、质量门、缺失项和后续待办。
10. 不重新创作内容，只做整理和归档。

## Completed Blocking Rules
`status=completed` 只有在以下条件全部满足时才允许：

- 分镜序列审查已通过，且 `concretization_check_passed=true`。
- 所有阻断图片已生成或批准。
- 主要人物关键参考图已生成或批准，或有明确豁免。
- 有声镜头音色不是 `missing | needed | placeholder`。
- Seedance 视频提示词已逐 shot 生成，并通过任务类型、编辑/延长句式、资产声明和声音符号检查。
- 外部生成结果已执行 task-aware 审查。
- 外部生成最佳 take 没有未处理 P0。
- 连续性审查已通过。
- `checkpoint.known_gaps` 为空。
- `checkpoint.blocking_issues` 为空。

## Quality Gate
- [ ] 所有必需产物路径存在。
- [ ] 每个产物能追溯到对应 Skill 和源提示词版本。
- [ ] 缺失项被明确标记，不伪装完成。
- [ ] `completed` 状态下没有未处理 P0/P1。
- [ ] `completed` 状态下分镜四译法审查已通过。
- [ ] `completed` 状态下阻断图片已生成或批准。
- [ ] `completed` 状态下主要人物三视图已批准或有明确豁免。
- [ ] `completed` 状态下有声镜头音色不是 `missing | needed | placeholder`。
- [ ] `completed` 状态下 Seedance 视频提示词已通过 task type 校验。
- [ ] `completed` 状态下外部生成结果已完成 task-aware 审查。
- [ ] `completed` 状态下外部生成最佳 take 没有未处理 P0。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `production_package_builder`
- `completed_phases`: 追加 `production_package_builder`
- `quality_gates.final_package_completed_blockers_checked`: true
- `status`: `completed | completed_with_known_gaps | revise_required`

## Failure Handling
- 缺失必需产物：输出缺失清单，不标记项目完成。
- 存在已知缺口但不阻塞草稿：标记为 `completed_with_known_gaps`，不得标记为 `completed`。
- 存在 P0/P1 阻塞项：标记为 `revise_required`。
- 外部生成未执行或未审查：标记为 `completed_with_known_gaps` 或 `revise_required`，不得标记为 `completed`。
