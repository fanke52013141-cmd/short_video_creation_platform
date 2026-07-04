# Skill: video_prompt_generator
**Version**: 2.4.0

## Source Prompt
`skills/raw_prompts/seedance_video_prompt.source.md`

## Purpose
生成最终可复制到即梦 / Seedance 2.0 的中文视频提示词，并同时输出可校验的结构化视频计划。

本 Skill 在所有分镜参考图生成完成之后运行。它负责把一个或多个连续 `S###` 规划为 `V###` 视频提示词。

## Minimal Inputs

```json
{
  "storyboard_json_path": "./outputs/storyboard.json",
  "storyboard_prompts_path": "./outputs/storyboard_prompts.md",
  "storyboard_reference_dir": "./outputs/storyboards",
  "shot_asset_map_path": "./outputs/shot_asset_map.json",
  "asset_reference_dir": "./outputs/assets"
}
```

可选输入：

```json
{
  "reference_media": []
}
```

不需要重新读取完整 `story.md`。视频阶段以导演分镜、分镜参考图提示词、分镜图和资产图为准。

## Outputs

```json
{
  "video_prompts_path": "./outputs/video_prompts.md",
  "video_prompts_json_path": "./outputs/video_prompts.json"
}
```

`video_prompts.md` 给人复制使用；`video_prompts.json` 给校验脚本、CI 和后续自动化使用。两者必须表达同一组 `V###`。

## Merge Policy

合并对象是连续 `shot_id`，不是 `scene_id`。

```text
合并 S，不合并 SC。
SC 只是判断 S 能不能合并的场景边界。
```

相邻 `S###` 只有同时满足以下条件，才允许合并为一个 `V###`：

1. `shot_id` 必须连续。
2. `scene_id` 必须相同。
3. 合并后 `duration_seconds` 总和必须 `<=15`。
4. 没有明显场景切换、时间跳跃、梦境/回忆切换或叙事空间切换。
5. 分镜参考图之间可以形成自然连续动作或自然镜头推进。

如果某个单独分镜时长小于 15 秒，不代表必须单独生成。应该判断它是否适合与相邻分镜合并。

### 优先合并

满足硬性条件后，以下情况优先合并：

- 同一动作链延续。
- 同一人物状态延续。
- 同一道具交互延续。
- 同一空间站位延续。
- 远景到中景、中景到近景、人物到手部细节等景别变化，但动作和情绪连续。

### 必须拆分

以下情况必须拆分：

- `scene_id` 不同。
- 合并后超过 15 秒。
- 时间跳跃。
- 叙事空间切换。
- 动作不连续，合并后提示词会含混。
- 主体、环境、情绪或镜头目标发生明显断裂。

## Storyboard Frame Role Resolution

`storyboard_prompt_generator` 会给每个 `S###` 输出推荐角色：

```text
first_frame | last_frame | keyframe
```

视频阶段必须根据最终合并结果确定实际引用角色：

- 一个 `V###` 只含一个 `S###`：该分镜图通常作为 `first_frame`；如需要结束锁定，也可同时作为关键参考。
- 一个 `V###` 合并多个 `S###`：第一个 source shot 的分镜图作为 `first_frame`。
- 一个 `V###` 合并多个 `S###`：最后一个 source shot 的分镜图作为 `last_frame`。
- 中间 source shots 的分镜图作为 `keyframe`。

如果分镜提示词里的 `recommended_frame_role` 与合并结果冲突，以视频阶段的合并结果为准，并在 `video_prompts.json` 里记录最终声明。

## Previous Storyboard Anchor Rule

如果 `storyboard_prompts.md` 中某个 source shot 标记：

```text
uses_previous_storyboard_reference: true
reference_purpose: placement_anchor
```

且该引用没有跨 `scene_id`，视频提示词应保留站位连续性描述：

```text
参考@上一分镜_站位，保持人物空间关系、朝向和相对位置不变
```

该锚点只用于站位、朝向、空间比例和连续性，不用于复制上一分镜的动作或表情。

## Required JSON Per V###

每个 `V###` 必须包含：

```json
{
  "video_id": "V001",
  "task_type": "pipeline_shot_generation",
  "source_shots": ["S001", "S002"],
  "duration_seconds": 10,
  "declared_assets": [],
  "frame_references": [
    {
      "shot_id": "S001",
      "asset_name": "S001",
      "role": "first_frame",
      "path": "./outputs/storyboards/S001.png"
    },
    {
      "shot_id": "S002",
      "asset_name": "S002",
      "role": "last_frame",
      "path": "./outputs/storyboards/S002.png"
    }
  ],
  "uses_previous_storyboard_anchor": true,
  "merge_decision": {
    "strategy": "merged_strong_action_continuity",
    "reason": "同一场景内动作与站位连续，合并可减少漂移。",
    "continuity_risk": "high"
  },
  "prompt_cn": "..."
}
```

## Output Requirements

每条 `V###` 必须包含：

```markdown
【自检通过项】
【资产声明区】
【中文视频提示词】
```

硬性要求：

- 只输出中文，不输出英文版本，不输出中英对照。
- 人物、场景和分镜图必须先声明再引用。
- 道具一般不使用 `@PROP`，写入正文描述。
- 高强度动作必须输出 `【生成风险提示】`。
- 必须包含无字幕、无 Logo、无水印约束。
- 每条 `V###` 必须写 `merge_decision`。

## Quality Gate

- [ ] 每个 storyboard shot 都被且仅被一个 `V###` 覆盖。
- [ ] 合并的 source shots 必须连续。
- [ ] 合并的 source shots 必须同一 `scene_id`。
- [ ] 合并总时长必须 `<=15` 秒。
- [ ] 每条 `V###` 有 `merge_decision`。
- [ ] 每条 `V###` 有 `frame_references`，并明确 `first_frame`、`last_frame` 或 `keyframe`。
- [ ] 同场景站位延续时保留 `参考@上一分镜_站位`。
- [ ] 不输出英文 Prompt。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `video_prompt_generator`
- `completed_phases`: 追加 `video_prompt_generator`
- `artifacts.video_prompts`: `./outputs/video_prompts.md`
- `artifacts.video_prompts_json`: `./outputs/video_prompts.json`
