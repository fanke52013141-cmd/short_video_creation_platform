# Consistency Checklist

## 能力守恒
- [ ] Agent.md 中每个关键动作都有对应 Skill。
- [ ] 每个 Skill 都在 Agent.md 的流程中被调用。
- [ ] 原始提示词源文件已保存在 `skills/raw_prompts/`。
- [ ] `config/config.yaml` 中的 Skill 版本与各 Skill 文件头一致。
- [ ] 核心 JSON 产物在 `schemas/` 中有对应契约。

## 数据连续
- [ ] `story_generation` 输出能被 `art_direction` 读取。
- [ ] `art_direction` 输出能锁定 `storyboard_director` 的风格边界。
- [ ] `storyboard_sequence_review` 在 `storyboard_director` 之后、`asset_manifest_builder` 之前执行。
- [ ] `storyboard_director` 输出的资产 ID 能被 `asset_manifest_builder` 解析。
- [ ] `asset_manifest.json` 中的所有资产都能生成资产提示词。
- [ ] `asset_prompt_generation` 只有在角色、场景、道具所需提示词完成后才标记完成。
- [ ] `image_generation_executor` 在音色和视频提示词阶段之前执行或明确记录为外部模式。
- [ ] `shot_video_prompt_generator` 不引用不存在的资产 ID。
- [ ] `shot_video_prompt_generator` 之后进入 `external_generation_handoff`，不直接跳到最终连续性审查。
- [ ] `external_generation_handoff` 之后进入 `generated_media_review`。
- [ ] `checkpoint.generation_modes.image_generation` 已明确为 `external_manual` 或 `internal_codex`，不是 `ask_user`。
- [ ] `checkpoint.completed_phases` 与 `checkpoint.phase_order` 顺序一致。

## 资产一致
- [ ] 角色 ID 使用 `CHAR_001` 格式。
- [ ] 场景 ID 使用 `ENV_001` 格式。
- [ ] 道具 ID 使用 `PROP_001` 格式。
- [ ] 状态变体按 A/B/C 标记。
- [ ] 母题资产在叙事骨架、资产表、分镜中一致。
- [ ] 人物不同年龄、服装、状态拆成独立资产图，不放进同一张最终资产图。
- [ ] 主要人物每个状态变体具备三视图：正视图、侧视图、后视图。
- [ ] 文字类道具仍有图片提示词或图片资产，不被跳过。
- [ ] 图片结果记录在 `image_result_manifest.json`，没有模板中的伪资产占位。

## 视频提示词一致
- [ ] 每个 shot 都有建议时长。
- [ ] 每个 shot 都有独立 `outputs/05_video_prompts/shots/SHOT_XXX.md`。
- [ ] 总文件 `shot_video_prompts.md` 由单 shot 文件汇总。
- [ ] 每个 shot 都声明对应 `@SHOT_XXX_STORYBOARD`。
- [ ] `@SHOT_XXX_STORYBOARD` 被标注为首帧参考、尾帧参考或关键帧参考。
- [ ] 视频提示词默认必须 `@` 分镜图和主要人物。
- [ ] 有台词、旁白、录音留言或可听见人声的 shot 必须 `@AUDIO`。
- [ ] 没有人声的 shot 不应 `@AUDIO`。
- [ ] `@ENV` 只在镜头运动需要扩展分镜图外空间时出现，并有引用决策说明。
- [ ] 视频提示词中默认没有 `@PROP`。
- [ ] 视频提示词只输出中文，不包含 `【English Prompt】`。
- [ ] 道具在正文中有清晰画面描述。

## 分镜序列连续
- [ ] `outputs/03_storyboard/storyboard_sequence_review.md` 存在。
- [ ] `outputs/03_storyboard/storyboard_sequence_review.json` 存在。
- [ ] 每个 shot 都完成单镜头自洽检查。
- [ ] 每组相邻 2-shot 窗口都完成检查。
- [ ] 每组相邻 3-shot 窗口都完成检查。
- [ ] 没有 P0 空间穿帮，例如道具凭空出现在上一个镜头未建立的位置。
- [ ] 没有未处理 P1；P1 已修复或有用户明确接受记录。
- [ ] 没有 P0 道具状态矛盾，例如已拿起的道具又无交代回到原位。
- [ ] 没有 P0 人物状态断裂，例如年龄、服装、伤痕或位置无交代跳变。
- [ ] 电话、门铃、电视、录像、旁白、台词等声音来源清楚，并标记给音色阶段。
- [ ] 空椅子、警号、警帽等母题只在正确位置和正确状态出现。

## 风格一致
- [ ] 分镜没有覆盖 `style_bible.md` 的核心风格。
- [ ] 角色、场景、道具提示词都引用视觉风格圣经。
- [ ] 视频提示词继承分镜与资产，不重新发明风格。

## 外部生成结果
- [ ] `image_result_manifest.json` 记录每个已生成图片资产的版本、状态和问题。
- [ ] `shot_result_manifest.json` 记录每个已生成 shot 的 take、文件/链接、状态和最佳版本。
- [ ] `generated_media_review.md` 与 `.json` 存在，或明确记录外部生成尚未执行。
- [ ] 被选为最佳 take 的镜头没有未处理 P0。
- [ ] 角色变脸、服装漂移、道具丢失、空间穿帮、音色错误已记录并给出返修建议。

## 交付完整
- [ ] `outputs/01_story/` 有故事产物。
- [ ] `outputs/02_art_direction/` 有视觉风格产物。
- [ ] `outputs/03_storyboard/` 有分镜产物。
- [ ] `outputs/04_assets/` 有资产注册表和资产提示词。
- [ ] `outputs/04_assets/audio/` 有音色参考清单或缺失说明。
- [ ] `outputs/05_video_prompts/` 有逐镜头视频提示词。
- [ ] `outputs/06_external_results/` 有图片/视频结果 manifest 和生成媒体审查。
- [ ] `production_status.csv` 存在，用于记录外部生成或内部生成状态。
- [ ] `outputs/07_final_delivery/` 有最终清单和审查报告。
- [ ] 最终状态为 `completed` 时，`known_gaps` 和 `blocking_issues` 均为空。
