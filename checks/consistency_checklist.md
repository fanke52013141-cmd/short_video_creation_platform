# Consistency Checklist

## 能力守恒
- [ ] Agent.md 中每个关键动作都有对应 Skill。
- [ ] 每个 Skill 都在 Agent.md 的流程中被调用。
- [ ] 原始提示词源文件已保存在 `skills/raw_prompts/`。

## 数据连续
- [ ] `story_generation` 输出能被 `art_direction` 读取。
- [ ] `art_direction` 输出能锁定 `storyboard_director` 的风格边界。
- [ ] `storyboard_director` 输出的资产 ID 能被 `asset_manifest_builder` 解析。
- [ ] `asset_manifest.json` 中的所有资产都能生成资产提示词。
- [ ] `shot_video_prompt_generator` 不引用不存在的资产 ID。
- [ ] `checkpoint.generation_modes.image_generation` 已明确为 `external_manual` 或 `internal_codex`，不是 `ask_user`。

## 资产一致
- [ ] 角色 ID 使用 `CHAR_001` 格式。
- [ ] 场景 ID 使用 `ENV_001` 格式。
- [ ] 道具 ID 使用 `PROP_001` 格式。
- [ ] 状态变体按 A/B/C 标记。
- [ ] 母题资产在叙事骨架、资产表、分镜中一致。
- [ ] 人物不同年龄、服装、状态拆成独立资产图，不放进同一张最终资产图。
- [ ] 文字类道具仍有图片提示词或图片资产，不被跳过。

## 视频提示词一致
- [ ] 每个 shot 都有建议时长。
- [ ] 每个 shot 都声明对应 `@SHOT_XXX_STORYBOARD`。
- [ ] `@SHOT_XXX_STORYBOARD` 被标注为首帧参考、尾帧参考或关键帧参考。
- [ ] 视频提示词默认只 `@` 分镜图、人物和场景。
- [ ] 视频提示词中默认没有 `@PROP`。
- [ ] 视频提示词只输出中文，不包含 `【English Prompt】`。
- [ ] 道具在正文中有清晰画面描述。

## 风格一致
- [ ] 分镜没有覆盖 `style_bible.md` 的核心风格。
- [ ] 角色、场景、道具提示词都引用视觉风格圣经。
- [ ] 视频提示词继承分镜与资产，不重新发明风格。

## 交付完整
- [ ] `outputs/01_story/` 有故事产物。
- [ ] `outputs/02_art_direction/` 有视觉风格产物。
- [ ] `outputs/03_storyboard/` 有分镜产物。
- [ ] `outputs/04_assets/` 有资产注册表和资产提示词。
- [ ] `outputs/05_video_prompts/` 有逐镜头视频提示词。
- [ ] `production_status.csv` 存在，用于记录外部生成或内部生成状态。
- [ ] `outputs/07_final_delivery/` 有最终清单和审查报告。
