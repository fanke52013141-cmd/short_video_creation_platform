# Skill: storyboard_static_frame_variant
**Version**: 1.0.0

## Source Prompt
`skills/raw_prompts/storyboard_static_frame_variant.source.md`

## Purpose
作为分镜主 Skill 的可选变体，用于需要静态关键帧、图像生成或首尾帧锁定的生产路径。

## Inputs
```json
{
  "story_markdown_path": "./outputs/01_story/story.md",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "use_case": "keyframe | first_frame | last_frame | first_last_frame"
}
```

## Outputs
```json
{
  "static_frame_storyboard_path": "./outputs/03_storyboard/static_frame_storyboard.md",
  "static_frame_storyboard_json_path": "./outputs/03_storyboard/static_frame_storyboard.json"
}
```

## Procedure
1. 仅当需要静态定格图像、首帧、尾帧或关键帧生产时使用。
2. 保留源提示词中的核心铁律：画面提示词描述一张冻结画面，不描述过程。
3. 产出可供图像生成或视频首尾帧控制的画面描述。

## Quality Gate
- [ ] 每条画面提示词都能对应一张静态图。
- [ ] 没有使用只能由视频过程呈现的描述。
- [ ] 静态帧资产 ID 与主资产清单一致。

## Checkpoint Update
可选阶段。通过后更新：
- `artifacts.static_frame_storyboard`: `./outputs/03_storyboard/static_frame_storyboard.md`

## Failure Handling
- 如果输出混入动态过程描述，重写为冻结瞬间。

