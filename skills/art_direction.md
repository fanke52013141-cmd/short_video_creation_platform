# Skill: art_direction
**Version**: 2.0.0

## Source Prompt
`skills/raw_prompts/art_direction.source.md`

## Purpose
将已确认剧本转译为一页以内、可贯穿后续环节的视觉约束文件 `style_bible.md`。

本 Skill 不输出 `art_direction.json`，不生成分镜，不定义资产，不写视频提示词。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "reference_paths": [],
  "user_visual_notes": ""
}
```

## Outputs
```json
{
  "style_bible_path": "./outputs/style_bible.md"
}
```

## Required style_bible.md Format

`style_bible.md` 必须控制在一页以内，只允许包含以下四项：

```markdown
# Style Bible

## 整体色调
- 关键词1
- 关键词2
- 关键词3

## 光线风格
一句话说明。

## 构图倾向
一句话说明。

## 禁止出现的视觉元素
- 禁止项1
- 禁止项2
```

## Procedure
1. 读取 `story.md`，不得改写故事核心。
2. 若用户提供参考图或视觉笔记，优先继承其视觉方向。
3. 只抽取可持续影响全片的视觉约束。
4. 将整体色调限制为 3 个关键词。
5. 将光线风格限制为 1 句话。
6. 将构图倾向限制为 1 句话。
7. 明确禁止出现的视觉元素。
8. 输出 `outputs/style_bible.md`。

## Quality Gate
- [ ] 未改写故事核心。
- [ ] `style_bible.md` 一页以内。
- [ ] 整体色调不超过 3 个关键词。
- [ ] 光线风格只有 1 句话。
- [ ] 构图倾向只有 1 句话。
- [ ] 包含禁止出现的视觉元素。
- [ ] 未输出 `art_direction.json`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `art_direction`
- `completed_phases`: 追加 `art_direction`
- `artifacts.style_bible`: `./outputs/style_bible.md`
- `next_phase.skill`: `storyboard_director`

## Failure Handling
- 视觉方向过泛：压缩为四项硬约束。
- 输出超过一页：删除解释性段落和候选方案。
- 与故事情绪冲突：回到本 Skill 修订，不在下游临时覆盖。
