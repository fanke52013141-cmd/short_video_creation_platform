# Schema Contracts

本项目中，Markdown 产物服务于人类确认和复制；JSON 产物只在确实需要下游稳定读取时才出现。剧本阶段不输出 JSON，避免让剧本专家同时承担结构化抽取职责。

## 核心 schema

| 产物 | Schema |
|---|---|
| `outputs/storyboard.json` | `schemas/storyboard.schema.json` |
| `outputs/asset_manifest.json` | `schemas/asset_manifest.schema.json` |
| `outputs/shot_asset_map.json` | `schemas/shot_asset_map.schema.json` |
| `outputs/video_prompts.json` | `schemas/video_prompt.schema.json` |
| 多参素材约束 | `schemas/reference_media.schema.json` |

`outputs/story.md` 和 `outputs/style_bible.md` 不对应 JSON schema。前者是剧本创作产物，后者是一页以内的视觉方向文件。

## story.md 契约

`story_generation` 只输出 `outputs/story.md`。该文件应服务剧本优化本身，而不是提前为下游抽字段。

禁止在剧本阶段输出：

- `outputs/story.json`
- `outputs/story_index.json`
- 镜头结构化
- 资产清单
- 角色状态拆分
- 场景资产拆分
- 道具资产拆分
- 图片提示词
- 视频提示词

镜头结构化由 `storyboard_director` 输出 `storyboard.json`；人物、场景、道具和资产结构化由 `asset_executor` 输出 `asset_manifest.json` 与 `shot_asset_map.json`。

## style_bible.md 契约

`art_direction` 只输出用户确认后的 `outputs/style_bible.md`。如果用户没有明确视觉方向，艺术总监应先给候选方案让用户选择，不直接定稿。

最终 `style_bible.md` 只包含：

- `画面风格`
- `整体色调`
- `光线风格`
- `AI 视觉执行要求`

禁止在艺术方向阶段输出：

- `art_direction.json`
- 独立 `构图倾向` 字段
- 独立 `禁止出现的视觉元素` 字段
- 逐镜头构图
- 景别表
- 机位设计
- 分镜

具体构图、景别、机位和镜头调度由 `storyboard_director` 负责。

## storyboard.json 契约

`storyboard.json` 的每个 shot 必须只包含导演分镜所需字段：

- `shot_id`: 镜头编号，`S001`、`S002`...
- `scene_id`: 场景 / 时空单元编号，`SC001`、`SC002`...，由导演创建，可被多个 shot 复用
- `duration_seconds`，必须 `>0` 且 `<=15`
- `framing`
- `camera_move`
- `action_desc`

导演分镜不得包含资产草表、资产 ID、音色 ID、图片提示词或视频提示词。`characters_in_shot`、`location`、`character_ids`、`prop_ids`、`prompt_cn` 等字段都不属于导演阶段。

## asset_manifest.json 契约

`asset_manifest.json` 按资产类别分为：

- `characters`
- `scenes`
- `props`

每个资产至少包含：

- `asset_name`: Seedance 稳定调用名，例如 `林小满`、`主体1`、`雨夜客厅场景`、`手机`。
- `asset_type`: `character | scene | prop`。
- `appears_in_shots`: 该资产出现的分镜 ID。
- `generation_required`: 是否需要生成独立资产图。

推荐补充字段：

- `naming_strategy`: `numbered_subject | custom_concrete_name | simple_scene_number | concrete_scene_name | key_prop_name`。
- `seedance_label`: 提示词中的稳定主体 / 场景 / 道具标签。
- `definition_sentence`: 对用户素材的前置定义句，例如“将图片1中穿红裙、戴草帽的女性定义为主体1”。
- `reference_bindings`: 同一主体或场景绑定的图片 / 视频 / 生成资产。
- `required_reference_set`: 人物通常为 `face_closeup + full_body_styling`，场景通常为 `scene_reference`。
- `handling_policy`: 说明是绑定现有参考、生成身份资产组、生成场景参考、正文控制道具、沿用参考道具、删除道具还是生成独立道具。

命名规则：

- 人物不得使用 `CHAR_001` 作为主名称。
- 场景不得使用 `ENV_001` 作为主名称。
- 道具不得使用 `PROP_001` 作为主名称。
- 人物不因表情、动作、姿态、角度拆成多个资产。
- 场景不因普通光线、时间、天气变化拆成多个资产。
- 道具只保留核心剧情道具；普通背景物件不强行生成独立资产。

## shot_asset_map.json 契约

`shot_asset_map.json` 是分镜与稳定资产名之间的唯一映射表。每条记录至少包含：

- `shot_id`
- `characters`
- `scenes`
- `props`

其中 `characters`、`scenes`、`props` 中的值必须全部存在于 `asset_manifest.json` 的 `asset_name`。

`shot_asset_map.json` 不写动作、不写提示词、不写素材分析。

## 视频提示词契约

`video_prompts.md` 是最终人工复制到即梦的主交付文件。`video_prompts.json` 是同一组 `V###` 的结构化计划，用于校验和后续自动化。

每个视频提示词使用 `V###` 命名。一个 `V###` 可以对应一个或多个连续 `S###`。合并对象是 `S###`，不是 `SC###`；`SC###` 只是合并边界。

合并必须满足：

1. `source_shots` 连续。
2. 同一 `scene_id`。
3. 合并后时长之和 `<=15s`。
4. 动作、情绪或空间关系连续，无场景切换、无时间跳跃。

强连续动作优先合并，避免手部、道具、姿态和情绪穿帮。景别变化不是禁止合并的理由。

每条 `V###` 必须包含 `merge_decision`，说明合并或不合并的策略、原因和连续性风险。

同一场景内连续多镜头必须引入：

```text
参考@上一分镜_站位，保持人物空间关系、朝向和相对位置不变
```

场景切换时不得引入上一分镜站位锚点。

## 原则

- 剧本阶段先保证剧本质量，不承担结构化抽取。
- 艺术方向阶段先保证用户确认的视觉边界，不承担具体构图。
- 导演阶段只做镜头结构化和场景分组，不做资产拆分。
- 资产阶段只做 Seedance 稳定命名、素材绑定、生成决策和 shot 映射，不写提示词。
- JSON 只在导演、资产执行、视频计划等明确需要机器校验的阶段出现。
- 新增影响下游读取的字段时，应同步更新 schema、Skill 文档和 `scripts/validate_project.py`。
- 旧项目不满足当前契约时，应重新初始化或标记为 legacy，不要伪装通过。
