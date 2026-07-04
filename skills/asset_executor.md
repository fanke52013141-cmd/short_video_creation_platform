# Skill: asset_executor
**Version**: 1.3.0

## Purpose
从 `story.md` 和 `storyboard.json` 中固定后续生产需要的稳定资产：人物、场景和必要核心道具。

本 Skill 是资产命名、素材绑定和分镜资产映射的唯一来源。它不写图片提示词，不生成图片，不决定视频合并。

核心目标不是把资产拆细，而是把资产固定下来：

```text
资产类型 + 资产名称 + 必要输出位置
```

资产提示词生成阶段仍然可以读取完整 `story.md`，因为角色设定、场景气质和道具意义需要剧情上下文。资产执行官不需要把剧情压缩成一堆 payload 字段。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "storyboard_json_path": "./outputs/storyboard.json",
  "reference_media": []
}
```

## Outputs
```json
{
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "shot_asset_map_path": "./outputs/shot_asset_map.json"
}
```

## Seedance Naming Policy

### 1. 人物命名

允许两种命名方式。

#### A. 序号标准化命名

适合通用素材或用户没有给角色名时。

```text
主体1、主体2、主体3...
```

如果绑定用户图片或视频，必须写定义句：

```text
将图片1中穿红裙、戴草帽的女性定义为主体1。
```

#### B. 自定义具象命名

适合剧情项目，优先使用剧本中的人名或唯一稳定身份标签。

```text
林小满、警察、小偷、女主
```

要求：
- 名称必须唯一稳定。
- 全程统一叫法。
- 不可中途改名。
- 禁止用 `CHAR_001`、`AssetA` 之类内部 ID 当人物名。

### 2. 人物素材绑定

同一人物跨多张参考图或视频，必须共用同一个人物命名。

```text
林小满 → 人脸大头特写 + 全身妆造图
```

不得因为表情、动作、姿态、坐下、抬手、哭泣、微笑等常规状态拆成多个角色资产。

如果项目需要人物身份稳定，推荐输出两份人物图片提示词：

```text
outputs/assets/characters/林小满_人脸大头特写.md
outputs/assets/characters/林小满_全身妆造.md
```

这不是拆人物资产。资产名称仍然只有一个：`林小满`。只是同一个人物资产有两个输出位置。

### 3. 场景命名

允许两种命名方式。

```text
场景1、场景2
宿舍场景、悬崖竹林场景、雨夜客厅场景
```

要求：
- 场景名称只概括环境，不做复杂编码。
- 一张场景参考图对应一个场景资产名。
- 光线、时间、天气变化通常不新建场景资产。

### 4. 场景拆分原则

不因为以下变化拆新场景资产：

- 白天 → 傍晚
- 晴天 → 阴天
- 自然光强弱变化
- 冷光 / 暖光变化
- 雨夜、清晨、傍晚等光影变化

只有以下情况才新建场景资产：

- 空间结构变化。
- 建筑布局变化。
- 地点发生实质切换。
- 从现实空间进入梦境、回忆、手机屏幕世界、监控视角等独立叙事空间。

### 5. 道具处理原则

不需要把画面所有道具逐一生成或描述。只管控核心剧情道具。

道具分三类：

1. `inherited_from_reference`
   - 参考素材里已有的普通道具。
   - 默认保留，不单独生成，不额外描述。

2. `text_prompt_control`
   - 需要新增、出现、移动或被人物交互的关键道具。
   - 不生成独立道具图，后续在视频提示词正文中描述。

3. `generate_independent_prop`
   - 剧情关键、反复出现、需要特写、外形复杂或状态变化明显的道具。
   - 才生成独立道具资产提示词。

多余道具需要移除时，使用 `remove_by_instruction`，只写明删除目标，不反向列出剩余所有道具。

## asset_manifest.json Contract

```json
{
  "naming_policy": "seedance_subject_scene_binding",
  "characters": [
    {
      "asset_type": "character",
      "asset_name": "林小满",
      "seedance_label": "林小满",
      "definition_sentence": "将生成的人物参考图统一定义为林小满。",
      "reference_bindings": [],
      "appears_in_shots": ["S001", "S002"],
      "generation_required": true,
      "handling_policy": "generate_identity_bundle",
      "prompt_outputs": [
        "./outputs/assets/characters/林小满_人脸大头特写.md",
        "./outputs/assets/characters/林小满_全身妆造.md"
      ],
      "notes": "常规表情和动作不拆新人物资产"
    }
  ],
  "scenes": [
    {
      "asset_type": "scene",
      "asset_name": "雨夜客厅场景",
      "seedance_label": "雨夜客厅场景",
      "reference_bindings": [],
      "appears_in_shots": ["S001", "S002"],
      "generation_required": true,
      "handling_policy": "generate_scene_reference",
      "prompt_outputs": [
        "./outputs/assets/scenes/雨夜客厅场景.md"
      ]
    }
  ],
  "props": [
    {
      "asset_type": "prop",
      "asset_name": "手机",
      "seedance_label": "手机",
      "appears_in_shots": ["S001", "S002"],
      "generation_required": false,
      "handling_policy": "text_prompt_control",
      "prompt_outputs": [],
      "notes": "普通手机不生成独立道具图，后续视频提示词正文控制"
    }
  ]
}
```

### Minimal Asset Prompt Input

资产提示词生成器每次只需要：

```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_type": "character",
  "asset_name": "林小满",
  "output_prompt_path": "./outputs/assets/characters/林小满_人脸大头特写.md"
}
```

不需要：

- `task_id`
- `asset_payload`
- `usage_context`
- `generation_brief`
- 单独的 `asset_prompt_tasks.json`

图片用途由 `output_prompt_path` 的文件名约定承载，例如 `人脸大头特写`、`全身妆造`、`场景参考图`。

## shot_asset_map.json Contract

```json
{
  "shot_assets": [
    {
      "shot_id": "S001",
      "characters": ["林小满"],
      "scenes": ["雨夜客厅场景"],
      "props": ["手机"]
    }
  ]
}
```

`shot_asset_map.json` 只映射稳定主体、场景和关键道具名称，不写动作、不写提示词、不写素材分析。

## Procedure

1. 读取 `story.md`，识别剧情中的人物、地点、关键道具和用户参考素材关系。
2. 读取 `storyboard.json`，按 shot 判断实际出现的主体、场景和关键道具。
3. 为人物选择稳定名称，不按表情、动作、姿态、角度或常规情绪拆分人物资产。
4. 为场景选择稳定名称，不因普通光影、时间、天气变化新建场景资产。
5. 只保留核心剧情道具；普通背景小物件不进资产清单。
6. 判断 `generation_required` 和 `handling_policy`。
7. 为需要生成提示词的资产写入 `prompt_outputs`。
8. 写入 `asset_manifest.json`。
9. 为每个 shot 写入 `shot_asset_map.json`。
10. 校验所有映射资产都存在于资产清单。

## Quality Gate

- [ ] 人物命名唯一、稳定、全程一致。
- [ ] 未使用 `CHAR_001`、`ENV_001`、`PROP_001` 或抽象 Asset ID 作为主名称。
- [ ] 同一人物跨多张参考图仍是同一个 `asset_name`。
- [ ] 常规表情、动作、姿态没有拆成多个人物资产。
- [ ] 场景没有因为普通光线、时间、天气变化被拆分。
- [ ] 只有空间结构或地点变化才新建场景资产。
- [ ] 道具只保留核心剧情道具。
- [ ] 普通背景道具没有强行生成独立资产图。
- [ ] 每个需要生成提示词的资产都有 `prompt_outputs`。
- [ ] 没有输出 `asset_prompt_tasks.json`、`task_id` 或大段 `asset_payload`。
- [ ] 每个 shot 都存在映射记录。
- [ ] `shot_asset_map.json` 中的所有资产都存在于 `asset_manifest.json`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `asset_executor`
- `completed_phases`: 追加 `asset_executor`
- `artifacts.asset_manifest`: `./outputs/asset_manifest.json`
- `artifacts.shot_asset_map`: `./outputs/shot_asset_map.json`
- `next_phase.skill`: `asset_prompt_generation`

## Failure Handling

- 分镜动作太抽象导致无法判断出现主体：返回 `storyboard_director` 修正 `action_desc`。
- 人物因表情/动作被拆成多个资产：合并为同一个人物资产，并用文字动作控制状态。
- 场景因光线/时间变化被拆成多个资产：合并为同一个场景资产，光影交给提示词控制。
- 普通道具被强行独立生成：改为 `text_prompt_control` 或从资产清单移除。
- 某 shot 缺少映射：补写该 shot 的主体、场景、关键道具关系。
