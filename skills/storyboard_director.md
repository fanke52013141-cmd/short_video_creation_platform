# Skill: storyboard_director
**Version**: 2.2.0

## Source Prompt
`skills/raw_prompts/storyboard_director.source.md`

## Purpose
将已确认故事和一页风格圣经转化为导演分镜序列 `storyboard.json`。

本 Skill 负责具体构图、景别、机位、镜头调度、动作节奏和 shot 结构化。它不得输出资产草表、资产 ID、角色拆分、场景拆分、道具拆分、图片提示词、视频提示词、音色定义或外部交接材料。

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

## shot_id vs scene_id

- `shot_id` 是镜头编号，表示第几个镜头，必须全片唯一并按顺序连续：`S001`、`S002`、`S003`。
- `scene_id` 是场景/时空单元编号，表示这个镜头属于哪一个连续场景，可以被多个 shot 复用：`SC001`、`SC002`。

示例：

```text
SC001 雨夜客厅：S001、S002、S003
SC002 走廊门口：S004、S005
```

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
- `framing`: 景别。
- `camera_move`: 运镜方式。
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
- 任何资产清单或提示词字段

人物、场景、道具和资产拆分由 `asset_executor` 基于 `story.md + storyboard.json` 处理。

## Procedure

1. 读取 `story.md` 和 `style_bible.md`。
2. 继承艺术总监定义的画面风格、整体色调、光线风格和 AI 视觉执行要求。
3. 按叙事节奏设计分镜，不平均切段。
4. 由导演创建 `scene_id`，同一连续场景/时空单元内的 shot 使用相同 `scene_id`。
5. 每个 shot 必须是独立镜头单位，不把连续镜头按时长硬拆。
6. 每个 shot 的 `duration_seconds` 必须 `>0` 且 `<=15`。
7. `action_desc` 必须具象、可见、可拍，不写裸抽象情绪。
8. `framing` 和 `camera_move` 必须服务剧情与风格圣经。
9. 保存唯一输出：`outputs/storyboard.json`。

## Internal Quality Gate

- [ ] 分镜覆盖完整故事，不遗漏关键叙事节点。
- [ ] `shot_id` 全片唯一、连续，格式为 `S###`。
- [ ] `scene_id` 由导演创建，格式为 `SC###`，同一连续场景可复用。
- [ ] 每个镜头是独立镜头单位，不是连续镜头硬拆。
- [ ] 每个镜头 `duration_seconds > 0` 且 `<= 15`。
- [ ] `action_desc` 是具象动作描述。
- [ ] 具体构图、景别和镜头调度与 `style_bible.md` 不冲突。
- [ ] 不输出人物、场景、道具或资产拆分字段。
- [ ] 不输出资产 ID。
- [ ] 不输出图片或视频提示词。
- [ ] 没有覆盖或冲突 `style_bible.md` 的核心视觉方向。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `storyboard_director`
- `completed_phases`: 追加 `storyboard_director`
- `artifacts.storyboard_json`: `./outputs/storyboard.json`
- `next_phase.skill`: `asset_executor`

## Failure Handling

- 镜头超过 15 秒：重新设计为真实不同镜头，不允许拉长。
- 连续镜头被硬拆：合并为一个镜头，或设计反应镜头、插入镜头、视角变化、景别变化或蒙太奇切换。
- `action_desc` 只有抽象情绪：改写为微表情、肢体动作、光影、声音、物体细节或空间关系。
- 出现角色/场景/道具拆分或资产字段：删除该内容，交给 `asset_executor`。
- 与 `style_bible.md` 冲突：优先回到艺术方向阶段修订风格边界，或在分镜内调整镜头表达。
