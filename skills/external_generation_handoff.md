# Skill: external_generation_handoff
**Version**: 0.5.0

## Purpose
把已确认的角色、场景、道具、分镜图、图片结果、音色参考和逐镜头中文 Seedance 视频提示词整理成外部工具可直接复制使用的交接包。此 Skill 不执行视频生成或剪辑。

从 0.5.0 起，本 Skill 必须保留 `shot_video_prompt_generator` 1.4.0 的 Seedance 任务类型信息，不能在交接过程中丢失 `task_type`、外部素材角色、图片结果可用性、编辑/延长硬句式或音频引用。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "asset_prompt_dir": "./outputs/04_assets",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
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
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
  "edit_notes_path": "./outputs/06_external_results/edit_notes.md"
}
```

## Required Shot Handoff Block
每个 shot 的交接块必须保留以下信息：

```text
## SHOT_XXX

- task_type: pipeline_shot_generation | multimodal_reference | video_edit | video_extend | combined_task
- Seedance 句式: 参考 / 严格编辑 / 向前延长 / 向后延长 / 组合任务
- 建议时长:
- 分镜图: @SHOT_XXX_STORYBOARD，首帧 / 尾帧 / 关键帧
- 人物资产: @CHAR_...
- 场景资产: 使用 / 不使用；理由
- 音色资产: 使用 / 不使用；状态
- 道具策略: 不 @PROP，只写正文描述
- 图片结果: 可用 / 不可用；来自 image_result_manifest 的状态
- 外部素材: @图片N / @视频N / @音频N 及其作用
- 可复制到 Seedance 的中文视频提示词:
```

## Procedure
1. 读取 `checkpoint.generation_modes.image_generation`。
2. 读取 `image_result_manifest.json`，列出可作为视频参考的图片和阻断缺图。
3. 如果图片模式为 `external_manual`，汇总角色、场景、道具图片提示词和图片生成队列。
4. 如果图片模式为 `internal_codex`，只汇总已生成图片路径和缺失项，不重复输出大段图片提示词。
5. 逐个读取 `outputs/05_video_prompts/shots/SHOT_XXX.md`，不得只读取汇总文件。
6. 保留每个 shot 的【引用决策】、【资产声明区】和【中文视频提示词】。
7. 为每个 shot 提取并显示 `task_type`。
8. 对 `video_edit` 检查并保留 `严格编辑 @视频N` 句式。
9. 对 `video_extend` 检查并保留 `向前延长 @视频N` 或 `向后延长 @视频N` 句式。
10. 对 `combined_task` 同时保留参考素材和编辑/延长目标。
11. 为每个镜头列出需要复制到外部视频工具的中文提示词、分镜图角色、人物参考、条件场景参考、音色参考、建议时长和注意事项。
12. 生成或更新图片结果记录 `image_result_manifest.json`，供用户记录外部图片生成结果。
13. 生成视频结果记录模板 `shot_result_manifest.template.json`，每个 shot 必须支持多 take、best_take 和 selected_for_edit。
14. 生成剪映交接说明：镜头顺序、建议时长、转场、音效/情绪备注。

## Quality Gate
- [ ] 不包含任何自动调用外部服务的步骤。
- [ ] 每个资产和镜头都有清晰可复制的提示词块。
- [ ] 每个视频镜头都保留资产 ID、镜头 ID、task_type 和分镜上下文。
- [ ] 视频提示词只输出中文。
- [ ] 每个视频镜头列出分镜图作为首帧、尾帧或关键帧参考。
- [ ] 每个有台词、旁白、留言或人声的镜头列出音色参考和音色状态。
- [ ] 场景参考只在镜头运动需要扩展空间时列出。
- [ ] 道具不作为视频多参 `@PROP` 声明，只作为画面描述或人工参考。
- [ ] `video_edit` 任务保留 `严格编辑 @视频N`。
- [ ] `video_extend` 任务保留 `向前延长 @视频N` 或 `向后延长 @视频N`。
- [ ] `combined_task` 同时保留参考素材作用和编辑/延长目标。
- [ ] 只把 `image_result_manifest.json` 中 `used_as_video_reference=true` 且 `status=generated | approved` 的图片列为可用参考图。
- [ ] 明确标记哪些内容由用户在外部网页端执行。
- [ ] 剪辑说明只做交接，不替代剪映操作。
- [ ] 外部生成结果记录模板已创建，且每个 shot 可追踪多 take、best_take、selected_for_edit、问题和返修建议。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `external_generation_handoff`
- `completed_phases`: 追加 `external_generation_handoff`
- `artifacts.external_generation_handoff`: `./outputs/06_external_results/external_generation_handoff.md`
- `artifacts.shot_result_manifest_template`: `./outputs/06_external_results/shot_result_manifest.template.json`
- `artifacts.image_result_manifest`: `./outputs/06_external_results/image_result_manifest.json`
- `quality_gates.external_handoff_preserved_seedance_task_type`: true
- `next_phase.skill`: `generated_media_review`

## Failure Handling
- 如果资产提示词或视频提示词缺失，返回对应上游阶段补齐。
- 如果单 shot 文件缺少 `task_type`，返回 `shot_video_prompt_generator`。
- 如果编辑或延长任务句式缺失，返回 `shot_video_prompt_generator` 重写该 shot。
- 如果目标外部工具不明确，使用通用网页端交接格式，不阻塞流程。
