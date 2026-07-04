# Schema Contracts

本项目的 Markdown 产物服务于人类确认和复制，JSON 产物服务于下游 Skill 和校验脚本读取。凡是进入下游的核心 JSON，都必须满足 `schemas/` 中对应 schema。

## 核心 schema

| 产物 | Schema |
|---|---|
| `outputs/story.json` | `schemas/story.schema.json` |
| `outputs/storyboard.json` | `schemas/storyboard.schema.json` |
| `outputs/asset_manifest.json` | `schemas/asset_manifest.schema.json` |
| `outputs/shot_asset_map.json` | `schemas/shot_asset_map.schema.json` |
| 可选结构化视频提示词计划 | `schemas/video_prompt.schema.json` |

`style_bible.md` 不再对应 JSON schema。风格圣经以 Markdown 作为唯一产物，且必须保持在一页以内。

## story.json 契约

`story.json` 只保留下游必要字段：

- `title`
- `logline`
- `scenes`
- `characters`
- `plot_segments`
- `production_notes`

禁止在故事 JSON 中堆叠复杂心理层、多余元数据或不会被下游消费的分析字段。

## storyboard.json 契约

`storyboard.json` 的每个 shot 必须只包含导演分镜所需字段：

- `shot_id`: `S001`、`S002`...
- `scene_id`
- `duration_seconds`，必须 `>0` 且 `<=15`
- `framing`
- `camera_move`
- `action_desc`
- `characters_in_shot`
- `location`

导演分镜不得包含资产草表、资产 ID、音色 ID、图片提示词或视频提示词。出现 `CHAR_001`、`ENV_001`、`PROP_001` 等旧式抽象资产 ID 时，视为不合格。

## asset_manifest.json 契约

`asset_manifest.json` 按资产类别分为：

- `characters`
- `scenes`
- `props`

每个资产至少包含：

- `asset_name`: 使用“特征 + 状态”命名，例如 `少女_默然_正面`。
- `asset_type`: `character | scene | prop`。
- `appears_in_shots`: 该资产出现的分镜 ID。
- `generation_required`: 是否需要生成独立资产图。

资产命名禁止使用 `CHAR_001`、`ENV_001`、`PROP_001` 作为主标识。此类编号不符合本流程的可读交付目标。

## shot_asset_map.json 契约

`shot_asset_map.json` 是分镜与资产之间的唯一映射表。每条记录至少包含：

- `shot_id`
- `characters`
- `scenes`
- `props`

其中 `characters`、`scenes`、`props` 中的值必须全部存在于 `asset_manifest.json` 的 `asset_name`。

## 视频提示词契约

`video_prompts.md` 是最终人工复制到即梦的主交付文件。

每个视频提示词使用 `V###` 命名。一个 `V###` 可以对应一个或多个 `S###`，但合并必须同时满足：

1. 同一 `scene_id`。
2. 合并后时长之和 `<=15s`。
3. 动作描述连续，无场景切换、无时间跳跃。

同一场景内连续多镜头必须引入：

```text
参考@上一分镜_站位，保持人物空间关系、朝向和相对位置不变
```

场景切换时不得引入上一分镜站位锚点。

## 原则

- Markdown 可以灵活，JSON 字段必须稳定。
- 下游 Skill 不得依赖未写入 JSON 的关键事实。
- 新增影响下游读取的字段时，应同步更新 schema、Skill 文档和 `scripts/validate_project.py`。
- 旧项目不满足 schema 时，应重新初始化或标记为 legacy，不要伪装通过。
