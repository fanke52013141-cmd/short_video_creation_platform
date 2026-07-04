# 短视频创作平台

这是一套面向即梦画布生产的短视频创作流程仓库。仓库不直接生成最终视频，也不管理外部生成后的成片审查；它负责把用户想法转化为剧本、风格约束、分镜序列、资产清单、资产/分镜生图提示词和最终视频提示词。

## 核心原则

- 剧本优先：`story_generation` 只优化剧本，不输出结构化 JSON。
- 最小必要输入：下游只读取当前阶段真正需要的文件。
- 职责单一：导演只做镜头结构化，资产执行官只做资产提取和映射，视频提示词生成器只做可复制到即梦的提示词。
- 流程精简：流程终点是进入即梦画布生产，不在仓库内追加音色、外部结果、媒体审查和最终打包节点。
- 交付清晰：最终交付给即梦画布的内容只包含剧本、视频提示词、有效角色资产、有效场景资产和分镜参考图。

## 推荐试跑顺序

1. 执行 `scripts/init_local_run.ps1 -ProjectSlug your-project-slug` 初始化本地创作目录。
2. 填写 `local_runs/YYYY-MM-DD/your-project-slug/inputs/idea_brief.md`。
3. 运行 `skills/story_generation.md`，只产出 `outputs/story.md`。
4. 人工确认剧本后运行 `skills/art_direction.md`，产出一页以内的 `outputs/style_bible.md`。
5. 运行 `skills/storyboard_director.md`，由导演负责结构化镜头，产出 `outputs/storyboard.json`。
6. 运行 `skills/asset_executor.md`，由资产执行官负责人物、场景、道具拆分，产出 `outputs/asset_manifest.json` 和 `outputs/shot_asset_map.json`。
7. 并行运行 `skills/character_prompt_generator.md`、`skills/scene_prompt_generator.md`、`skills/prop_prompt_generator.md`。
8. 去即梦生成资产图片，并回填到 `outputs/assets/characters/`、`outputs/assets/scenes/`、`outputs/assets/props/`。
9. 运行 `skills/storyboard_prompt_generator.md`，产出 `outputs/storyboard_prompts.md`。
10. 去即梦生成分镜参考图，并回填到 `outputs/storyboards/S001.png`、`S002.png` 等。
11. 运行 `skills/video_prompt_generator.md`，产出 `outputs/video_prompts.md` 和 `outputs/video_prompts.json`。
12. 将 `story.md`、`video_prompts.md`、`assets/characters/`、`assets/scenes/`、`storyboards/` 交给即梦画布生产。

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

- 角色：`{外貌特征}_{情绪状态}_{角度}`，例如 `少女_默然_正面`。
- 场景：`{地点名}_{时间/光线}_{氛围}`，例如 `破旧公寓_深夜_冷白灯光`。
- 道具：`{物品名}_{视角/状态}`，例如 `旧皮箱_正面`。
- 分镜：`S{三位数序号}`，例如 `S001`。
- 视频提示词：`V{三位数序号}`，例如 `V001`，可合并多个连续分镜。

## 校验

初始化后可运行：

```bash
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase initialized
```

完整项目可运行：

```bash
python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase all
```

可选阶段：`initialized`、`story`、`art`、`storyboard`、`assets`、`asset_prompt_generation`、`storyboard_prompt_generation`、`video_prompts`、`all`。

## 仓库边界

- 仓库保存流程、Skill、配置模板、schema、检查规则和文档。
- 真实创作产物、参考素材、生成图片、日志和 `checkpoint.json` 放入本地 `local_runs/YYYY-MM-DD/project_slug/`，不提交仓库。
- `story_generation` 不输出 `story.json`；镜头和资产结构化分别交给导演和资产执行官。
- 道具资产不作为最终即梦画布交付目录单独交付；它们应写入 `video_prompts.md` 正文描述。
