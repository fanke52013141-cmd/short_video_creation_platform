# Changelog

## 2026-07-04 - v1.0.3

### Changed
- [process] 简化第一阶段：`story_generation` 只输出 `outputs/story.md`，不再输出 `story.json` 或任何 story index。
- [process] 明确艺术总监先于导演出现，但只负责视觉方向；具体构图、景别、机位和镜头调度归 `storyboard_director`。
- [process] 沉淀人物状态资产规则：人物资产采用 `人物稳定名_状态`，例如 `林小满_雨夜接电话状态`。
- [process] 明确人物资产生产为一张 21:9 人物状态资产图，可在同一张图里包含特写、正面、侧面、后视图。
- [process] 简化资产提示词生成输入：使用 `story.md + style_bible.md + asset_type + asset_name + output_prompt_path`。
- [process] 增加分镜参考图规则：每个 `S###` 必须声明 `recommended_frame_role`，并判断是否引用上一分镜图片作为站位参考。
- [process] 沉淀视频分镜合并规则：合并对象是连续 `S###`，不是 `SC###`；同一 `scene_id` 内连续分镜且总时长 `<=15s` 才允许合并。
- [process] 明确视频提示词阶段必须输出 `frame_references`，说明每张分镜图在 `V###` 中承担首帧、尾帧或关键帧角色。
- [skill] 将 `image_generation_executor` 升级到 1.3.0：改为单资产图片执行契约。
- [skill] 将 `video_prompt_generator` 升级到 2.6.0：吸收最新中文视频提示词规则，新增锁定与补足、镜头可见、具象化转译、单运镜纯度和三段输出格式。
- [prompt] 更新 `skills/raw_prompts/seedance_video_prompt.source.md`。
- [script] `validate_project.py` 只校验当前生产链路。
- [schema] `video_prompt.schema.json` 只保留当前流水线视频生成计划。
- [docs] 更新 README、flow、local run 模板和质量门。
- [examples] 更新 `examples/minimal_run/`。

### Reason
- 资产提示词生成需要完整剧本上下文，否则人物、场景和道具只剩孤立名称，难以做准设定。
- 视频提示词必须把抽象情绪、氛围和事件转译为可见动作、光影、声音和空间关系，避免文学化描述。
- 强连续动作如果拆成多次生成，容易造成动作、手部、道具位置和人物姿态穿帮，因此在同场景且总时长不超过 15 秒时应优先合并。

### Validation
- 待 CI 验证：`python scripts/validate_project.py examples/minimal_run --phase all`。

## 2026-07-04 - v1.0.2

### Changed
- [ci] 新增 GitHub Actions workflow：编译 `scripts/validate_project.py`、解析 `checkpoint.template.json` 与全部 schema JSON、运行最小样例 `examples/minimal_run --phase all`。
- [examples] 新增 `examples/minimal_run/`，提供一套可跑通的最小本地 run，用作回归测试基线。
- [schema] 扩展 `schemas/video_prompt.schema.json`，要求 `video_prompts.json` 输出结构化 `V###` 计划。
- [script] `validate_project.py` 新增 `video_prompts.json` 校验。

### Reason
- 仅有 Markdown 提示词无法可靠校验 shot 覆盖、任务类型、操作对象和素材声明关系；结构化 JSON 可作为机器可验证的生产计划。

### Validation
- 已用本地最小样例跑通 `python scripts/validate_project.py examples/minimal_run --phase all`。

## 2026-07-04 - v1.0.1

### Changed
- [skill] 将 `video_prompt_generator` 升级到 2.1.0，补入早期 Seedance 视频提示词规则。

### Validation
- 已在本地构建新版 `validate_project.py` 并通过 Python 语法编译检查。

## 2026-07-04 - v1.0.0

### Changed
- [process] 将旧 13 阶段流程重构为 7 阶段即梦画布前置流程：`story_generation` → `art_direction` → `storyboard_director` → `asset_executor` → `asset_prompt_generation` → `storyboard_prompt_generator` → `video_prompt_generator`。
- [outputs] 将本地 run 输出目录改为扁平结构。
- [script] 重写 `validate_project.py`，按新扁平目录和新 schema 校验。
