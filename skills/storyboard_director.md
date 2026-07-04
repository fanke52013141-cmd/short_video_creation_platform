# Skill: storyboard_director
**Version**: 2.1.0

## Source Prompt
`skills/raw_prompts/storyboard_director.source.md`

## Purpose
将已确认故事和一页风格圣经转化为导演分镜序列 `storyboard.json`。

本 Skill 负责具体构图、景别、机位、镜头调度、动作节奏和 shot 结构化。它不得输出资产草表、资产 ID、图片提示词、视频提示词、音色定义或外部交接材料。

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

## Required Shot Fields
每个 shot 只包含：

```json
{
  "shot_id": "S001",
  "scene_id": "SCENE_001",
  "duration_seconds": 6,
  "framing": "中景",
  "camera_move": "缓慢推近",
  "action_desc": "少女把旧皮箱拉到桌边，手指停在生锈锁扣上",
  "characters_in_shot": ["少女"],
  "location": "破旧公寓"
}
```

## Procedure
1. 读取 `story.md` 和 `style_bible.md`。
2. 继承艺术总监定义的画面风格、整体色调、光线风格和 AI 视觉执行要求。
3. 按叙事节奏设计分镜，不平均切段。
4. 每个 shot 必须是独立镜头单位，不把连续镜头按时长硬拆。
5. 每个 shot 的 `duration_seconds` 必须 `>0` 且 `<=15`。
6. `action_desc` 必须具象、可见、可拍，不写裸抽象情绪。
7. `framing` 和 `camera_move` 必须服务剧情与风格圣经。
8. `characters_in_shot` 使用角色特征名或故事中的明确角色名，不使用 `CharA`、`CHAR_001`。
9. `location` 使用场景名，不使用 `ENV_001`。
10. 保存 `outputs/storyboard.json`。

## Internal Quality Gate
- [ ] 分镜覆盖完整故事，不遗漏关键叙事节点。
- [ ] 每个镜头是独立镜头单位，不是连续镜头硬拆。
- [ ] 每个镜头 `duration_seconds <= 15`。
- [ ] `action_desc` 是具象动作描述。
- [ ] 具体构图、景别和镜头调度与 `style_bible.md` 不冲突。
- [ ] 不输出资产草表。
- [ ] 不定义资产 ID。
- [ ] 不输出音色定义。
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
- 出现资产 ID 或资产草表：删除该内容，交给 `asset_executor`。
- 与 `style_bible.md` 冲突：优先回到艺术方向阶段修订风格边界，或在分镜内调整镜头表达。
