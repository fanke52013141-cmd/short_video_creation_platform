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

- Asset image generation: `jimeng_web_manual | chatgpt_web | codex_direct | external_manual`
- Storyboard image generation: `jimeng_web_manual | chatgpt_web | codex_direct | external_manual`
- Video generation: `jimeng_canvas_manual`。

## Phase Log

| Phase | Status | Artifact | Notes |
| -- | -- | -- | -- |
| story_generation | pending | `outputs/story.md` | 只做剧本，不输出 JSON |
| art_direction | pending | `outputs/style_bible.md` | 用户有风格则继承；无风格则先给候选方案；不做具体构图 |
| storyboard_director | pending | `outputs/storyboard.json` | 负责具体构图、景别、镜头和分镜结构化 |
| asset_executor | pending | `outputs/asset_manifest.json`, `outputs/shot_asset_map.json` | Seedance 稳定命名、素材绑定、生成决策和 shot 映射 |
| asset_prompt_generation | pending | `outputs/assets/**.md` | 输入为 story、style、asset_type、asset_name、output_prompt_path；不需要 task_id |
| image_generation_executor | optional | `outputs/image_generation_queue.json`, `outputs/image_generation_queue.md`, `outputs/assets/**.png` | 一个任务只生成一张图，禁止拼接图 |
| storyboard_prompt_generator | pending | `outputs/storyboard_prompts.md` | 生成分镜参考图提示词 |
| video_prompt_generator | pending | `outputs/video_prompts.md`, `outputs/video_prompts.json` | 最终复制到即梦；每条 V### 记录 merge_decision |

## Asset Prompt Generation Steps

1. 从 `asset_manifest.json` 中选择一个需要生成提示词的资产和一个 `prompt_outputs` 输出路径。
2. 调用对应生成器，输入：
   - `outputs/story.md`
   - `outputs/style_bible.md`
   - `asset_type`
   - `asset_name`
   - `output_prompt_path`
3. 不传 `task_id`。
4. 不传 `asset_payload`。
5. 不额外维护 `asset_prompt_tasks.json`。

## Asset Image Generation Steps

1. 资产提示词完成后，运行或手动执行 `image_generation_executor`。
2. 选择生成方式：即梦网页端、ChatGPT 网页端、Codex 直接生成或其他外部工具。
3. 每个 `asset_image_task` 只生成一张图片。
4. 禁止把人脸大头特写和全身妆造拼到一张图。
5. 禁止场景四宫格、对比图、设定表、contact sheet。
6. 人物通常回填：
   - 人脸/面部参考图
   - 全身妆造参考图
7. 场景通常回填：
   - 稳定空间结构参考图
8. 道具只有 `generation_required=true` 时才回填独立道具图；普通道具不需要。
9. 将有效资产图片回填到：
   - `outputs/assets/characters/`
   - `outputs/assets/scenes/`
   - `outputs/assets/props/`
10. 分镜提示词完成后，生成分镜参考图。
11. 将分镜图回填到 `outputs/storyboards/S001.png`、`S002.png` 等。
12. 运行 `video_prompt_generator` 生成最终 `video_prompts.md` 和 `video_prompts.json`。
13. 将最终交付物带入即梦画布。

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
