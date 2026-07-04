# Skill: video_prompt_generator
**Version**: 2.0.0

## Source Prompt
`skills/raw_prompts/seedance_video_prompt.source.md`

## Purpose
生成最终可复制到即梦画布的视频提示词文档 `video_prompts.md`。

本 Skill 以分镜序列、分镜参考图和资产图为输入，按规则合并连续分镜，并为同场景连续镜头引入上一分镜站位锚点。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/storyboard.json",
  "storyboard_reference_dir": "./outputs/storyboards",
  "asset_reference_dir": "./outputs/assets",
  "shot_asset_map_path": "./outputs/shot_asset_map.json"
}
```

## Outputs
```json
{
  "video_prompts_path": "./outputs/video_prompts.md"
}
```

## Merge Rule
相邻 shot 只有同时满足以下三项，才可合并为一个 `V###`：

1. 同一 `scene_id`。
2. 相邻 shot 时长之和 `<=15s`。
3. 动作描述具有连续性，无场景切换、无时间跳跃。

不满足任一条件时，必须拆成独立 `V###`。

## Previous Storyboard Anchor Rule
同一场景内的连续多镜头，每个视频提示词必须引入：

```text
参考@上一分镜_站位，保持人物空间关系、朝向和相对位置不变
```

适用条件：同一场景内连续多镜头，且上一分镜参考图可用。

场景切换时：不引入上一分镜，避免错误约束。

## Prop Rule
道具资产不使用 `@PROP`。道具只写入视频提示词正文描述，包括位置、状态、交互动作和视觉细节。

## Procedure
1. 读取 `storyboard.json`，构建 shot 顺序。
2. 读取 `shot_asset_map.json`，为每个 shot 取角色、场景、道具。
3. 检查 `outputs/storyboards/S###.png` 是否存在；缺失时在提示词中标注需人工补图。
4. 检查 `outputs/assets/characters/` 与 `outputs/assets/scenes/` 是否存在有效资产图。
5. 从 `S001` 开始按顺序尝试合并相邻 shot。
6. 只有满足合并三条件时才合并；合并后总时长仍不得超过 15 秒。
7. 为每个 `V###` 输出：来源分镜、时长、参考图、资产声明、中文视频提示词、自检项。
8. 同一场景连续镜头写入上一分镜站位锚点；场景切换不写。
9. 输出 `outputs/video_prompts.md`。

## Output Format

```markdown
# Video Prompts

## V001
- 来源分镜：S001-S002
- 时长：12s
- 参考图：@S001_分镜参考图，@S002_分镜参考图
- 资产：少女_默然_正面；破旧公寓_深夜_冷白灯光
- 中文视频提示词：...
- 自检：同场景、时长 <=15s、动作连续、无 @PROP。
```

## Quality Gate
- [ ] 每个 `S###` 都被且仅被一个 `V###` 覆盖。
- [ ] 每个 `V###` 的时长 `<=15s`。
- [ ] 合并镜头满足同场景、总时长、动作连续三条件。
- [ ] 同一场景连续镜头包含上一分镜站位锚点。
- [ ] 场景切换不包含上一分镜站位锚点。
- [ ] 角色和场景参考来自 `shot_asset_map.json` 与实际资产图。
- [ ] 道具只写正文，不出现 `@PROP`。
- [ ] 输出中文，不输出 `English Prompt`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `video_prompt_generator`
- `completed_phases`: 追加 `video_prompt_generator`
- `artifacts.video_prompts`: `./outputs/video_prompts.md`
- `status`: `ready_for_jimeng_canvas`

## Failure Handling
- 分镜图缺失：标注缺口并要求用户回填 `outputs/storyboards/S###.png`。
- 资产图缺失：不声明为可参考图，只写正文描述并标注需补图。
- 动作不连续：拆分为独立 `V###`。
- 视频提示词出现 `@PROP`：改为正文描述。
