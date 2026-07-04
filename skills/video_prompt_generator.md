# Skill: video_prompt_generator
**Version**: 2.5.0

## Source Prompt
`skills/raw_prompts/seedance_video_prompt.source.md`

## Purpose
在所有分镜参考图生成完成后，把连续分镜组织成最终可复制到即梦 / Seedance 的中文视频提示词，并同步输出结构化 `video_prompts.json`。

本 Skill 只服务当前流水线生产，不处理视频编辑、视频延长、音频参考、多模态实验任务或轨道拼接。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/storyboard.json",
  "storyboard_prompts_path": "./outputs/storyboard_prompts.md",
  "storyboard_reference_dir": "./outputs/storyboards",
  "shot_asset_map_path": "./outputs/shot_asset_map.json",
  "asset_reference_dir": "./outputs/assets"
}
```

不需要读取 `story.md`。视频阶段以导演分镜、分镜参考图提示词、分镜图和资产图为准。

## Outputs
```json
{
  "video_prompts_path": "./outputs/video_prompts.md",
  "video_prompts_json_path": "./outputs/video_prompts.json"
}
```

## Merge Policy

合并对象是连续 `S###`，不是 `SC###`。`SC###` 只是合并边界。

相邻分镜只有同时满足以下条件，才允许合并为一个 `V###`：

1. `shot_id` 连续。
2. `scene_id` 相同。
3. 合并后 `duration_seconds` 总和 `<=15`。
4. 没有场景切换、时间跳跃或叙事空间切换。
5. 动作、情绪、站位或镜头推进可以自然连续。

单个分镜小于 15 秒不代表必须单独生成；如果同场景、动作连续、总时长不超过 15 秒，优先合并。

必须拆分：

- `scene_id` 不同。
- 合并后超过 15 秒。
- 时间或叙事空间跳跃。
- 动作不连续，合并后提示词含混。

## Frame Reference Policy

视频阶段根据最终合并结果确定每张分镜图的实际角色：

- 单个 `S###` 生成一个 `V###`：该分镜图作为 `first_frame`。
- 多个 `S###` 合并为一个 `V###`：第一个 source shot 是 `first_frame`。
- 多个 `S###` 合并为一个 `V###`：最后一个 source shot 是 `last_frame`。
- 中间 source shots 是 `keyframe`。

每条 `V###` 必须在 `video_prompts.json` 中写入 `frame_references`。

## Previous Storyboard Anchor

如果 `storyboard_prompts.md` 中某个 source shot 标记：

```text
uses_previous_storyboard_reference: true
reference_purpose: placement_anchor
```

且没有跨 `scene_id`，视频提示词应保留：

```text
参考@上一分镜_站位，保持人物空间关系、朝向和相对位置不变
```

该锚点只用于站位、朝向、空间比例和连续性。

## Required JSON Per V###

每个 `V###` 必须包含：

```json
{
  "video_id": "V001",
  "task_type": "pipeline_shot_generation",
  "source_shots": ["S001", "S002"],
  "duration_seconds": 10,
  "scene_id": "SC001",
  "merge_decision": {
    "strategy": "merged_strong_action_continuity",
    "reason": "同一场景内动作与站位连续，合并可减少漂移。",
    "continuity_risk": "high"
  },
  "frame_references": [],
  "declared_assets": [],
  "uses_previous_storyboard_anchor": true,
  "risk_notice_required": false,
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

- 只输出中文。
- 分镜图、人物资产、场景资产必须先声明再引用。
- 道具一般不使用 `@PROP`，写入正文描述。
- 必须包含无字幕、无 Logo、无水印约束。
- 每条 `V###` 必须写 `merge_decision` 和 `frame_references`。

## Quality Gate

- [ ] 每个 storyboard shot 都被且仅被一个 `V###` 覆盖。
- [ ] 合并的 source shots 连续。
- [ ] 合并的 source shots 同一 `scene_id`。
- [ ] 合并总时长 `<=15` 秒。
- [ ] 每条 `V###` 有 `merge_decision`。
- [ ] 每条 `V###` 有 `frame_references`。
- [ ] 不输出英文 Prompt。
