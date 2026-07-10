# 短视频创作平台

这是一套面向即梦画布生产的短视频创作流程仓库。仓库不直接生成最终视频，也不管理外部生成后的成片审查；它负责把用户想法转化为剧本、风格约束、分镜序列、资产清单、资产/分镜生图提示词和最终视频提示词。

## 核心原则

- 剧本优先：`story_generation` 只优化剧本，不输出结构化 JSON。
- 用户确认：剧本与视觉方向都需要用户确认后再进入下游。
- 艺术先行：艺术总监先定画面风格、色调、光线和 AI 视觉执行要求；导演后续负责具体构图与分镜。
- 最小必要输入：下游只读取当前阶段真正需要的文件。
- 人物资产：按 `人物稳定名_状态` 固定，例如 `林小满_雨夜接电话状态`；不默认拆成大头特写和全身妆造两个资产。
- 场景资产：按稳定场景名固定，普通光线、时间、天气变化不拆新场景。
- 资产提示词输入保持简单：`story.md + style_bible.md + asset_type + asset_name + output_prompt_path`。
- 分镜参考图：每个 `S###` 必须标明首帧、尾帧或关键帧，并判断是否引用上一分镜作站位参考。
- 视频提示词：可在同一 `scene_id` 内合并连续 `S###`，合并总时长必须不超过 15 秒。

## 推荐试跑顺序

1. 执行 `scripts/init_local_run.ps1 -ProjectSlug your-project-slug` 初始化本地创作目录。
2. 填写 `local_runs/YYYY-MM-DD/your-project-slug/inputs/idea_brief.md`。
3. 运行 `skills/story_generation.md`，只产出 `outputs/story.md`。
4. 用户与剧本专家反复讨论，直到用户确认剧本可以进入下一阶段。
5. 运行 `skills/art_direction.md`，用户确认后产出 `outputs/style_bible.md`。
6. 运行 `skills/storyboard_director.md`，产出 `outputs/storyboard.json`。
7. 运行 `skills/asset_executor.md`，产出 `outputs/asset_manifest.json` 和 `outputs/shot_asset_map.json`。
8. 根据 `asset_manifest.json` 里的 `output_prompt_path`，循环运行人物、场景、必要道具提示词生成器。
9. 每次提示词生成器只输入：剧本、风格圣经、资产类型、资产名和输出路径。
10. 运行或手动执行 `skills/image_generation_executor.md` 生成资产图片；每个任务只生成一张图片文件。
11. 将有效资产图片回填到 `outputs/assets/characters/`、`outputs/assets/scenes/`、`outputs/assets/props/`。
12. 运行 `skills/storyboard_prompt_generator.md`，产出 `outputs/storyboard_prompts.md`，明确每个分镜的帧角色和上一分镜站位参考判断。
13. 生成分镜参考图，并回填到 `outputs/storyboards/S001.png`、`S002.png` 等。
14. 运行 `skills/video_prompt_generator.md`，根据连续 shot、同一 scene_id 和 15 秒上限生成 `outputs/video_prompts.md` 与 `outputs/video_prompts.json`。

## 输出目录

```text
outputs/
├── story.md
├── style_bible.md
├── storyboard.json
├── asset_manifest.json
├── shot_asset_map.json
├── storyboard_prompts.md
├── video_prompts.md
├── video_prompts.json
├── assets/
│   ├── characters/
│   ├── scenes/
│   └── props/
└── storyboards/
```

## 命名规范

- 人物：`人物稳定名_状态`，例如 `林小满_雨夜接电话状态`。
- 人物资产图：一个人物状态资产生成一张 21:9 人物资产图，可在同一张图内包含特写、正面、侧面、后视图。
- 场景：优先使用具象场景名，例如 `雨夜客厅场景`；无明确名称时用 `场景1`、`场景2`。
- 道具：只管控核心剧情道具；普通背景物件不强行生成独立资产。
- 分镜：`S{三位数序号}`，例如 `S001`。
- 场景/时空单元：`SC{三位数序号}`，例如 `SC001`。
- 视频提示词：`V{三位数序号}`，例如 `V001`，可合并多个连续分镜。

## 校验

```bash
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase all
python scripts/validate_seedance_video_prompts.py local_runs/YYYY-MM-DD/project_slug
```

## 仓库边界

- 仓库保存流程、Skill、配置模板、schema、检查规则和文档。
- 真实创作产物、参考素材、生成图片、日志和 `checkpoint.json` 放入本地 `local_runs/YYYY-MM-DD/project_slug/`，不提交仓库。
- `story_generation` 不输出 `story.json`；镜头和资产结构化分别交给导演和资产执行官。
- `art_direction` 不负责具体构图，构图、景别、机位和镜头调度由 `storyboard_director` 处理。
