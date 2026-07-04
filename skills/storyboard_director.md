# Skill: storyboard_director
**Version**: 2.3.0

## Source Prompt
`skills/raw_prompts/storyboard_director.source.md`

## Purpose
将已确认故事和一页风格圣经转化为导演分镜序列 `storyboard.json`。

本 Skill 负责具体构图、景别、机位、镜头调度、动作节奏和 shot 结构化。它不得输出资产草表、资产 ID、角色拆分、场景拆分、道具拆分、图片提示词、视频提示词、音色定义或外部交接材料。

导演方法论：

```text
剧本 → 戏剧节拍 → 观看问题 → 视点策略 → 镜头功能 → 镜头参数 → 蒙太奇关系
```

每个镜头必须回答：观众此刻看见什么。
每个剪接必须回答：观众因此想到什么。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "max_shot_duration_seconds": 15
}
```

## Outputs
```json
{
  "storyboard_json_path": "./outputs/storyboard.json"
}
```

## Internal Director Method

该方法只用于导演内部推理，不作为 `storyboard.json` 的字段输出。

### 1. 戏剧节拍
先按“变化”拆故事，而不是按句子、动作流水账或台词拆。

每个节拍至少判断：

- 核心事件是什么。
- 人物想要什么。
- 冲突在哪里。
- 信息什么时候暴露。
- 情绪从哪里转到哪里。

### 2. 观看问题
每个节拍转成一个观看问题：

```text
观众此刻应该知道什么、感受到什么、站在谁的意识位置里看？
```

镜头顺序就是观众的认知顺序。

### 3. 视点策略
每个镜头必须选择清晰的视点功能：

- 客观视点：旁观事件。
- 主观视点：进入角色感知。
- 半主观视点：贴近角色但保留外部观察。
- 全知视点：观众知道角色不知道的信息。
- 限制视点：观众只知道角色知道的东西。

### 4. 镜头功能
不要把镜头当画面编号，要当叙事功能单位。常见功能包括：

- 建立空间
- 引导注意力
- 表达动作
- 表达反应
- 揭示信息
- 隐藏信息
- 转换视点
- 改变节奏
- 制造悬念
- 形成隐喻

没有明确功能的镜头必须删除、合并或重写。

### 5. 蒙太奇关系
相邻镜头必须有关系。常见关系包括：

- 连续：保持动作和空间清晰。
- 因果：A 导致 B。
- 反应：A 是刺激，B 是心理反应。
- 对照：A 与 B 形成冲突。
- 递进：信息或情绪升级。
- 省略：跳过过程，只保留关键节点。
- 平行：两条行动线互相强化。
- 隐喻：并置产生第三层含义。
- 反讽：声音、画面或前后镜头互相否定。
- 悬念：先给结果，延迟原因。

镜头 A + 镜头 B 不只是 A 然后 B；相接后必须产生连续、因果、反应、对照、递进、省略、隐喻、反讽或悬念中的至少一种意义关系。

## shot_id vs scene_id

- `shot_id` 是镜头编号，表示第几个镜头，必须全片唯一并按顺序连续：`S001`、`S002`、`S003`。
- `scene_id` 是场景/时空单元编号，表示这个镜头属于哪一个连续场景，可以被多个 shot 复用：`SC001`、`SC002`。

`scene_id` 由导演创建，用于后续视频提示词判断同场景连续镜头能否合并，也用于场景切换时停止上一分镜站位锚点。

## Required Shot Fields

每个 shot 只包含：

```json
{
  "shot_id": "S001",
  "scene_id": "SC001",
  "duration_seconds": 5,
  "framing": "中景",
  "camera_move": "固定镜头",
  "action_desc": "林小满坐在沙发边缘，手机屏幕在茶几上亮起。"
}
```

字段说明：

- `shot_id`: 镜头编号，格式 `S###`，全片唯一且连续。
- `scene_id`: 场景/时空单元编号，格式 `SC###`，由导演创建，同一连续场景内多个镜头可共用。
- `duration_seconds`: 必填，每个 shot 必须 `>0` 且 `<=15`，供后续视频提示词合并判断使用。
- `framing`: 景别。景别不是装饰，而是观众与人物的心理距离。
- `camera_move`: 运镜方式。镜头运动不是炫技，而是注意力或情绪的运动。
- `action_desc`: 这个镜头里可见、可拍、可执行的动作和画面变化。

## Explicitly Excluded Fields

不得在 `storyboard.json` 中输出：

- `characters_in_shot`
- `location`
- `character_ids`
- `prop_ids`
- `asset_ids`
- `prompt_cn`
- `frame_strategy`
- `continuity_risk`
- `boundary_reason`
- `shot_function`
- `montage_relation`
- 任何资产清单或提示词字段

人物、场景、道具和资产拆分由 `asset_executor` 基于 `story.md + storyboard.json` 处理。

## Procedure

1. 读取 `story.md` 和 `style_bible.md`。
2. 继承艺术总监定义的画面风格、整体色调、光线风格和 AI 视觉执行要求。
3. 先拆戏剧节拍，不按句子或动作流水账切镜头。
4. 为每个节拍确定观看问题和视点策略。
5. 为每个镜头分配明确的叙事功能。
6. 设计相邻镜头的蒙太奇关系，避免素材堆叠。
7. 再把镜头功能转成景别、机位、运动、时长和可见动作。
8. 由导演创建 `scene_id`，同一连续场景/时空单元内的 shot 使用相同 `scene_id`。
9. 每个 shot 必须是独立镜头单位，不把连续镜头按时长硬拆。
10. 每个 shot 的 `duration_seconds` 必须 `>0` 且 `<=15`。
11. `action_desc` 必须具象、可见、可拍，不写裸抽象情绪。
12. 保存唯一输出：`outputs/storyboard.json`。

## Internal Quality Gate

- [ ] 分镜覆盖完整故事，不遗漏关键叙事节点。
- [ ] 每个镜头来自明确戏剧节拍，而不是平均切段。
- [ ] 每个镜头有内部镜头功能；没有功能的镜头已删除、合并或重写。
- [ ] 每个相邻镜头存在连续、因果、反应、对照、递进、省略、平行、隐喻、反讽或悬念关系。
- [ ] `shot_id` 全片唯一、连续，格式为 `S###`。
- [ ] `scene_id` 由导演创建，格式为 `SC###`，同一连续场景可复用。
- [ ] 每个镜头是独立镜头单位，不是连续镜头硬拆。
- [ ] 每个镜头 `duration_seconds > 0` 且 `<= 15`。
- [ ] `action_desc` 是具象动作描述。
- [ ] 具体构图、景别和镜头调度与 `style_bible.md` 不冲突。
- [ ] 不输出人物、场景、道具或资产拆分字段。
- [ ] 不输出图片或视频提示词。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `storyboard_director`
- `completed_phases`: 追加 `storyboard_director`
- `artifacts.storyboard_json`: `./outputs/storyboard.json`
- `next_phase.skill`: `asset_executor`

## Failure Handling

- 镜头超过 15 秒：重新设计为真实不同镜头，不允许拉长。
- 连续镜头被硬拆：合并为一个镜头，或设计反应镜头、插入镜头、视角变化、景别变化或蒙太奇切换。
- 镜头没有功能：删除、合并，或改成建立空间、反应、揭示信息、隐藏信息、转换视点等功能镜头。
- 相邻镜头没有关系：补足连续、因果、反应、对照、递进、省略、隐喻、反讽或悬念关系，否则合并。
- `action_desc` 只有抽象情绪：改写为微表情、肢体动作、光影、声音、物体细节或空间关系。
- 出现角色/场景/道具拆分或资产字段：删除该内容，交给 `asset_executor`。
- 与 `style_bible.md` 冲突：优先回到艺术方向阶段修订风格边界，或在分镜内调整镜头表达。
