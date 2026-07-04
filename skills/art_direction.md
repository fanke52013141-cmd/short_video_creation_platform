# Skill: art_direction
**Version**: 2.1.0

## Source Prompt
`skills/raw_prompts/art_direction.source.md`

## Purpose
将用户已确认锁定的 `story.md` 转译为可供导演、资产执行官和后续提示词阶段继承的视觉方向。

本 Skill 是艺术总监阶段，不是分镜阶段。它负责画面风格、整体色调、光线风格和 AI 视觉执行要求；不负责具体构图、镜头拆分、资产拆分或提示词生成。

如果用户已经提供明确艺术风格、参考图或视觉偏好，本 Skill 必须优先继承并补全执行规则。如果用户没有提供明确视觉方向，本 Skill 应先提出候选方案让用户选择，不应一锤定音。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "reference_paths": [],
  "user_visual_notes": "",
  "mode": "auto | propose_options | refine | finalize"
}
```

## Outputs
```json
{
  "style_bible_path": "./outputs/style_bible.md",
  "status": "needs_user_choice | ready_for_storyboard"
}
```

## Output Modes

### 1. 用户已有明确视觉方向

直接基于用户输入补全 `style_bible.md`，状态为 `ready_for_storyboard`。

### 2. 用户没有明确视觉方向

先在对话中提出 2-3 个候选视觉方案，让用户选择或混合，不直接定稿。用户确认后再输出 `style_bible.md`。

### 3. 用户要求调整视觉方向

基于用户反馈修订 `style_bible.md`，不得改剧情。

## Required style_bible.md Format

`style_bible.md` 必须控制在一页以内，只允许包含以下四项：

```markdown
# Style Bible

## 画面风格
一句话定义画面介质、真实度、风格化程度和整体观感。

## 整体色调
- 关键词1
- 关键词2
- 关键词3

## 光线风格
一句话说明主要光源、冷暖关系、阴影气质。

## AI 视觉执行要求
- AI 生成时应该保持的视觉规则1
- AI 生成时应该保持的视觉规则2
- AI 生成时应该避免的明显偏差，仅限会破坏风格或交付的必要项
```

## Boundary

- 具体构图由 `storyboard_director` 在分镜阶段决定。
- 艺术总监可以描述“画面气质”，但不得规定每个镜头的构图、景别或机位。
- 不输出“构图倾向”作为硬字段。
- 不输出“禁止出现的视觉元素”作为独立硬字段。
- 不输出 `art_direction.json`。
- 不改写剧情。
- 不生成资产清单。
- 不写图片提示词或视频提示词。

## Procedure

1. 读取用户已确认锁定的 `story.md`。
2. 判断用户是否提供参考图、艺术风格、画面偏好或禁用方向。
3. 如果用户有明确视觉方向，优先继承用户方向，只补全画面风格、色调、光线和 AI 执行要求。
4. 如果用户没有明确视觉方向，提出 2-3 个候选方案，等待用户选择，不直接输出最终 `style_bible.md`。
5. 用户确认后，输出一页以内 `outputs/style_bible.md`。
6. 将状态置为 `ready_for_storyboard`，进入导演阶段。

## Quality Gate

- [ ] 使用的是用户已确认锁定的 `story.md`。
- [ ] 如果用户提供视觉方向，已优先继承而不是推翻。
- [ ] 如果用户未提供视觉方向，先给候选方案而不是直接定稿。
- [ ] `style_bible.md` 一页以内。
- [ ] 包含画面风格、整体色调、光线风格、AI 视觉执行要求。
- [ ] 不包含具体构图、分镜、镜头编号或资产拆分。
- [ ] 未输出 `art_direction.json`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `art_direction`
- `completed_phases`: 追加 `art_direction`
- `artifacts.style_bible`: `./outputs/style_bible.md`
- `next_phase.skill`: `storyboard_director`

## Failure Handling

- 用户没有视觉方向：先给候选方案，状态为 `needs_user_choice`。
- 用户视觉方向过泛：补齐画面风格、色调、光线和 AI 执行规则。
- 输出含具体构图或分镜：删除该内容，交给 `storyboard_director`。
- 与故事情绪冲突：说明冲突点，给用户可选修正方案，不直接改剧情。
