# Skill: art_direction
**Version**: 1.0.0

## Source Prompt
`skills/raw_prompts/art_direction.source.md`

## Purpose
将已确认故事转译为统一、可执行、可传递给后续环节的视觉方向系统。

## Inputs
```json
{
  "story_markdown_path": "./outputs/01_story/story.md",
  "story_json_path": "./outputs/01_story/story.json",
  "reference_paths": [],
  "platform": "to_be_confirmed",
  "duration_minutes": "2-5"
}
```

## Outputs
```json
{
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "art_direction_json_path": "./outputs/02_art_direction/art_direction.json"
}
```

## Procedure
1. 读取 `art_direction.source.md` 作为主提示词。
2. 将故事视为只读数据，不改写剧情核心。
3. 输出视觉方向系统：风格、色彩、灯光、材质、摄影倾向、禁用项、后续交接规范。
4. 另存结构化 JSON，供分镜和资产提示词引用。

## Quality Gate
- [ ] 没有改写故事核心。
- [ ] 视觉风格、色调、灯光、材质、镜头语言可执行。
- [ ] 明确“应该长什么样”和“不应该长什么样”。
- [ ] 能被分镜、角色、场景、视频提示词继续引用。
- [ ] 不越界生成逐镜头分镜或完整视频提示词。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `art_direction`
- `completed_phases`: 追加 `art_direction`
- `artifacts.style_bible`: `./outputs/02_art_direction/style_bible.md`
- `artifacts.art_direction_json`: `./outputs/02_art_direction/art_direction.json`
- `next_phase.skill`: `storyboard_director`

## Failure Handling
- 与故事情绪冲突：回到本 Skill 修订视觉方向，不在分镜阶段临时覆盖。
- 输出过泛：要求补充可执行的色彩、灯光、材质和禁止项。

