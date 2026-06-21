# Phase State Machine

本文件定义 local run 中每个阶段的状态语义。真实运行状态写入 `checkpoint.json`，仓库只提交 `checkpoint.template.json`。

## 状态值

| 状态 | 含义 |
|---|---|
| `not_started` | 阶段尚未开始。 |
| `in_progress` | 阶段正在生成或整理。 |
| `needs_user_input` | 缺少用户选择、确认或素材。 |
| `draft_ready` | 草稿产物已生成，但不可视为最终生产准备完成。 |
| `review_required` | 需要人工或审查 Skill 检查。 |
| `approved` | 用户已确认该阶段产物可作为下游输入。 |
| `completed` | 阶段完成且无阻塞问题。 |
| `completed_with_known_gaps` | 可继续草稿流程，但存在必须在最终交付前解决的缺口。 |
| `blocked` | 存在 P0 或缺少关键输入，不能继续到依赖该产物的阶段。 |

## 基本规则

- 下游阶段只能读取 `approved`、`completed` 或明确允许草稿继续的 `completed_with_known_gaps`。
- `storyboard_sequence_review` 必须在 `asset_manifest_builder` 之前完成。
- 有未处理 P0 时，不得进入后续依赖阶段。
- 有 P1 时，必须修复或由用户明确接受风险。
- 音色 `missing` 可以进入草稿视频提示词，但不能最终 `completed`。
- 主要人物三视图未批准可以进入草稿测试，但不能最终 `completed`。
- 外部生成结果未审查时，最终包只能是 `completed_with_known_gaps` 或 `revise_required`。

## 完成状态

最终打包阶段只允许三种项目级状态：

- `completed`：全部关键质量门通过。
- `completed_with_known_gaps`：可归档草稿，但仍有明确缺口。
- `revise_required`：存在阻塞问题，不能交付。
