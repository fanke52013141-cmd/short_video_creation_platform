# Skill: story_generation
**Version**: 1.0.0

## Source Prompt
`skills/raw_prompts/story_generation.source.md`

## Purpose
将用户的模糊想法、主题、角色、世界观、片段或故事草稿，开发为适合 2-5 分钟 AI 短片生产的故事方案。

## Inputs
```json
{
  "idea_brief_path": "./inputs/idea_brief.md",
  "mode": "clarify | develop | finalize",
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
  "story_markdown_path": "./outputs/01_story/story.md",
  "story_json_path": "./outputs/01_story/story.json",
  "status": "needs_user_answer | ready_for_art_direction"
}
```

## Schema
`outputs/01_story/story.json` 必须满足 `schemas/story.schema.json`。

## Procedure
1. 读取 `story_generation.source.md` 作为主提示词，不改写其创作方法论。
2. 读取 `idea_brief_path`。
3. 如果信息不足，按源提示词的共创规则输出最多 2 个问题，并将状态标为 `needs_user_answer`。
4. 如果信息足够，输出短片故事方案。
5. 额外保存机器可读摘要到 `story.json`，用于后续视觉和分镜 Skill。

## Quality Gate
- [ ] 故事适合 2-5 分钟短片，不像长片梗概或小说章节。
- [ ] 人物数量、核心场景数量和关键情节动作保持可生产。
- [ ] 主角弱点、外部欲望、真实需要、对手压力、自我揭示清晰。
- [ ] 故事具体、可视化、可分镜。
- [ ] 输出明确进入下一阶段所需的故事信息。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `story_generation`
- `completed_phases`: 追加 `story_generation`
- `artifacts.story_markdown`: `./outputs/01_story/story.md`
- `artifacts.story_json`: `./outputs/01_story/story.json`
- `next_phase.skill`: `art_direction`

## Failure Handling
- 信息不足：输出问题，不生成最终故事。
- 故事过大：按源提示词压缩人物、场景、机制和支线。
- 下游需要 JSON 但故事只有 Markdown：补写 `story.json`，不改变故事正文。

