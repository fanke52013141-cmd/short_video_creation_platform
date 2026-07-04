# 短视频创作平台

这是一套面向即梦画布生产的短视频创作流程仓库。仓库不直接生成最终视频，也不管理外部生成后的成片审查；它负责把用户想法转化为剧本、风格约束、分镜序列、资产清单、资产/分镜生图提示词和最终视频提示词。

## 核心原则

- 剧本优先：`story_generation` 只优化剧本，不输出结构化 JSON。
- 用户确认：剧本与视觉方向都需要用户确认后再进入下游。
- 艺术先行：艺术总监先定画面风格、色调、光线和 AI 视觉执行要求；导演后续负责具体构图与分镜。
- 最小必要输入：下游只读取当前阶段真正需要的文件。
- Seedance 友好：人物和场景使用稳定命名与素材绑定，不按表情、动作、普通光影变化拆资产。
- 资产提示词输入保持简单：`story.md + style_bible.md + asset_type + asset_name + output_prompt_path`。
- 单图生成：每个资产图片任务只生成一张图片，禁止拼接图、四宫格、设定表或对比图。
- 交付清晰：最终交付给即梦画布的内容只包含剧本、视频提示词、有效角色资产、有效场景资产和分镜参考图。

## 推荐试跑顺序

1. 执行 `scripts/init_local_run.ps1 -ProjectSlug your-project-slug` 初始化本地创作目录。
2. 填写 `local_runs/YYYY-MM-DD/your-project-slug/inputs/idea_brief.md`。
3. 运行 `skills/story_generation.md`，只产出 `outputs/story.md`。
4. 用户与剧本专家反复讨论，直到用户确认剧本可以进入下一阶段。
5. 运行 `skills/art_direction.md`，用户确认后产出 `outputs/style_bible.md`。
6. 运行 `skills/storyboard_director.md`，产出 `outputs/storyboard.json`。
7. 运行 `skills/asset_executor.md`，产出 `outputs/asset_manifest.json` 和 `outputs/shot_asset_map.json`。
8. 根据 `asset_manifest.json` 里的 `prompt_outputs`，循环运行人物、场景、必要道具提示词生成器。
9. 每次提示词生成器只输入：剧本、风格圣经、资产类型、资产名和输出路径。
10. 运行或手动执行 `skills/image_generation_executor.md` 生成资产图片；每个任务只生成一张图片。
11. 将有效资产图片回填到 `outputs/assets/characters/`、`outputs/assets/scenes/`、`outputs/assets/props/`。
12. 运行 `skills/storyboard_prompt_generator.md`，产出 `outputs/storyboard_prompts.md`。
13. 生成分镜参考图，并回填到 `outputs/storyboards/S001.png`、`S002.png` 等。
14. 运行 `skills/video_prompt_generator.md`，产出 `outputs/video_prompts.md` 和 `outputs/video_prompts.json`。

## 输出目录

```text
outputs/
├── story.md
├── style_bible.md
├── storyboard.json
├── asset_manifest.json
├── shot_asset_map.json
├── image_generation_queue.json
├── image_generation_queue.md
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

- 人物：优先使用剧本中的唯一稳定人名或身份标签，例如 `林小满`、`警察`；无明确名称时用 `主体1`、`主体2`。
- 场景：优先使用具象场景名，例如 `雨夜客厅场景`；无明确名称时用 `场景1`、`场景2`。
- 道具：只管控核心剧情道具；普通背景物件不强行生成独立资产。
- 资产提示词：每次只处理一个资产名和一个输出路径；需要完整剧本和风格圣经，不需要 `task_id` 或 `asset_payload`。
- 分镜：`S{三位数序号}`，例如 `S001`。
- 场景/时空单元：`SC{三位数序号}`，例如 `SC001`。
- 视频提示词：`V{三位数序号}`，例如 `V001`，可合并多个连续分镜。

## 校验

```bash
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase all
```

## 仓库边界

- 仓库保存流程、Skill、配置模板、schema、检查规则和文档。
- 真实创作产物、参考素材、生成图片、日志和 `checkpoint.json` 放入本地 `local_runs/YYYY-MM-DD/project_slug/`，不提交仓库。
- `story_generation` 不输出 `story.json`；镜头和资产结构化分别交给导演和资产执行官。
- `art_direction` 不负责具体构图，构图、景别、机位和镜头调度由 `storyboard_director` 处理。
