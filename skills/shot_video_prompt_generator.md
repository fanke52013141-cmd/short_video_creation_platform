# Skill: shot_video_prompt_generator
**Version**: 1.1.0

## Source Prompt
`skills/raw_prompts/seedance_video_prompt.source.md`

## Purpose
把每个分镜、资产提示词、分镜图和参考素材转译为可直接交付 Seedance 2.0 多模态多参考能力的中文视频生成提示词。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "asset_prompt_dir": "./outputs/04_assets",
  "storyboard_keyframe_dir": "./outputs/03_storyboard/keyframes",
  "reference_media": [],
  "shot_id": "SHOT_001 | all"
}
```

## Outputs
```json
{
  "shot_video_prompts_markdown_path": "./outputs/05_video_prompts/shot_video_prompts.md",
  "video_prompt_asset_reference_path": "./outputs/05_video_prompts/video_prompt_asset_reference.md"
}
```

## Procedure
1. 读取 Seedance 视频提示词源文件。
2. 对每个镜头读取分镜参数、资产 ID、资产提示词、风格圣经和参考素材。
3. 先进行输入素材分类：文本、图像、音频、视频分别承担什么锁定作用。
4. 对已锁定维度不重复发明，只补全未锁定维度。
5. 为每个镜头写入建议时长，使用 `storyboard.json.duration_seconds`。
6. 如果存在对应分镜图，声明为 `@SHOT_XXX_STORYBOARD`，并标注首帧参考、尾帧参考或关键帧参考。
7. 资产声明默认只包含分镜图、人物资产和场景资产；道具资产只写入画面描述，不写 `@PROP`。
8. 输出中文视频提示词，不输出英文对照。

## Quality Gate
- [ ] 每条视频提示词引用的分镜图、角色和场景均存在。
- [ ] 每条视频提示词包含建议时长。
- [ ] 清楚声明参考素材的角色：首帧、尾帧、关键帧、人物资产、场景资产、风格参考、动作参考等。
- [ ] 默认不出现 `@PROP`；道具写入正文画面描述。
- [ ] 不把风格参考图误当内容参考。
- [ ] 台词、动作、镜头运动和情绪可被视频模型执行。
- [ ] 输出包含自检通过项。
- [ ] 不输出 `【English Prompt】`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `shot_video_prompt_generator`
- `completed_phases`: 追加 `shot_video_prompt_generator`
- `artifacts.shot_video_prompts`: `./outputs/05_video_prompts/shot_video_prompts.md`
- `artifacts.video_prompt_asset_reference`: `./outputs/05_video_prompts/video_prompt_asset_reference.md`
- `next_phase.skill`: `continuity_review`

## Failure Handling
- 资产引用缺失：停止生成该镜头，返回资产清单阶段。
- 参考素材角色不明：要求用户标注参考素材用途。
- 提示词过度抽象：按源提示词执行具象化转换。
- 道具需要稳定出现但不适合 `@`：保留道具图片作为人工参考，在正文中写清道具位置、动作和视觉细节。
