# Quality Gate Hardening Protocol

本协议用于防止“文件存在但内容不可生产”的假通过问题。

## 核心原则

1. 下游不得只凭 Markdown 判断阶段通过，必须读取 JSON 和 schema。
2. 生成提示词阶段不得声明不存在、未生成、未批准或需要重生的参考图。
3. 外部生成交接不得丢失 Seedance task_type、编辑/延长句式、外部素材角色和图片结果可用性。
4. 最终 `completed` 不是文件齐全，而是关键质量门全部通过。

## 必须硬阻断的情况

### 分镜阶段

- `storyboard.json` 缺少 `abstract_terms_detected`。
- `storyboard.json` 缺少 `concretization_evidence`。
- `storyboard_sequence_review.json` 缺少 `concretization_check_passed`。
- `concretization_check_passed=false`。
- 关键转折镜头缺少可见画面证据。

### 图片阶段

- `must_generate` 队列项没有进入 `image_result_manifest.json`。
- `blocking_if_missing=true` 的图片仍为 `missing | rejected | needs_regeneration`。
- `used_as_video_reference=true` 但图片状态不是 `generated | approved`。

### 音色阶段

- 有台词、旁白、留言或可听见人声的 shot 没有 `AUDIO_XXX`。
- 最终交付时 `AUDIO_XXX` 状态仍为 `missing | needed | placeholder`。

### 视频提示词阶段

- 单 shot 文件缺失。
- 单 shot 文件缺少 `【引用决策】`、`【资产声明区】`、`【中文视频提示词】` 或 `【自检通过项】`。
- 缺少 Seedance `task_type`。
- `video_edit` 未使用 `严格编辑 @视频N`。
- `video_extend` 未使用 `向前延长 @视频N` 或 `向后延长 @视频N`。
- 默认出现 `@PROP`。
- 有人声但没有 `@AUDIO`。
- 声明了不可用图片参考。

### 外部交接阶段

- 交接包没有保留 `task_type`。
- 交接包没有保留编辑/延长硬句式。
- 交接包没有保留外部素材角色。
- 交接包没有保留图片结果可用性。

### 生成结果审查阶段

- 外部生成结果未审查。
- `generated_media_review.json` 缺少 `task_type_review_passed`。
- `task_type_review_passed=false`。
- 被选为 best take 的镜头有未处理 P0。
- `video_edit` 任务整体重生成或破坏未要求修改的部分。
- `video_extend` 任务人物、场景、光线、动作节奏或声音不连续。

### 最终打包阶段

`status=completed` 必须同时满足：

- 分镜四译法审查通过。
- 阻断图片全部 ready。
- 最终有声镜头音色全部 ready。
- Seedance 视频提示词已通过任务类型和表层校验。
- 外部交接保留 task_type。
- 外部生成结果已 task-aware 审查。
- 外部结果无未处理 P0。
- 连续性审查通过。
- `known_gaps` 为空。
- `blocking_issues` 为空。

否则只能是：

- `completed_with_known_gaps`
- `revise_required`

## 推荐校验命令

```bash
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase storyboard
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase assets
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase video
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase final
```

专项 Seedance prompt 校验仍可单独运行：

```bash
python scripts/validate_seedance_video_prompts.py local_runs/YYYY-MM-DD/project_slug
```

主校验已经内置 Seedance prompt 表层检查；专项脚本用于单独排查视频提示词问题。
