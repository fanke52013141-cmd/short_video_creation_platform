# Skill: story_generation
**Version**: 1.0.1

## Source Prompt
`skills/raw_prompts/story_generation.source.md`

## Purpose
将用户的模糊想法、主题、角色、世界观、片段或故事草稿，处理为适合 2-5 分钟 AI 短片生产的故事产物。

本 Skill 的首要任务不是默认重写故事，而是先判断用户输入完整度：
- 用户故事已经完整时，优先保真整理、结构化提取和短片可执行性检查。
- 用户故事不完整或存在明显结构缺口时，才进行诊断优化。
- 用户只提供模糊想法时，先提出少量关键问题，不直接生成完整故事。

## Core Methodology

### 1. Complete Story Preservation Mode
适用：用户已经提供完整故事，且主角、目标、冲突、推进、高潮和结尾基本清晰。

规则：
- 不默认重写用户故事。
- 保留用户的主角、核心设定、人物关系、主题方向、关键事件和结局。
- 只做轻量结构整理、短片可执行性检查、必要的缺口标注和 `story.json` 结构化提取。
- 如果发现优化空间，作为“可选优化建议”列出，不静默改写原故事。
- 若故事已能支撑视觉风格和分镜阶段，可直接标记为 `ready_for_art_direction`。

### 2. Draft Diagnosis Optimization Mode
适用：用户提供了故事草稿、大纲、剧情片段或完整但存在明显问题的故事。

规则：
- 先诊断主要缺口，再优化。
- 优先保留用户已有材料，不重建一个无关故事。
- 只补强薄弱环节：主角弱点、外部欲望、真实需要、压力系统、错误计划、升级链、高潮选择、自我揭示或新平衡。
- 输出中必须区分 `preserved_elements` 和 `optimized_elements`。

### 3. Exploration Question Mode
适用：用户只提供模糊主题、抽象概念或很少信息。

规则：
- 不直接生成完整故事。
- 每轮最多提出 1-2 个高信息增益问题。
- 状态标记为 `needs_user_answer`。

### 4. Full Story Development Mode
适用：用户明确希望 Codex 从核心创意发展完整故事，或明确允许合理假设。

规则：
- 使用源提示词中的 Truby 故事引擎。
- 保持 2-5 分钟短片可执行性。
- 明确说明采用了哪些默认假设。

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
  "story_markdown_path": "./outputs/01_story/story.md",
  "story_json_path": "./outputs/01_story/story.json",
  "method": "complete_story_preservation | draft_diagnosis_optimization | exploration_question | full_story_development",
  "status": "needs_user_answer | draft_diagnosed | story_structured | story_optimized | ready_for_art_direction"
}
```

## Schema
`outputs/01_story/story.json` 必须满足 `schemas/story.schema.json`。

## Procedure
1. 读取 `story_generation.source.md` 作为主提示词，不改写其创作方法论。
2. 读取 `idea_brief_path`。
3. 先判断用户输入完整度：完整故事、半完整草稿、模糊想法、或明确要求完整开发。
4. 如果是完整故事，进入保真整理模式：不改变核心故事，只结构化整理并写入 `story.md` 和 `story.json`。
5. 如果是半完整草稿，进入诊断优化模式：先列出保留内容和缺口，再补强弱项。
6. 如果信息不足，按源提示词的共创规则输出最多 2 个问题，并将状态标为 `needs_user_answer`。
7. 如果用户明确要求完整开发且输入具备最低生成条件，输出完整短片故事方案，并说明默认假设。
8. 额外保存机器可读摘要到 `story.json`，用于后续视觉和分镜 Skill。

## Quality Gate
- [ ] 已先判断用户输入完整度，没有默认重写完整故事。
- [ ] 完整故事模式下保留了用户主角、主题、关键事件、人物关系和结局。
- [ ] 优化模式下明确区分了保留内容和优化内容。
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
- `artifacts.story_generation_method`: 当前采用的方法模式
- `next_phase.skill`: `art_direction`

## Failure Handling
- 信息不足：输出问题，不生成最终故事。
- 用户故事完整但仍有小缺口：标注缺口和可选优化建议，不静默重写。
- 用户故事过大：先说明压缩原因，再压缩人物、场景、机制和支线。
- 下游需要 JSON 但故事只有 Markdown：补写 `story.json`，不改变故事正文。
