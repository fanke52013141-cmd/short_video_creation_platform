# Skill: video_prompt_generator
**Version**: 2.2.0

## Source Prompt
`skills/raw_prompts/seedance_video_prompt.source.md`

## Purpose
生成最终可复制到即梦 / Seedance 2.0 的中文视频提示词，并同时输出可校验的结构化视频计划。

本 Skill 支持两类使用场景：

1. **流水线分镜生成**：读取 `storyboard.json`、`shot_asset_map.json`、资产图和分镜参考图，按规则生成 `V###` 视频提示词。
2. **多模态多参考生成**：根据用户提供的文本、图片、音频、视频素材，识别素材角色，区分参考类素材与操作对象类素材，生成可直接交付 Seedance 2.0 的中文提示词。

本 Skill 只输出中文，不输出英文版本，不输出中英对照，不输出素材分析过程。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/storyboard.json",
  "storyboard_reference_dir": "./outputs/storyboards",
  "asset_reference_dir": "./outputs/assets",
  "shot_asset_map_path": "./outputs/shot_asset_map.json",
  "reference_media": [
    {
      "asset_name": "雨夜客厅",
      "media_type": "image | audio | video | text",
      "role": "first_frame | last_frame | keyframe | character_asset | scene_asset | style_reference | voice_reference | music_reference | ambience_reference | action_reference | style_video_reference | overall_reference | edit_object | extend_object",
      "usage_type": "reference | operation_object | text_only"
    }
  ],
  "user_video_intent": ""
}
```

## Outputs
```json
{
  "video_prompts_path": "./outputs/video_prompts.md",
  "video_prompts_json_path": "./outputs/video_prompts.json"
}
```

`video_prompts.md` 给人复制到即梦使用；`video_prompts.json` 给校验脚本、CI 和后续自动化使用。两者必须表达同一组 `V###`。

## Task Type System

每条 `V###` 必须声明任务类型：

| 任务类型 | 适用情况 | 正文引用方式 |
|---|---|---|
| `pipeline_shot_generation` | 默认流水线分镜生成 | 参考分镜图、人物资产、场景资产 |
| `multimodal_reference` | 使用图片、音频、视频作为参考维度生成新视频 | 参考类素材使用 `参考@资产名` |
| `video_edit` | 修改已有视频本体 | 使用 `严格编辑 @资产名`，禁止写 `参考@资产名` |
| `video_extend` | 向前或向后延长已有视频 | 使用 `向前延长 @资产名` 或 `向后延长 @资产名`，禁止写 `参考@资产名` |
| `combined_task` | 参考某素材，同时编辑或延长另一素材 | 参考素材写 `参考@资产名`；操作对象直接写 `严格编辑 @资产名` 或 `向后延长 @资产名` |
| `track_stitch` | 多段视频衔接成连续轨道 | `@视频1 + 过渡画面 + 接 @视频2` |

## Material Role Rules

### Text Input
文本输入用于补充主体、场景、动作、情绪、风格、剧情、台词或视频意图。

- 无参考素材时，补全主体、场景、动作、镜头、光线、色彩、节奏和声音。
- 有参考素材时，文本主要补充动作、情绪、叙事目标、镜头演进和声音设计。

### Image Input
图片必须声明角色：

- `首帧`：锁定起始构图、起始画面、主体初始状态。正文写“从首帧出发”。
- `尾帧`：锁定结束构图、最终画面、主体最终状态。正文写画面如何抵达尾帧。
- `关键帧`：锁定中间状态。正文写关键帧前后的动作过渡。
- `场景资产`：锁定空间、时间、天气、环境光基调。正文补主体动作和镜头运动。
- `人物资产`：锁定人物外观、服装、身份、面部特征。正文不重复外貌，重点补动作、表情、姿态、情绪。
- `风格参考图`：只锁定色调、质感、画风、视觉语言，不锁定图片内容。必须写明：仅参考风格，不参考内容。

### Audio Input
音频必须声明角色：

- `声音参考`：锁定说话人音色，不锁定情绪。台词处再次调用该资产，并写明情绪、语速、音量、停顿、句尾走向和伴随动作。
- `配乐参考`：锁定音乐基调、节奏和情绪走向。正文写画面节奏如何对齐配乐。
- `环境音参考`：锁定声音空间感或环境氛围。正文写声音与画面的关系。

### Video Input
视频必须先判断是参考类还是操作对象类。

参考类视频正文使用 `参考@资产名`：动作参考、风格视频参考、整体参考。

操作对象类视频正文直接使用 `@资产名`，禁止加 `参考` 前缀：

- `编辑对象`：必须写 `严格编辑 @资产名，将...修改为...`，并明确保持哪些主体、动作、构图或背景不变。
- `延长对象`：必须写 `向前延长 @资产名` 或 `向后延长 @资产名`，并要求主体、风格、声音、叙事与原片保持一致。

**硬性规则：编辑对象和延长对象绝不能写成 `参考@资产名`。**

## Asset Declaration Rules

所有参考素材和操作对象必须在提示词最前面统一声明。

```markdown
【资产声明区】
@资产名一（首帧）
@资产名二（人物资产）
@资产名三（声音参考）
@资产名四（编辑对象）
```

如果没有任何参考素材，写：

```markdown
【资产声明区】
无参考素材，以下内容根据用户文字需求生成。
```

声明规则：

- 正文引用的资产名必须与声明区完全一致。
- 禁止用系统内部 Asset ID 替代资产名。
- 同一素材多主体时，在声明区分别命名，例如 `@警察`、`@小偷`。
- 多素材同一主体时，统一绑定为一个资产名，并注明来自哪些素材。
- 未提前定义的主体必须使用 `@主体名@素材名` 绑定语法，不得裸写。

## Lock And Complement Principle

提示词内容 = 未被素材锁定的必要维度 + 素材之间的关系说明 + 镜头可执行描述。

- 有首帧、尾帧、关键帧时，不重复描述已锁定构图，重点写画面演进。
- 有人物资产时，不重复人物外观，重点写动作、表情、姿态和情绪。
- 有环境资产时，不重复环境细节，重点写主体在环境中的行动和镜头运动。
- 有风格参考时，只写“仅参考风格，不参考内容”。
- 有声音参考时，不重复音色，只写情绪、语速、音量、停顿和句尾走向。
- 有动作参考视频时，不重复解释动作模式，只写动作如何应用到当前主体和场景。
- 操作对象类素材默认锁定原片本体，正文只说明变化点和必须保持不变的部分。

冲突处理：多个参考素材在风格、色彩、构图、环境或人物状态上冲突时，必须显式写明“以某某素材为准”。默认优先级为：用户文字要求 > 首帧/尾帧/关键帧 > 人物资产 > 环境资产 > 风格参考 > 音频参考。

## Visible Camera Principle

提示词必须是摄影机可见、麦克风可听的指令。禁止只写：难过、紧张、温馨、压抑、思考、打游戏、关系疏离。必须转译为：表情变化、肢体动作、物体互动、空间距离、视线方向、光影变化、声音细节、镜头运动、节奏变化。

## Camera And Action Rules

每个镜头只能指定一种运镜方式：推近、拉远、横移、摇镜、跟随、升降、环绕、固定，选其一。禁止在同一镜头内叠加多种运镜，例如“缓慢推近的同时向右横移”。

若需求包含奔跑、跳跃、翻滚、剧烈打斗、快速追逐等高强度动作：

1. 最前面必须输出 `零、【生成风险提示】`。
2. 动作必须按“起势—发力—收势”拆分到多个镜头。
3. 有动作参考视频时，优先写“动作幅度与节奏参考@资产名”。

避免在自然语言提示词正文中强行指定精确总时长。`V###` 元数据可以保留建议时长，但正文只写节奏、停顿和动作间隔。

## Pipeline Merge Rule

相邻 shot 只有同时满足以下三项，才可合并为一个 `V###`：同一 `scene_id`、相邻 shot 时长之和 `<=15s`、动作描述连续且无场景切换或时间跳跃。不满足任一条件时，必须拆成独立 `V###`。

## Previous Storyboard Anchor Rule

同一场景内的连续多镜头，每个视频提示词必须引入：

```text
参考@上一分镜_站位，保持人物空间关系、朝向和相对位置不变
```

场景切换时不引入上一分镜，避免错误约束。

## Prop Rule

道具资产不使用 `@PROP`。道具只写入视频提示词正文描述，包括位置、状态、交互动作和视觉细节。

## Markdown Output Format

`video_prompts.md` 中每条 `V###` 必须按以下顺序输出。

```markdown
## V001
- 来源分镜：S001-S002
- 时长：10s
- 任务类型：pipeline_shot_generation

零、【生成风险提示】
仅在包含高强度动作时输出；不涉及高强度动作时省略本节。

一、【自检通过项】
- 资产命名一致：正文引用与声明区完全一致。
- 锁补匹配：已由素材锁定的维度未重复，未锁定维度已补足。
- 运镜纯度：每个镜头只使用一种运镜。
- 操作对象用语：编辑/延长对象未误写为参考素材。
- 约束条件：已写入防字幕、防 Logo、防水印。

二、【资产声明区】
@S001_分镜参考图（首帧）
@少女_默然_正面（人物资产）
@破旧公寓_深夜_冷白灯光（场景资产）

三、【中文视频提示词】
从首帧 @S001_分镜参考图 出发。镜头固定在门口中景...

约束条件：画面保持无字幕，避免生成任何文字、Logo 或水印。
```

## JSON Output Format

`video_prompts.json` 必须符合 `schemas/video_prompt.schema.json`，并为每条 `V###` 输出：

```json
{
  "video_id": "V001",
  "task_type": "pipeline_shot_generation",
  "source_shots": ["S001", "S002"],
  "duration_seconds": 10,
  "scene_id": "SC001",
  "declared_assets": [
    {
      "asset_name": "S001_分镜参考图",
      "media_type": "storyboard",
      "role": "first_frame",
      "usage_type": "reference",
      "source_path": "outputs/storyboards/S001.png"
    }
  ],
  "operation_objects": [],
  "uses_previous_storyboard_anchor": true,
  "risk_notice_required": false,
  "prompt_cn": "完整中文提示词"
}
```

JSON 质量要求：

- `video_id` 必须从 `V001` 连续递增。
- `source_shots` 必须覆盖全部 `S###`，且每个 shot 只能被覆盖一次。
- `duration_seconds` 必须 `>0` 且 `<=15`。
- `declared_assets` 必须与 Markdown 资产声明一致。
- `prompt_cn` 必须为中文提示词，不得含 `English Prompt` 或中英对照。
- 编辑/延长对象必须出现在 `declared_assets` 中，且 `usage_type` 为 `operation_object`。

## Procedure

1. 读取 `storyboard.json`，构建 shot 顺序。
2. 读取 `shot_asset_map.json`，为每个 shot 取角色、场景、道具。
3. 读取 `reference_media`，识别每份素材的类型和角色。
4. 判断任务类型：默认 `pipeline_shot_generation`，如用户提供编辑对象、延长对象或组合任务，则切换到对应类型。
5. 检查 `outputs/storyboards/S###.png` 是否存在；缺失时在提示词中标注需人工补图。
6. 检查 `outputs/assets/characters/` 与 `outputs/assets/scenes/` 是否存在有效资产图。
7. 从 `S001` 开始按顺序尝试合并相邻 shot；只有满足合并三条件时才合并。
8. 为每个 `V###` 输出自检、资产声明区、中文视频提示词和结构化 JSON 条目。
9. 同一场景连续镜头写入上一分镜站位锚点；场景切换不写。
10. 若存在高强度动作，在该 `V###` 最前面输出生成风险提示。
11. 若存在编辑/延长对象，正文直接使用 `@资产名`，不得写 `参考@资产名`。
12. 输出 `outputs/video_prompts.md` 和 `outputs/video_prompts.json`。

## Quality Gate

- [ ] 每个 `S###` 都被且仅被一个 `V###` 覆盖。
- [ ] 每个 `V###` 的建议时长 `<=15s`。
- [ ] 合并镜头满足同场景、总时长、动作连续三条件。
- [ ] 同一场景连续镜头包含上一分镜站位锚点。
- [ ] 场景切换不包含上一分镜站位锚点。
- [ ] 每条 `V###` 包含 `【自检通过项】`、`【资产声明区】`、`【中文视频提示词】`。
- [ ] `video_prompts.json` 符合 `schemas/video_prompt.schema.json`。
- [ ] JSON 覆盖全部 `S###`，且不重复覆盖。
- [ ] 所有参考素材先声明再引用。
- [ ] 编辑对象、延长对象正文中未出现 `参考@资产名`。
- [ ] 道具只写正文，不出现 `@PROP`。
- [ ] 每个镜头只指定一种运镜。
- [ ] 抽象情绪和氛围已转译为可见或可听信号。
- [ ] 有台词时，写明声音参考、情绪、语速、音量、停顿、句尾走向和伴随动作。
- [ ] 输出中文，不输出 `English Prompt`。
- [ ] 写入防字幕、防 Logo、防水印约束；如用户明确需要文字，则单独说明文字内容、位置、出现时机和样式。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `video_prompt_generator`
- `completed_phases`: 追加 `video_prompt_generator`
- `artifacts.video_prompts`: `./outputs/video_prompts.md`
- `artifacts.video_prompts_json`: `./outputs/video_prompts.json`
- `status`: `ready_for_jimeng_canvas`

## Failure Handling

- 分镜图缺失：标注缺口并要求用户回填 `outputs/storyboards/S###.png`。
- 资产图缺失：不声明为可参考图，只写正文描述并标注需补图。
- 动作不连续：拆分为独立 `V###`。
- 视频提示词出现 `@PROP`：改为正文描述。
- 编辑对象或延长对象被写成 `参考@资产名`：必须重写该 `V###`。
- 同一镜头出现多种运镜：拆分为多个镜头或保留一种主运镜。
- `video_prompts.json` 缺失、覆盖分镜不完整或重复覆盖：重建 JSON 计划。
- 抽象词未落地：改写为微表情、肢体动作、光影、声音、物体细节或空间关系。
