# Local Run Template

复制本文件内容到：

```text
local_runs/YYYY-MM-DD/project_slug/notes.md
```

## Project
- Slug:
- Date:
- Owner:
- Goal:

## Input
- Idea brief:
- References:
- Constraints:

## Generation Modes
- Image generation: `ask_user | external_manual | internal_codex`
- Video generation: `external_manual`
- Editing: `external_manual`

进入图片阶段前必须确认 image generation 模式。视频生成和剪辑默认外部执行。

## Phase Log

| Phase | Status | Artifact | Notes |
| -- | -- | -- | -- |
| story_generation | pending |  |  |
| art_direction | pending |  |  |
| storyboard_director | pending |  |  |
| storyboard_sequence_review | pending |  |  |
| asset_manifest_builder | pending |  |  |
| asset_prompt_generation | pending |  |  |
| image_generation_or_handoff | pending |  |  |
| voice_reference_manifest_builder | pending |  |  |
| shot_video_prompt_generation | pending |  |  |
| external_generation_handoff | pending |  |  |
| continuity_review | pending |  |  |

## Production Status
用 `production_status.csv` 跟踪每个 shot 的分镜连续性、音色、场景引用决策、提示词、图片、视频、最佳版本和返修问题。

## Storyboard Sequence Review
- Review file: `outputs/03_storyboard/storyboard_sequence_review.md`
- JSON file: `outputs/03_storyboard/storyboard_sequence_review.json`
- 必须用 1-shot、2-shot、3-shot 窗口检查相邻镜头逻辑。
- 有 P0 问题时先修分镜，不进入资产生成。

## Video Prompt Loop
- Single shot prompt dir: `outputs/05_video_prompts/shots/`
- Aggregate prompt file: `outputs/05_video_prompts/shot_video_prompts.md`
- 每个 shot 必须先生成单条文件，通过自检后再汇总。

## Audio References
- Manifest: `outputs/04_assets/audio/voice_reference_manifest.json`
- 有台词、旁白、录音留言或可听见人声的 shot 必须绑定音色参考。

## Problems Found
- 

## Reusable Improvements
记录可以反哺仓库的流程问题，不记录具体私有创作内容。

- 
