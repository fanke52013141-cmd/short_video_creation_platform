# Skill: storyboard_prompt_generator
**Version**: 1.1.0

## Purpose
将导演分镜转化为可生成分镜参考图的中文图片提示词。

本 Skill 按 `shot_id` 循环工作。每次只处理一个 `S###`，输出一份分镜参考图提示词。

它还必须执行两件事：

1. 当前分镜是否需要引用上一分镜图片作为站位参考。
2. 从已批准的 `video_segment_plan.json` 读取当前分镜的 `first_frame`、`last_frame` 或 `keyframe` 角色，不再自行猜测。

## Inputs

单个 shot 调用：

```json
{
  "storyboard_json_path": "./outputs/storyboard.json",
  "style_bible_path": "./outputs/style_bible.md",
  "shot_asset_map_path": "./outputs/shot_asset_map.json",
  "video_segment_plan_path": "./outputs/video_segment_plan.json",
  "asset_image_root": "./outputs/assets",
  "storyboard_image_root": "./outputs/storyboards",
  "shot_id": "S002",
  "output_prompt_path": "./outputs/approved/storyboard_prompts/S002.md"
}
```

可选输入：

```json
{
  "story_markdown_path": "./outputs/story.md"
}
```

`story.md` 只在 `action_desc` 信息不足时作为补充，不作为默认重写依据。

## Outputs

```json
{
  "shot_id": "S002",
  "output_prompt_path": "./outputs/approved/storyboard_prompts/S002.md",
  "frame_role": "keyframe",
  "uses_previous_storyboard_reference": true,
  "previous_storyboard_reference": {
    "source_shot_id": "S001",
    "source_path": "./outputs/storyboards/S001.png",
    "reference_purpose": "placement_anchor"
  }
}
```

最终也可以汇总为：

```text
./outputs/storyboard_prompts.md
```

## Previous Storyboard Reference Policy

不是所有相邻分镜都引用上一分镜。只有满足以下条件时才引用：

1. 当前 shot 与上一 shot 连续。
2. 两个 shot 的 `scene_id` 相同。
3. 人物、场景或主要道具存在明显站位延续关系。
4. 当前 shot 不是新的空间布局、时间跳跃或叙事空间切换。
5. 上一分镜图已经存在，或将按固定路径生成。

引用上一分镜时，只把它作为站位参考，不作为表情、动作、服装、光影的强制复制。

推荐写法：

```text
参考上一分镜 S001 的站位关系，只继承人物相对位置、朝向、空间比例和场景连续性；当前画面动作、表情和景别以 S002 为准。
```

必须避免：

- 跨 `scene_id` 引用上一分镜。
- 时间跳跃后继续引用上一分镜。
- 新构图、新调度却硬套上一分镜站位。
- 把上一分镜当作完整画面复制。

## Frame Role Policy

每个分镜参考图必须从 `video_segment_plan.json` 读取 `frame_role`：

```text
first_frame | last_frame | keyframe
```

不得覆盖或重新推断已规划角色。若当前 shot 不在 plan 中，停止并返回 `video_segment_planner`。

### first_frame
用于视频段落的起始画面。通常适合：

- 新场景的第一个 shot。
- 新空间关系首次建立。
- 人物站位、场景布局、镜头轴线需要被锁定。
- 预计后续同场景镜头会延续该站位。

### last_frame
用于视频段落的目标画面或动作结果。通常适合：

- 连续动作的终点。
- 情绪反应的落点。
- 人物姿态、道具位置或表情需要在视频末端准确抵达。
- 与前一个 shot 存在强动作连续性，且当前 shot 是这个动作的完成状态。

### keyframe
用于中间状态或重要参考画面。通常适合：

- 同一视频段落中间的过渡状态。
- 远景到近景、人物到手部细节等景别变化。
- 对动作、表情、道具或站位有约束价值，但不一定是视频起点或终点。

## Procedure

1. 读取 `storyboard.json`，定位当前 `shot_id`。
2. 读取 `style_bible.md`，继承画面风格、整体色调、光线风格和 AI 视觉执行要求。
3. 读取 `shot_asset_map.json`，查询当前 shot 对应的人物、场景和必要道具。
4. 查找 `asset_image_root` 中已生成的人物、场景、必要道具图。
5. 判断是否引用上一分镜图片作为站位参考。
6. 从视频段计划读取当前分镜图的 `frame_role`。
7. 把导演分镜的 `framing`、`camera_move`、`action_desc` 改写为静态分镜参考图提示词。
8. 不生成视频动作时长，不合并镜头，不决定最终视频提示词。

## Output Format

```markdown
# S002 分镜参考图提示词

## 分镜角色
frame_role: keyframe

## 上一分镜站位参考
uses_previous_storyboard_reference: true
source_shot_id: S001
source_path: ./outputs/storyboards/S001.png
reference_purpose: placement_anchor
reason: 同一 scene_id，人物与手机位置延续，当前为同一动作的近景反应。

## 资产声明区
@林小满_雨夜居家装（人物资产）
@雨夜客厅场景（场景资产）
手机（正文控制道具）

## 中文分镜图提示词
参考上一分镜 S001 的站位关系，只继承人物相对位置、朝向、空间比例和场景连续性；当前画面动作、表情和景别以 S002 为准。近景，林小满握紧手机，嘴唇微张又抿紧，眼眶泛红但没有眼泪。继承 style_bible.md 的冷蓝雨夜与暖黄室内灯光。画面无字幕、无 Logo、无水印。
```

## Quality Gate

- [ ] 每个 `storyboard.json` 中的 shot 都有对应提示词。
- [ ] 每个 shot 都明确 `frame_role`，且与视频段计划一致。
- [ ] 每个 shot 都明确是否引用上一分镜。
- [ ] 引用上一分镜时，必须说明只用于站位、朝向、空间比例和连续性。
- [ ] 不跨 `scene_id` 引用上一分镜。
- [ ] 每条提示词注入 `style_bible.md` 的核心约束。
- [ ] 资产引用来自 `shot_asset_map.json`。
- [ ] 不新增未登记资产。
- [ ] 输出中文。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `storyboard_prompt_generator`
- `completed_phases`: 追加 `storyboard_prompt_generator`
- `artifacts.storyboard_prompts`: `./outputs/storyboard_prompts.md`
- `next_phase.skill`: `storyboard_image_generation`

## Failure Handling

- 某 shot 缺少资产映射：返回 `asset_executor` 补齐。
- 静态分镜提示词无法生成：返回 `storyboard_director` 具象化 `action_desc`。
- 风格约束缺失：返回 `art_direction` 修订 `style_bible.md`。
- 需要上一分镜站位参考但上一分镜图片不存在：先生成上一分镜图片，再生成当前分镜。
