# Skill: shot_video_prompt_generator
**Version**: 1.3.0

## Source Prompt
`skills/raw_prompts/seedance_video_prompt.source.md`

## Purpose
逐 shot 循环生成可直接交付 Seedance 2.0 多模态多参考能力的中文视频提示词。每条 shot 必须独立生成、独立自检、独立保存，最后再汇总。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "asset_prompt_dir": "./outputs/04_assets",
  "storyboard_keyframe_dir": "./outputs/03_storyboard/keyframes",
  "voice_reference_manifest_path": "./outputs/04_assets/audio/voice_reference_manifest.json",
  "reference_media": [],
  "shot_id": "SHOT_001 | all"
}
```

## Outputs
```json
{
  "single_shot_prompt_dir": "./outputs/05_video_prompts/shots",
  "single_shot_prompt_json_path": "./outputs/05_video_prompts/shots/SHOT_XXX.json",
  "shot_video_prompt_index_path": "./outputs/05_video_prompts/shot_video_prompt_index.md",
  "shot_video_prompts_markdown_path": "./outputs/05_video_prompts/shot_video_prompts.md",
  "video_prompt_asset_reference_path": "./outputs/05_video_prompts/video_prompt_asset_reference.md"
}
```

## Schema
如果输出 `outputs/05_video_prompts/shots/SHOT_XXX.json`，必须满足 `schemas/shot_video_prompt.schema.json`。

## Procedure
1. 读取 Seedance 视频提示词源文件和 `docs/video_prompt_loop_protocol.md`。
2. 构建 shot queue。不得跳过 shot，不得只一次性生成总文件。
3. 对每个 shot 循环执行：
   - 读取当前 shot 的叙事功能、时长、镜头运动、台词、人物、场景、道具。
   - 声明 `@SHOT_XXX_STORYBOARD`，并标注首帧参考、尾帧参考或关键帧参考。
   - 声明主要人物 `@CHAR`，人物应来自三视图资产或三视图映射。
   - 判断是否有人声；有台词、旁白、录音留言或可听见人声时，必须声明对应 `@AUDIO`。
   - 根据镜头运动和分镜图覆盖范围判断是否声明 `@ENV`；必须写明使用或不使用理由。
   - 道具只写入正文画面描述，不写 `@PROP`。
   - 生成单条中文视频提示词，保存为 `outputs/05_video_prompts/shots/SHOT_XXX.md`。
   - 如运行环境支持结构化输出，同时保存 `outputs/05_video_prompts/shots/SHOT_XXX.json`，字段需满足 `schemas/shot_video_prompt.schema.json`。
   - 对该 shot 自检，不合格则重写该 shot。
4. 全部单 shot 文件通过后，生成 `shot_video_prompt_index.md`。
5. 按镜头顺序汇总所有单 shot 文件，生成 `shot_video_prompts.md`。

## Quality Gate
- [ ] 每个 storyboard shot 都有一个 `shots/SHOT_XXX.md`。
- [ ] 汇总文件由单 shot 文件按顺序汇总而来。
- [ ] 每条视频提示词引用的分镜图和主要角色均存在。
- [ ] 每条视频提示词包含建议时长。
- [ ] 清楚声明参考素材的角色：首帧、尾帧、关键帧、人物资产、条件场景资产、声音参考等。
- [ ] 有人声的 shot 必须声明 `@AUDIO`；无人声的 shot 不声明 `@AUDIO`。
- [ ] 每条 shot 都有 `@ENV` 使用或不使用的引用决策说明。
- [ ] 默认不出现 `@PROP`；道具写入正文画面描述。
- [ ] 不把风格参考图误当内容参考。
- [ ] 台词、动作、镜头运动和情绪可被视频模型执行。
- [ ] 输出包含自检通过项。
- [ ] 不输出 `【English Prompt】`。
- [ ] 若输出 `SHOT_XXX.json`，必须满足 `schemas/shot_video_prompt.schema.json`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `shot_video_prompt_generator`
- `completed_phases`: 追加 `shot_video_prompt_generator`
- `artifacts.single_shot_video_prompt_dir`: `./outputs/05_video_prompts/shots`
- `artifacts.shot_video_prompt_index`: `./outputs/05_video_prompts/shot_video_prompt_index.md`
- `artifacts.shot_video_prompts`: `./outputs/05_video_prompts/shot_video_prompts.md`
- `artifacts.video_prompt_asset_reference`: `./outputs/05_video_prompts/video_prompt_asset_reference.md`
- `next_phase.skill`: `external_generation_handoff`

## Failure Handling
- 资产引用缺失：停止生成该镜头，返回资产清单阶段。
- 有人声但缺少音色参考：停止该 shot，要求用户提供音频，或按用户确认标记 `missing` 占位。
- 参考素材角色不明：要求用户标注参考素材用途。
- 提示词过度抽象：按源提示词执行具象化转换。
- 道具需要稳定出现但不适合 `@`：保留道具图片作为人工参考，在正文中写清道具位置、动作和视觉细节。
