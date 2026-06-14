# Skill: voice_reference_manifest_builder
**Version**: 0.1.0

## Purpose
根据分镜台词、旁白、录音留言和角色资产，建立项目级音色参考清单。该 Skill 不生成音频，只识别哪些 shot 需要音色参考，并要求用户提供或确认占位。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/03_storyboard/storyboard.json",
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "user_audio_reference_dir": "./references/audio"
}
```

## Outputs
```json
{
  "voice_reference_manifest_path": "./outputs/04_assets/audio/voice_reference_manifest.json",
  "voice_reference_assets_markdown_path": "./outputs/04_assets/audio/voice_reference_assets.md"
}
```

## Procedure
1. 读取 `storyboard.json`，识别包含对白、旁白、录音留言、新闻播报或可听见人声的 shot。
2. 将每个有声 shot 绑定到说话人角色或旁白类型。
3. 为每个说话人创建 `AUDIO_XXX` 音色资产。
4. 如果用户已提供音频文件，记录路径并标记 `provided`。
5. 如果缺少音频文件，标记 `needed` 或 `missing`，并向用户索要对应音色参考。
6. 输出音色参考清单和人工采集说明。

## Quality Gate
- [ ] 每个有台词、旁白、录音留言或可听见人声的 shot 都有对应 `AUDIO_XXX`。
- [ ] 没有人声的 shot 不强行绑定音色。
- [ ] 每个 `AUDIO_XXX` 都有说话人、音色方向、状态和适用镜头。
- [ ] 缺少音频时明确标记，不伪装为已完成。

## Checkpoint Update
通过质量门后更新：
- `artifacts.voice_reference_manifest`: `./outputs/04_assets/audio/voice_reference_manifest.json`
- `artifacts.voice_reference_assets`: `./outputs/04_assets/audio/voice_reference_assets.md`
- `completed_phases`: 追加 `voice_reference_manifest_builder`

## Failure Handling
- 有台词但没有说话人：返回分镜阶段补全。
- 缺少音频参考：询问用户提供音频，或按用户确认写入 `placeholder`。
- 用户暂时没有音频：允许继续草稿视频提示词，但 production status 必须标记 `audio_reference_status=missing`。
