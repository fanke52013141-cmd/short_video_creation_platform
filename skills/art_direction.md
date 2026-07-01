# Skill: art_direction
**Version**: 1.0.1

## Source Prompt
`skills/raw_prompts/art_direction.source.md`

## Purpose
将已确认故事转译为统一、可执行、可传递给后续环节的视觉方向系统。

本 Skill 必须尊重用户提供的明确视觉建议。若用户提供了明确参考图、参考画面、风格图或 moodboard，本阶段不应默认重新发散独立风格，而应优先解析参考图，并在用户参考图的视觉体系内进行拓展、统一和生产化定义。

## Core Methodology

### 1. Reference Image First Mode
适用：用户提供了明确参考图、风格图、截图、moodboard 或其他视觉参考。

规则：
- 将参考图视为最高优先级的视觉输入，但不得直接复制具体 IP、角色、构图或受版权保护的独特资产。
- 先解析参考图的视觉语法：色彩、灯光、材质、构图、真实度、风格化程度、镜头气质、空间气质、角色/场景视觉倾向。
- 不重新提出与参考图冲突的主视觉方向。
- 只在参考图风格边界内做拓展：统一风格、补充缺失规则、定义可复用的视觉系统。
- 如果参考图与故事情绪、平台目标或 AI 视频稳定性冲突，必须先指出冲突，再给出“保留参考图核心 + 修正不可执行部分”的方案。

### 2. User Visual Direction Preservation Mode
适用：用户没有给图，但给出了明确视觉建议、风格关键词、禁用方向或目标平台审美。

规则：
- 优先继承用户视觉建议。
- 不默认推翻用户指定风格。
- 只补全用户未定义的色彩、灯光、材质、摄影、负面风格和下游交接规则。

### 3. Open Art Direction Mode
适用：用户没有提供明确视觉参考或视觉建议。

规则：
- 根据故事生成 3 个候选视觉方向。
- 比较后推荐一个主视觉方向。
- 明确说明为什么选择它，以及为什么不选择其他方向。

## Inputs
```json
{
  "story_markdown_path": "./outputs/01_story/story.md",
  "story_json_path": "./outputs/01_story/story.json",
  "reference_paths": [],
  "user_visual_notes": "",
  "platform": "to_be_confirmed",
  "duration_minutes": "2-5"
}
```

## Outputs
```json
{
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "art_direction_json_path": "./outputs/02_art_direction/art_direction.json",
  "method": "reference_image_first | user_visual_direction_preservation | open_art_direction"
}
```

## Schema
`outputs/02_art_direction/art_direction.json` 必须满足 `schemas/art_direction.schema.json`。

## Procedure
1. 读取 `art_direction.source.md` 作为主提示词。
2. 读取 `story_markdown_path` 和 `story_json_path`，将故事视为只读数据，不改写剧情核心。
3. 检查 `reference_paths` 与 `user_visual_notes`：
   - 如果存在明确参考图，进入 Reference Image First Mode。
   - 如果存在明确视觉建议，进入 User Visual Direction Preservation Mode。
   - 如果没有明确视觉输入，进入 Open Art Direction Mode。
4. 有参考图时，先解析参考图的视觉语法，再基于该风格做拓展，不另起炉灶。
5. 输出视觉方向系统：风格、色彩、灯光、材质、摄影倾向、禁用项、后续交接规范。
6. 另存结构化 JSON，供分镜、资产提示词和视频提示词引用。

## Quality Gate
- [ ] 没有改写故事核心。
- [ ] 如果用户提供参考图，已优先继承参考图风格，而不是重新发散无关风格。
- [ ] 如果参考图存在冲突，已说明保留项、修正项和原因。
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
- `artifacts.art_direction_method`: 当前采用的方法模式
- `next_phase.skill`: `storyboard_director`

## Failure Handling
- 参考图与故事情绪冲突：保留参考图可用视觉核心，修正冲突部分，不直接推翻用户参考图。
- 参考图无法支撑完整短片：说明风险，抽象出可复用视觉语法，再补充可执行规则。
- 与故事情绪冲突：回到本 Skill 修订视觉方向，不在分镜阶段临时覆盖。
- 输出过泛：要求补充可执行的色彩、灯光、材质和禁止项。
