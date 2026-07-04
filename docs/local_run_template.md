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
- User visual style / references:
- User character / scene references:

## Generation Modes

- Asset image generation: `external_manual`，默认在即梦网页端生成。
- Storyboard image generation: `external_manual`，默认在即梦网页端生成。
- Video generation: `jimeng_canvas_manual`。

## Phase Log

| Phase | Status | Artifact | Notes |
| -- | -- | -- | -- |
| story_generation | pending | `outputs/story.md` | 只做剧本，不输出 JSON |
| art_direction | pending | `outputs/style_bible.md` | 用户有风格则继承；无风格则先给候选方案；不做具体构图 |
| storyboard_director | pending | `outputs/storyboard.json` | 负责具体构图、景别、镜头和分镜结构化 |
| asset_executor | pending | `outputs/asset_manifest.json`, `outputs/shot_asset_map.json` | Seedance 稳定命名、素材绑定、生成决策和 shot 映射 |
| asset_prompt_generation | pending | `outputs/assets/**.md` | 人物生成身份资产组；场景生成空间参考；道具只处理必要核心道具 |
| storyboard_prompt_generator | pending | `outputs/storyboard_prompts.md` | 生成分镜参考图提示词 |
| video_prompt_generator | pending | `outputs/video_prompts.md`, `outputs/video_prompts.json` | 最终复制到即梦；每条 V### 记录 merge_decision |

## Manual Jimeng Steps

1. 资产提示词完成后，在即梦生成必要人物、场景、道具图片。
2. 人物通常回填：
   - 人脸/面部参考图
   - 全身妆造参考图
3. 场景通常回填：
   - 稳定空间结构参考图
4. 道具只有 `generation_required=true` 时才回填独立道具图；普通道具不需要。
5. 将有效资产图片回填到：
   - `outputs/assets/characters/`
   - `outputs/assets/scenes/`
   - `outputs/assets/props/`
6. 分镜提示词完成后，在即梦生成分镜参考图。
7. 将分镜图回填到 `outputs/storyboards/S001.png`、`S002.png` 等。
8. 运行 `video_prompt_generator` 生成最终 `video_prompts.md` 和 `video_prompts.json`。
9. 将最终交付物带入即梦画布。

## Final Handoff Checklist

- [ ] `outputs/story.md`
- [ ] `outputs/video_prompts.md`
- [ ] `outputs/video_prompts.json`
- [ ] `outputs/assets/characters/` 中只保留有效角色资产
- [ ] `outputs/assets/scenes/` 中只保留有效场景资产
- [ ] `outputs/storyboards/` 中包含全部有效分镜参考图

道具资产不作为单独最终交付目录；道具信息写入 `video_prompts.md` 正文。

## Validation

初始化后运行：

```text
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase initialized
```

完整项目运行：

```text
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase all
```

## Problems Found

-

## Reusable Improvements

记录可以反哺仓库的流程问题，不记录具体私有创作内容。

-
