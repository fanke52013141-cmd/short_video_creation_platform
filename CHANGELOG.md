# Changelog

## 2026-07-04 - v1.0.3

### Changed
- [process] 简化第一阶段：`story_generation` 只输出 `outputs/story.md`，不再输出 `story.json` 或任何 story index。
- [process] 明确艺术总监先于导演出现，但只负责视觉方向；具体构图、景别、机位和镜头调度归 `storyboard_director`。
- [process] 沉淀人物状态资产规则：人物资产采用 `人物稳定名_状态`，例如 `林小满_雨夜接电话状态`，不默认拆成大头特写和全身妆造两个资产。
- [process] 明确人物资产生产为一张 21:9 人物状态资产图，可在同一张图里包含特写、正面、侧面、后视图。
- [process] 简化资产提示词生成输入：使用 `story.md + style_bible.md + asset_type + asset_name + output_prompt_path`，不再使用 `asset_prompt_tasks.json`、`task_id`、`asset_payload` 或 `prompt_outputs` 数组。
- [process] 增加分镜参考图规则：每个 `S###` 必须声明 `recommended_frame_role`，并判断是否引用上一分镜图片作为站位参考。
- [process] 沉淀视频分镜合并规则：合并对象是连续 `S###`，不是 `SC###`；同一 `scene_id` 内连续分镜且总时长 `<=15s` 才允许合并。
- [process] 明确视频提示词阶段必须输出 `frame_references`，说明每张分镜图在 `V###` 中承担首帧、尾帧或关键帧角色。
- [skill] 将 `story_generation` 升级到 3.0.0。
- [skill] 将 `art_direction` 升级到 2.1.0。
- [skill] 将 `storyboard_director` 升级到 2.2.0。
- [skill] 将 `asset_executor` 升级到 1.4.0：固定人物状态资产、场景资产、核心道具、shot 映射和单个 `output_prompt_path`。
- [skill] 将 `character_prompt_generator` 升级到 2.4.0：单次只处理一个人物状态资产。
- [skill] 将 `scene_prompt_generator`、`prop_prompt_generator` 保持为 2.3.0 简化输入模型。
- [skill] 将 `image_generation_executor` 升级到 1.2.0：允许一张 21:9 人物多视角资产图作为合法单图输出。
- [skill] 将 `storyboard_prompt_generator` 升级到 1.1.0：新增上一分镜站位参考判断和帧角色判断。
- [skill] 将 `video_prompt_generator` 升级到 2.4.0：最小输入加入 `storyboard_prompts.md`，并要求 `frame_references`。
- [prompt] 新增 `skills/raw_prompts/storyboard_prompt_generator.source.md`。
- [prompt] 更新 `skills/raw_prompts/character_prompt_generator.source.md` 和 `skills/raw_prompts/seedance_video_prompt.source.md`。
- [script] `validate_project.py` 现在校验分镜提示词中的 `recommended_frame_role`、`uses_previous_storyboard_reference`，禁止跨 `scene_id` 引用上一分镜。
- [script] `validate_project.py` 现在校验视频合并的 source shots 连续、同一 `scene_id`、合并总时长 `<=15s`。
- [schema] `asset_manifest.schema.json` 改为单个 `output_prompt_path`。
- [schema] `video_prompt.schema.json` 要求每条 `V###` 包含 `frame_references` 和 `merge_decision`。
- [config] 更新 `asset_policy`、`image_generation_policy`、`storyboard_prompt_policy` 和 `video_prompt_policy`。
- [docs] 更新 README、flow、local run 模板和质量门。
- [examples] 更新 `examples/minimal_run/`：人物资产改为 `林小满_雨夜接电话状态`，分镜提示词加入帧角色和站位锚点，视频计划加入 `frame_references`。

### Reason
- 资产提示词生成需要完整剧本上下文，否则人物、场景和道具只剩孤立名称，难以做准设定。
- 人物资产应以“人物稳定名 + 状态”作为生产单位，而不是默认拆成身份大头和全身妆造两个产物。
- 分镜连续生成时，同场景且站位延续的相邻分镜应可引用上一分镜图片作为站位锚点，降低人物位置和空间关系漂移。
- 视频提示词阶段必须知道每张分镜图在最终视频中承担首帧、尾帧还是关键帧，才能正确声明素材角色。
- 强连续动作如果拆成多次生成，容易造成动作、手部、道具位置和人物姿态穿帮，因此在同场景且总时长不超过 15 秒时应优先合并。

### Validation
- 待 CI 验证：`python scripts/validate_project.py examples/minimal_run --phase all`。

## 2026-07-04 - v1.0.2

### Changed
- [ci] 新增 GitHub Actions workflow：编译 `scripts/validate_project.py`、解析 `checkpoint.template.json` 与全部 schema JSON、运行最小样例 `examples/minimal_run --phase all`。
- [examples] 新增 `examples/minimal_run/`，提供一套可跑通的最小本地 run，用作回归测试基线。
- [schema] 扩展 `schemas/video_prompt.schema.json`，要求 `video_prompts.json` 输出结构化 `V###` 计划。
- [schema] 新增 `schemas/reference_media.schema.json`，沉淀多参素材的类型、角色和用途约束。
- [skill] 将 `video_prompt_generator` 升级到 2.2.0，要求同时输出 `outputs/video_prompts.md` 与 `outputs/video_prompts.json`。
- [script] `validate_project.py` 新增 `video_prompts.json` 校验。
- [config] 更新 `video_prompt_policy` 与最终交付清单，加入 `outputs/video_prompts.json`。

### Reason
- 仅有 Markdown 提示词无法可靠校验 shot 覆盖、任务类型、操作对象和素材声明关系；结构化 JSON 可作为机器可验证的生产计划。
- CI 与最小样例可以防止后续修改 Skill、schema 或脚本时破坏核心流程。

### Validation
- 已在本地构建并编译新版 `validate_project.py`。
- 已用本地最小样例跑通 `python scripts/validate_project.py examples/minimal_run --phase all`。

## 2026-07-04 - v1.0.1

### Changed
- [skill] 将 `video_prompt_generator` 升级到 2.1.0，补入 Seedance 2.0 多模态多参考任务体系。
- [skill] 新增任务类型规则：`pipeline_shot_generation`、`multimodal_reference`、`video_edit`、`video_extend`、`combined_task`、`track_stitch`。
- [skill] 新增素材角色识别：首帧、尾帧、关键帧、人物资产、场景资产、风格参考、声音参考、配乐参考、环境音参考、动作参考、整体参考、编辑对象、延长对象。
- [skill] 强化硬规则：编辑对象与延长对象正文中禁止写 `参考@资产名`，必须分别使用 `严格编辑 @资产名`、`向前延长 @资产名` 或 `向后延长 @资产名`。
- [script] `validate_project.py` 增加视频提示词静态检查。
- [config] 更新 `video_prompt_policy`，记录多参考素材角色、操作对象规则、必需输出段落和高强度动作风险提示规则。

### Reason
- 即梦 / Seedance 2.0 的多参考素材任务中，最容易出错的是把待编辑/待延长视频误写成参考素材。

### Validation
- 已在本地构建新版 `validate_project.py` 并通过 Python 语法编译检查。

## 2026-07-04 - v1.0.0

### Changed
- [process] 将旧 13 阶段流程重构为 7 阶段即梦画布前置流程：`story_generation` → `art_direction` → `storyboard_director` → `asset_executor` → `asset_prompt_generation` → `storyboard_prompt_generator` → `video_prompt_generator`。
- [outputs] 将本地 run 输出目录改为扁平结构。
- [skill] 新增 `skills/asset_executor.md`、`skills/storyboard_prompt_generator.md`、`skills/video_prompt_generator.md`。
- [script] 重写 `validate_project.py`，按新扁平目录和新 schema 校验。

### Reason
- 新目标是进入即梦画布生产，而不是在仓库内管理完整外部生成回流与最终审查。
