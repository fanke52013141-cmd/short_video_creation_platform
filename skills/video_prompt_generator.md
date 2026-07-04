# Skill: video_prompt_generator
**Version**: 2.7.0

## Source Prompt
`skills/raw_prompts/seedance_video_prompt.source.md`

## Purpose
在所有分镜参考图生成完成后，把连续分镜组织成最终可复制到即梦 / Seedance 的中文视频提示词，并同步输出结构化 `video_prompts.json`。

本 Skill 必须同时处理：

- 资产声明
- 画面描述
- 镜头描述
- 人物动作与表情
- 场景互动
- 物品交互
- 环境音
- 配乐
- 配音
- 台词或无声留白

它不改剧本，不改分镜，不新增资产，不重新生成图片。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/storyboard.json",
  "storyboard_prompts_path": "./outputs/storyboard_prompts.md",
  "storyboard_reference_dir": "./outputs/storyboards",
  "shot_asset_map_path": "./outputs/shot_asset_map.json",
  "asset_reference_dir": "./outputs/assets",
  "optional_audio_references": [],
  "optional_dialogue_or_voiceover_notes": ""
}
```

不需要默认读取 `story.md`。视频阶段以导演分镜、分镜参考图提示词、分镜图、资产图和用户补充声音/台词要求为准。

## Outputs
```json
{
  "video_prompts_path": "./outputs/video_prompts.md",
  "video_prompts_json_path": "./outputs/video_prompts.json"
}
```

## Asset Declaration Contract

每条 `V###` 必须先输出【资产声明区】，再进入正文。

资产声明区可包含：

- `@S001_分镜参考图（首帧）`
- `@S002_分镜参考图（尾帧）`
- `@S003_分镜参考图（关键帧）`
- `@人物状态资产（人物资产）`
- `@场景资产（场景资产）`
- `@物品资产（物品资产）`
- `@声音参考（声音参考）`
- `@配乐参考（配乐参考）`
- `@环境音参考（环境音参考）`
- `@风格参考（风格参考）`

正文中引用的资产名必须与声明区完全一致。

## Prompt Body Contract

【中文视频提示词】必须根据当前素材实际情况写清楚：

1. 画面描述：从首帧/关键帧/尾帧如何演进。
2. 镜头描述：景别、主运镜、焦点、节奏；单镜头只允许一种主运镜。
3. 人物动作与表情：人物资产锁定外观，正文补动作、姿态、表情、情绪线索。
4. 场景互动：场景资产锁定空间，正文补局部变化、光影、主体与环境关系。
5. 物品交互：物品出现时机、位置、触碰、移动、状态变化。
6. 声音设计：环境音、配乐、配音、无声留白。
7. 台词块：仅在用户需要台词、旁白、电话、独白或对话时输出。
8. 约束条件：画面保持无字幕，避免生成文字、Logo、水印；如果用户明确要文字/字幕，单独说明文字内容、样式、出现时机和位置。

## Lock And Complete Rule

提示词内容 = 未被素材锁定的必要维度 + 素材之间的关系说明 + 镜头可执行描述 + 声音/台词/节奏设计。

省略规则：

- 有首帧、尾帧或关键帧时，不重复描述已锁定构图，只写画面演进。
- 有人物资产时，不重复描述人物外观，只写动作、表情、姿态和情绪。
- 有场景资产时，不重复描述环境全貌，只写主体行动、镜头运动、局部光影和声音。
- 有物品资产时，不重复描述物品静态外形，只写出现、位置、交互和状态变化。
- 有声音参考时，不重复写音色，只写情绪、语速、音量、停顿和句尾走向。
- 有配乐参考时，不重复写音乐风格，只写画面节奏如何对齐音乐。

## Merge Policy

合并对象是连续 `S###`，不是 `SC###`。`SC###` 只是合并边界。

相邻分镜只有同时满足以下条件，才允许合并为一个 `V###`：

1. `shot_id` 连续。
2. `scene_id` 相同。
3. 合并后 `duration_seconds` 总和 `<=15`。
4. 没有场景切换、时间跳跃或叙事空间切换。
5. 动作、情绪、站位、道具交互或镜头推进可以自然连续。

单个分镜小于 15 秒不代表必须单独生成；如果同场景、动作连续、总时长不超过 15 秒，优先合并。

## Frame Reference Policy

视频阶段根据最终合并结果确定每张分镜图的实际角色：

- 单个 `S###` 生成一个 `V###`：该分镜图作为 `first_frame`。
- 多个 `S###` 合并为一个 `V###`：第一个 source shot 是 `first_frame`。
- 多个 `S###` 合并为一个 `V###`：最后一个 source shot 是 `last_frame`。
- 中间 source shots 是 `keyframe`。

每条 `V###` 必须在 `video_prompts.json` 中写入 `frame_references`。

## Required JSON Per V###

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

## Markdown Output Requirements

每条 `V###` 必须包含：

```markdown
一、【自检通过项】
二、【资产声明区】
三、【中文视频提示词】
```

如涉及高强度动作，必须在最前面补：

```markdown
零、【生成风险提示】
```

## Quality Gate

- [ ] 每个 storyboard shot 都被且仅被一个 `V###` 覆盖。
- [ ] 合并的 source shots 连续。
- [ ] 合并的 source shots 同一 `scene_id`。
- [ ] 合并总时长 `<=15` 秒。
- [ ] 每条 `V###` 有 `merge_decision`。
- [ ] 每条 `V###` 有 `frame_references`。
- [ ] 每条提示词有资产声明区。
- [ ] 资产声明区包含当前 `V###` 实际使用的分镜、人物、场景、物品、声音、配乐或环境音资产。
- [ ] 中文视频提示词包含画面、镜头、动作、声音/配乐/台词或无声留白。
- [ ] 抽象词已转译为可见动作、光影、声音或空间关系。
- [ ] 每个视频段只使用一种主运镜方式。
- [ ] 不输出英文 Prompt。
