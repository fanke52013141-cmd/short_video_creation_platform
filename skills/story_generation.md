# Skill: story_generation
**Version**: 3.0.0

## Source Prompt
`skills/raw_prompts/story_generation.source.md`

## Purpose
将用户的原始想法、草稿或半成品故事优化为一个可用于后续艺术方向、导演分镜和资产执行的短视频剧本。

本 Skill 只负责剧本创作与剧本优化。它不负责结构化镜头、不负责资产拆分、不负责资产命名、不负责图片提示词、不负责视频提示词。

**核心原则：先把剧本写好。不要为了下游字段提前分散模型注意力。**

## Inputs
```json
{
  "idea_brief_path": "./inputs/idea_brief.md",
  "mode": "auto | preserve | diagnose | clarify | develop | finalize",
  "constraints": {
    "duration_minutes": "2-5",
    "tone": "",
    "must_keep": [],
    "avoid": []
  }
}
```

## Outputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "status": "needs_user_answer | ready_for_art_direction"
}
```

## Output Contract

唯一主产物是：

```text
./outputs/story.md
```

不得输出 `story.json`、`story_index.json` 或任何故事结构化 JSON。结构化职责后移：

- 镜头结构化交给 `storyboard_director`。
- 人物、场景、道具和资产拆分交给 `asset_executor`。
- 视频生成计划交给 `video_prompt_generator`。

## story.md Must Include

`story.md` 应围绕剧本本身组织，而不是围绕下游字段组织。建议包含：

- 标题
- 一句话故事
- 完整剧本正文或完整短片故事方案
- 主要人物说明
- 主要场景说明
- 剧情段落
- 关键情绪推进
- 必须保留的用户设定
- 必要生产备注

## Hard Rules

- 不输出结构化 JSON。
- 不输出分镜。
- 不输出镜头编号。
- 不输出资产清单。
- 不拆角色状态。
- 不拆场景资产。
- 不拆道具资产。
- 不写图片提示词。
- 不写视频提示词。
- 不为了下游方便牺牲剧本文学性、叙事完整性和用户原意。

## Procedure

1. 读取 `story_generation.source.md` 作为主提示词。
2. 读取 `idea_brief.md`。
3. 判断输入类型：模糊想法、半成品草稿、完整故事、诊断请求、润色请求或完整开发请求。
4. 如果信息不足，只问 1-2 个高信息增益问题，不生成最终剧本。
5. 如果用户已有完整故事，优先保真整理，不擅自改人物关系、核心事件和结局。
6. 如果用户需要开发故事，补足人物动机、冲突、转折、结尾和情绪推进。
7. 输出唯一主文件：`outputs/story.md`。

## Quality Gate

- [ ] 剧本可读，核心故事清楚。
- [ ] 人物动机清楚。
- [ ] 外部冲突明确。
- [ ] 情绪推进明确。
- [ ] 适合短视频长度。
- [ ] 人物和核心场景数量可生产。
- [ ] 保留用户核心想法、关键人物、核心事件和结局。
- [ ] 没有输出任何结构化生产文件。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `story_generation`
- `completed_phases`: 追加 `story_generation`
- `artifacts.story_md`: `./outputs/story.md`
- `next_phase.skill`: `art_direction`

## Failure Handling

- 信息不足：输出问题，不生成最终故事。
- 用户已有完整故事但要求整理：只保真整理，不默认重写。
- 故事过大：压缩人物、场景、机制和支线，但说明压缩原因。
- 下游需要镜头或资产结构化信息：停止在本 Skill，不代替导演或资产执行官。