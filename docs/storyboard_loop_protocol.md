# Storyboard Director Protocol

本协议覆盖当前主流程的 `storyboard_director`。旧的 `outputs/03_storyboard/planning/`、`outputs/03_storyboard/shots/`、`SHOT_XXX_STORYBOARD.md` 和 `draft_asset_sheet.json` 结构已废弃；当前主流程只要求导演阶段输出：

```text
outputs/storyboard.json
```

分镜参考图提示词由后续 `storyboard_prompt_generator` 负责，资产拆分由后续 `asset_executor` 负责。

## 输入

```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "max_shot_duration_seconds": 15
}
```

## 输出

`outputs/storyboard.json` 的每个 shot 只包含：

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

## 字段规则

### shot_id

- 格式：`S###`。
- 从 `S001` 开始。
- 全片唯一。
- 必须按顺序连续。

### scene_id

- 格式：`SC###`。
- 表示连续场景 / 时空单元。
- 同一连续场景内多个 shot 可以共用同一个 `scene_id`。
- 场景、地点、时间或叙事空间发生切换时，创建新的 `scene_id`。

### duration_seconds

- 必须大于 0。
- 必须小于或等于 15。
- 后续 `video_prompt_generator` 会用它判断 `S### → V###` 合并总时长。

### action_desc

- 必须写可见、可拍、可执行的动作和画面变化。
- 不要只写抽象情绪，例如“她很难过”。
- 应落地为微表情、肢体动作、视线、空间距离、光影、声音或物体状态。

## 明确禁止输出的字段

`storyboard.json` 不得包含：

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

这些内容分别交给后续阶段：

- 人物、场景、道具和资产映射：`asset_executor`。
- 分镜参考图提示词：`storyboard_prompt_generator`。
- 视频提示词合并和引用：`video_prompt_generator`。

## 导演方法

导演阶段可以内部使用以下方法分析，但不要把这些分析字段写入 `storyboard.json`：

```text
剧本 → 戏剧节拍 → 观看问题 → 视点策略 → 镜头功能 → 镜头参数 → 蒙太奇关系
```

每个镜头必须回答：观众此刻看见什么。  
每个剪接必须回答：观众因此想到什么。

## 镜头边界

合法镜头边界包括：

- 景别变化。
- 机位变化。
- 视角变化。
- 焦点变化。
- 主体变化。
- 空间变化。
- 时间变化。
- 反应镜头。
- 插入镜头。
- 信息揭示镜头。
- 蒙太奇关系变化。

不允许新建 shot 的情况：

- 同一机位、同一景别、同一空间、同一运动路径中，一个动作连续发生，只是因为时长长而被拆成两段。
- 前后 shot 画面几乎相同，只是动作从“开始”变成“继续”。
- 镜头边界没有新的叙事信息、观看角度、情绪层级、空间信息或蒙太奇意义。

## 自检

分镜阶段完成后必须通过：

```bash
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase storyboard
```

检查重点：

- `storyboard.json` 存在且是对象。
- `shots` 非空。
- `shot_id` 从 `S001` 连续递增。
- `scene_id` 符合 `SC###`。
- 每个 shot 时长大于 0 且不超过 15 秒。
- 没有后置阶段字段。
- 每个 `action_desc` 是具象可见画面，而不是裸抽象情绪。
