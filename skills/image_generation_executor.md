# Skill: image_generation_executor
**Version**: 0.1.0

## Purpose
在用户选择 `internal_codex` 时，按资产提示词生成或整理本地图片资产；在 `external_manual` 时，不执行图片生成，只核对外部图片结果记录。该 Skill 不处理视频生成。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "asset_prompt_dir": "./outputs/04_assets",
  "generation_mode": "internal_codex | external_manual",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json"
}
```

## Outputs
```json
{
  "generated_image_index_path": "./outputs/generated_image_index.md",
  "image_result_manifest_path": "./outputs/06_external_results/image_result_manifest.json",
  "final_image_dir": "./outputs/04_assets/final_images"
}
```

## Procedure
1. 读取 `checkpoint.generation_modes.image_generation`。
2. 如果模式仍为 `ask_user`，停止并要求用户选择 `internal_codex` 或 `external_manual`。
3. 如果是 `external_manual`，复制或生成 `image_result_manifest.json` 空表，等待用户填写外部图片结果。
4. 如果是 `internal_codex`，逐资产读取角色、场景、道具提示词并生成图片，保存到 `outputs/04_assets/final_images/`。
5. 为每个资产记录结果文件、版本、状态、问题和最佳版本。
6. 输出 `generated_image_index.md` 供人类检查。

## Quality Gate
- [ ] 图片生成模式已明确，不是 `ask_user`。
- [ ] 每个需要图片的资产都有 `generated | approved | missing | needs_regen` 状态。
- [ ] 主要人物三视图资产有独立状态记录。
- [ ] 文字类道具没有被跳过；如果文字不稳定，标记后期修正需求。
- [ ] 所有生成媒体只保存在 local run，不提交仓库。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `image_generation_executor`
- `completed_phases`: 追加 `image_generation_executor`
- `artifacts.image_result_manifest`: `./outputs/06_external_results/image_result_manifest.json`
- `artifacts.generated_image_index`: `./outputs/generated_image_index.md`
- `next_phase.skill`: `voice_reference_manifest_builder`

## Failure Handling
- 模式未确认：停止并询问用户。
- 生成失败：记录到 `image_result_manifest.json`，不覆盖已通过图片。
- 主要角色三视图缺失：允许草稿继续，但最终打包不得标记 `completed`。
