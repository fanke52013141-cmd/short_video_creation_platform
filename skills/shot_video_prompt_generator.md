# Skill: shot_video_prompt_generator
**Version**: 1.5.0

## Source Prompt
`skills/raw_prompts/seedance_video_prompt.source.md`

## Purpose
逐 shot 循环生成可直接交付即梦 / Doubao Seedance 2.0 多模态多参考能力的中文视频提示词。每条 shot 必须独立生成、独立自检、独立保存，最后再汇总。

从 1.4.0 起，本 Skill 是 **Seedance 任务类型感知的逐镜头视频提示词生成器**。它不仅生成普通参考型视频提示词，还必须先判断每条 shot 是否属于：

- `pipeline_shot_generation`: 项目流水线默认类型，由分镜、资产清单、图片结果和音色清单驱动。
- `multimodal_reference`: 参考图片、视频、音频的指定维度生成新视频。
- `video_edit`: 严格编辑已有视频，未提及部分保持不变。
- `video_extend`: 向前或向后延长已有视频。
- `combined_task`: 同时参考某些素材并编辑或延长另一个素材。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "asset_prompt_dir": "./outputs/04_assets",
  "storyboard_keyframe_dir": "./outputs/03_storyboard/keyframes",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
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
每个 `SHOT_XXX.md` 都必须同时生成 `SHOT_XXX.json`，并满足 `schemas/shot_video_prompt.schema.json`。

## Seedance Task Type Rules

### pipeline_shot_generation
项目默认类型。使用 `storyboard.json`、`asset_manifest.json`、`image_result_manifest.json`、`voice_reference_manifest.json` 和资产提示词生成单镜头视频提示词。

### multimodal_reference
从图片、视频或音频中提取指定维度，生成全新视频。

必须使用：
- `参考 @图片N 的人物形象...`
- `参考 @视频N 的动作节奏...`
- `参考 @音频N 的音色...`

### video_edit
在已有视频基础上修改局部或全局内容。

必须使用：
- `严格编辑 @视频N，将...修改为...`
- `严格编辑 @视频N，在...位置增加...`
- `严格编辑 @视频N，移除...，其余主体、动作、镜头和节奏保持不变。`

禁止把编辑任务写成 `参考 @视频N`。

### video_extend
在时间维度上延续原视频。

必须使用：
- `向后延长 @视频N，保持原视频的人物外观、场景光线、镜头节奏和声音氛围，继续生成...`
- `向前延长 @视频N，生成原视频开始前的连续动作...`

禁止把延长任务写成 `参考 @视频N`。

### combined_task
参考某个素材的指定维度，同时编辑或延长另一个素材。

示例：
- `参考 @图片1 的人物形象，严格编辑 @视频1，将视频中的人物替换为该人物，保留原视频动作、运镜和节奏。`
- `参考 @音频1 的音色，向后延长 @视频1，并让后续台词使用同一音色。`

## Procedure
1. 读取 Seedance 视频提示词源文件和 `docs/video_prompt_loop_protocol.md`。
2. 构建 shot queue。不得跳过 shot，不得只一次性生成总文件。
3. 对每个 shot 循环执行：
   - 读取当前 shot 的叙事功能、时长、镜头运动、台词、人物、场景、道具。
   - 判断任务类型：默认 `pipeline_shot_generation`；如存在外部编辑、延长或组合任务，则切换到对应类型。
   - 读取 `image_result_manifest.json`，只把 `used_as_video_reference=true` 且状态为 `generated` 或 `approved` 的图片声明为可用参考图。
   - 声明 `@SHOT_XXX_STORYBOARD`，并标注首帧参考、尾帧参考或关键帧参考。
   - 声明主要人物 `@CHAR`，人物应来自三视图资产、三视图映射或已批准图片结果。
   - 判断是否有人声；有台词、旁白、录音留言或可听见人声时，必须声明对应 `@AUDIO`。
   - 根据镜头运动和分镜图覆盖范围判断是否声明 `@ENV`；必须写明使用或不使用理由。
   - 道具只写入正文画面描述，不写 `@PROP`。
   - 若有外部图片、视频或音频素材，按上传顺序命名为 `@图片1`、`@视频1`、`@音频1`，并在资产声明区明确素材角色。
   - 若外部素材中有多个主体，先用 2-3 个稳定静态特征定义主体名。
   - 使用 Seedance 声音符号：背景音乐用 `（背景中播放着...）`，环境音用 `<...>`，人物台词用 `{...}`，字幕用 `【...】`。
   - 生成单条中文视频提示词，保存为 `outputs/05_video_prompts/shots/SHOT_XXX.md`。
   - 同时保存 `outputs/05_video_prompts/shots/SHOT_XXX.json`，写入上一镜、连续关系、生成策略和首尾状态。
   - 对该 shot 自检，不合格则重写该 shot。
4. 全部单 shot 文件通过后，生成 `shot_video_prompt_index.md`。
5. 按镜头顺序汇总所有单 shot 文件，生成 `shot_video_prompts.md`。
6. 在本 Skill 内对全部提示词做一次 AI 总检，输出 `video_prompt_review.json`；不增加新的流程阶段。

## Quality Gate
- [ ] 每个 storyboard shot 都有一个 `shots/SHOT_XXX.md`。
- [ ] 汇总文件由单 shot 文件按顺序汇总而来。
- [ ] 每条视频提示词包含 `task_type` 或明确任务类型判断。
- [ ] 编辑任务必须使用 `严格编辑 @视频N`，不得写成参考任务。
- [ ] 延长任务必须使用 `向前延长 @视频N` 或 `向后延长 @视频N`，不得写成参考任务。
- [ ] 每条视频提示词引用的分镜图和主要角色均存在。
- [ ] 每条视频提示词包含建议时长。
- [ ] 清楚声明参考素材的角色：首帧、尾帧、关键帧、人物资产、条件场景资产、声音参考、动作参考、编辑视频、延长视频等。
- [ ] 正文中引用的资产名与资产声明区完全一致。
- [ ] 只有 `image_result_manifest.json` 中 `used_as_video_reference=true` 且状态为 `generated` 或 `approved` 的图片才可声明为参考图。
- [ ] 有人声的 shot 必须声明 `@AUDIO`；无人声的 shot 不声明 `@AUDIO`。
- [ ] 每条 shot 都有 `@ENV` 使用或不使用的引用决策说明。
- [ ] 默认不出现 `@PROP`；道具写入正文画面描述。
- [ ] 不把风格参考图误当内容参考。
- [ ] 单个镜头只设置一种主要运镜。
- [ ] 台词、动作、镜头运动、声音和情绪可被视频模型执行。
- [ ] 输出包含自检通过项。
- [ ] 不输出 `【English Prompt】`。
- [ ] 每个 shot 都有符合 schema 的 `SHOT_XXX.json`。
- [ ] `match_action` 或 `same_continuous_shot` 不得使用 `independent_clip`。
- [ ] `video_prompt_review.json` 由 AI 生成，覆盖全部镜头和相邻镜头，且没有未处理 P0/P1。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `shot_video_prompt_generator`
- `completed_phases`: 追加 `shot_video_prompt_generator`
- `artifacts.single_shot_video_prompt_dir`: `./outputs/05_video_prompts/shots`
- `artifacts.shot_video_prompt_index`: `./outputs/05_video_prompts/shot_video_prompt_index.md`
- `artifacts.shot_video_prompts`: `./outputs/05_video_prompts/shot_video_prompts.md`
- `artifacts.video_prompt_asset_reference`: `./outputs/05_video_prompts/video_prompt_asset_reference.md`
- `artifacts.video_prompt_review`: `./outputs/05_video_prompts/video_prompt_review.json`
- `artifacts.seedance_task_type_policy`: `enabled`
- `next_phase.skill`: `external_generation_handoff`

## Failure Handling
- 资产引用缺失：停止生成该镜头，返回资产清单或图片结果登记阶段。
- 图片结果不可用：不声明为参考图，只写正文描述，并记录 known gap。
- 有人声但缺少音色参考：停止该 shot，要求用户提供音频，或按用户确认标记 `missing` 占位。
- 参考素材角色不明：要求用户标注参考素材用途。
- 编辑任务误写成参考任务：重写该 shot，使用 `严格编辑 @视频N`。
- 延长任务误写成参考任务：重写该 shot，使用 `向前延长 @视频N` 或 `向后延长 @视频N`。
- 提示词过度抽象：按源提示词执行具象化转换。
- 道具需要稳定出现但不适合 `@`：保留道具图片作为人工参考，在正文中写清道具位置、动作和视觉细节。
