# Skill: story_generation
**Version**: 2.0.0

## Source Prompt
`skills/raw_prompts/story_generation.source.md`

## Purpose
将 `idea_brief.md` 转化为适合后续风格、分镜和资产提取的短视频剧本。

本 Skill 的输出必须轻量。它不负责视觉风格、分镜、资产命名或视频提示词。

## Inputs
```json
{
  "idea_brief_path": "./inputs/idea_brief.md",
  "mode": "auto | preserve | diagnose | clarify | develop | finalize",
  "constraints": {
    "duration_minutes": "2-5",
    "max_characters": 3,
    "max_core_locations": 4
  }
}
```

## Outputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "story_json_path": "./outputs/story.json",
  "status": "needs_user_answer | ready_for_art_direction"
}
```

## story.md Must Include
- 标题
- 一句话故事
- 角色列表
- 场景列表
- 剧情段落
- 必要生产备注

## story.json Contract
`outputs/story.json` 必须满足 `schemas/story.schema.json`，只保留：

- `title`
- `logline`
- `duration_minutes`
- `genre`
- `theme`
- `scenes`
- `characters`
- `plot_segments`
- `production_notes`

删除过度复杂的角色心理层、多余元数据字段和不会被下游消费的分析字段。

## Procedure
1. 读取 `story_generation.source.md` 作为主提示词。
2. 读取 `idea_brief.md`。
3. 判断输入完整度：完整故事、半完整草稿、模糊想法或明确要求完整开发。
4. 完整故事优先保真整理，不静默重写。
5. 半完整草稿先诊断缺口，再做最小必要补强。
6. 信息不足时最多提出 1-2 个高信息增益问题，不生成最终剧本。
7. 输出 `story.md` 和精简 `story.json`。

## Quality Gate
- [ ] 保留用户核心想法、关键人物、核心事件和结局。
- [ ] 故事适合 2-5 分钟短视频。
- [ ] 角色数量和核心场景数量可生产。
- [ ] 场景列表、角色列表、剧情段落足够支撑资产提取。
- [ ] `story.json` 只包含下游必要字段。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `story_generation`
- `completed_phases`: 追加 `story_generation`
- `artifacts.story_md`: `./outputs/story.md`
- `artifacts.story_json`: `./outputs/story.json`
- `next_phase.skill`: `art_direction`

## Failure Handling
- 信息不足：输出问题，不生成最终故事。
- 故事过大：压缩人物、场景、机制和支线。
- 下游需要 JSON 但故事只有 Markdown：补写 `story.json`，不改变故事正文。
