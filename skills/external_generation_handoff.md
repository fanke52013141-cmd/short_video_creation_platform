# Skill: external_generation_handoff
**Version**: 0.3.0

## Purpose
把已确认的角色、场景、道具、分镜图和逐镜头中文视频提示词整理成外部工具可直接复制使用的交接包。此 Skill 不执行视频生成或剪辑。图片是否外部生成取决于 `generation_modes.image_generation`。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "asset_prompt_dir": "./outputs/04_assets",
  "shot_video_prompts_markdown_path": "./outputs/05_video_prompts/shot_video_prompts.md",
  "single_shot_prompt_dir": "./outputs/05_video_prompts/shots",
  "video_prompt_asset_reference_path": "./outputs/05_video_prompts/video_prompt_asset_reference.md",
  "voice_reference_manifest_path": "./outputs/04_assets/audio/voice_reference_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "target_tools": {
    "image_generation": "external_manual | internal_codex",
    "video_generation": "jimeng_seedance_web",
    "editing": "jianying"
  }
}
```

## Outputs
```json
{
  "handoff_markdown_path": "./outputs/06_external_results/external_generation_handoff.md",
  "shot_result_manifest_template_path": "./outputs/06_external_results/shot_result_manifest.template.json",
  "edit_notes_path": "./outputs/06_external_results/edit_notes.md"
}
```

## Procedure
1. 读取 `checkpoint.generation_modes.image_generation`。
2. 如果图片模式为 `external_manual`，汇总角色、场景、道具图片提示词，按资产 ID 排列。
3. 如果图片模式为 `internal_codex`，只汇总已生成图片路径和缺失项，不重复输出大段图片提示词。
4. 汇总 `outputs/05_video_prompts/shots/SHOT_XXX.md`，按镜头编号排列。
5. 为每个镜头列出需要复制到外部视频工具的中文提示词、分镜图角色、人物参考、条件场景参考、音色参考、建议时长和注意事项。
6. 生成外部结果记录模板，供用户手动填写生成结果文件名、版本、外部平台链接或备注。
7. 生成剪映交接说明：镜头顺序、建议时长、转场、音效/情绪备注。

## Quality Gate
- [ ] 不包含任何自动调用外部服务的步骤。
- [ ] 每个资产和镜头都有清晰可复制的提示词块。
- [ ] 每个视频镜头都保留资产 ID、镜头 ID 和分镜上下文。
- [ ] 视频提示词只输出中文。
- [ ] 每个视频镜头列出分镜图作为首帧、尾帧或关键帧参考。
- [ ] 每个有台词、旁白、留言或人声的镜头列出音色参考。
- [ ] 场景参考只在镜头运动需要扩展空间时列出。
- [ ] 道具不作为视频多参 `@PROP` 声明，只作为画面描述或人工参考。
- [ ] 明确标记哪些内容由用户在外部网页端执行。
- [ ] 剪辑说明只做交接，不替代剪映操作。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `external_generation_handoff`
- `completed_phases`: 追加 `external_generation_handoff`
- `artifacts.external_generation_handoff`: `./outputs/06_external_results/external_generation_handoff.md`
- `next_phase.skill`: `continuity_review`

## Failure Handling
- 如果资产提示词或视频提示词缺失，返回对应上游阶段补齐。
- 如果目标外部工具不明确，使用通用网页端交接格式，不阻塞流程。
