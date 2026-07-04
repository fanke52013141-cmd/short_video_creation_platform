# Skill: asset_executor
**Version**: 1.2.0

## Purpose
从 `story.md` 和 `storyboard.json` 中提取后续 Seedance 生产真正需要稳定控制的主体、场景和关键道具，并建立分镜到资产的映射。

本 Skill 是资产清单、分镜资产映射和资产提示词任务包的唯一来源。它不写最终图片提示词，不生成图片，不决定视频合并。

核心目标不是把所有画面元素拆成资产，而是建立 Seedance 友好的稳定命名、素材绑定关系，以及下游提示词生成器所需的最小任务输入。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "storyboard_json_path": "./outputs/storyboard.json",
  "reference_media": []
}
```

`story.md` 和 `storyboard.json` 只在本阶段使用。进入 `asset_prompt_generation` 后，不再把完整剧本或完整分镜继续下传。

## Outputs
```json
{
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "shot_asset_map_path": "./outputs/shot_asset_map.json",
  "asset_prompt_tasks_path": "./outputs/asset_prompt_tasks.json"
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
林小满 → 图片1 人脸大头特写 + 图片2 全身妆造图
```

不得因为表情、动作、姿态、坐下、抬手、哭泣、微笑等常规状态拆成多个角色资产。

推荐人物主资产结构：

```text
1 张人脸大头特写图：锁定面部 ID
1 张全身妆造图：锁定体型、服装、整体造型
```

如果发生完全换装或造型大幅变化，可以新增备用全身参考图，但仍然绑定同一个人物名，不新建人物资产。

### 3. 场景命名

允许两种命名方式。

#### A. 简易编号命名

```text
场景1、场景2
```

调用时绑定素材：

```text
场景1@图片2
```

#### B. 具象场景命名

```text
宿舍场景@图片2
悬崖竹林场景@图片3
雨夜客厅场景
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

这些由后续提示词文字控制。

只有以下情况才新建场景资产：

- 空间结构变化。
- 建筑布局变化。
- 地点发生实质切换。
- 从现实空间进入梦境、回忆、手机屏幕世界、监控视角等独立叙事空间。

如果光影风格跨度极大，可以准备同构图备用场景参考图，但仍绑定同一个场景名，不作为全新场景资产。

### 5. 道具处理原则

不需要把画面所有道具逐一生成或描述。只管控核心剧情道具。

道具分三类：

1. `inherited_from_reference`
   - 参考素材里已有的普通道具。
   - 默认保留，不单独生成，不额外描述。

2. `text_control_only`
   - 需要新增、出现、移动或被人物交互的关键道具。
   - 不一定生成独立道具图，可以在视频提示词正文中写明特征、出现时机和位置。

3. `generate_independent_prop`
   - 剧情关键、反复出现、需要特写、外形复杂或状态变化明显的道具。
   - 才生成独立道具资产。

多余道具需要移除时，使用 `remove_by_instruction`，只写明删除目标，不反向列出剩余所有道具。

## asset_manifest.json Contract

```json
{
  "naming_policy": "seedance_subject_scene_binding",
  "characters": [
    {
      "asset_name": "林小满",
      "asset_type": "character",
      "naming_strategy": "custom_concrete_name",
      "seedance_label": "林小满",
      "definition_sentence": "将图片1中黑色中长发、深色针织衫的年轻女性定义为林小满。",
      "reference_bindings": [],
      "visual_anchors": ["黑色中长发", "深色针织衫"],
      "generation_brief": "年轻女性林小满，黑色中长发，深色针织衫，气质克制安静。",
      "usage_context": "家庭情绪短片主角，后续常出现接电话、停顿、抿唇等克制动作。",
      "appears_in_shots": ["S001", "S002"],
      "generation_required": true,
      "required_reference_set": ["face_closeup", "full_body_styling"],
      "prompt_scope": "single_character_identity_bundle",
      "handling_policy": "generate_identity_bundle",
      "notes": "常规表情和动作不拆新人物资产"
    }
  ],
  "scenes": [],
  "props": []
}
```

`generation_brief` 和 `usage_context` 是给下游资产提示词任务使用的浓缩上下文。它们由本阶段从 `story.md` 与 `storyboard.json` 中提炼，避免下游继续读取完整剧本。

## asset_prompt_tasks.json Contract

`asset_prompt_tasks.json` 是 `asset_prompt_generation` 的最小输入来源。每个 task 只对应一个资产提示词输出。

```json
{
  "tasks": [
    {
      "task_id": "PROMPT_CHARACTER_林小满_FACE",
      "parent_asset_name": "林小满",
      "asset_type": "character",
      "prompt_role": "face_closeup",
      "style_bible_path": "./outputs/style_bible.md",
      "asset_payload": {
        "seedance_label": "林小满",
        "definition_sentence": "将生成的人脸大头特写图和全身妆造图统一定义为林小满。",
        "visual_anchors": ["黑色中长发", "深色针织衫"],
        "generation_brief": "年轻女性林小满，黑色中长发，深色针织衫，气质克制安静。",
        "usage_context": "家庭情绪短片主角。"
      },
      "reference_bindings": [],
      "output_prompt_path": "./outputs/assets/characters/林小满_人脸大头特写.md"
    }
  ]
}
```

### 最小输入原则

`asset_prompt_generation` 不应读取：

- 完整 `story.md`
- 完整 `storyboard.json`
- 完整 `shot_asset_map.json`
- 完整 `asset_manifest.json`

它只读取：

- 当前 `asset_prompt_task`
- `style_bible.md`
- 当前 task 里携带的 `asset_payload`
- 当前 task 里列出的 `reference_bindings`

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
3. 为人物选择命名策略：有明确人名/身份时用具象命名；没有时用 `主体1`、`主体2`。
4. 为同一人物合并所有参考素材绑定，不因表情、动作、姿态、角度或常规情绪拆分人物资产。
5. 为场景选择命名策略：简单项目可用 `场景1`；剧情项目优先用具象场景名。
6. 合并同一空间结构的光线、时间、天气变化，不因普通光影变化新建场景资产。
7. 只保留核心剧情道具；普通背景小物件不进资产清单。
8. 为每个资产提炼 `generation_brief` 和 `usage_context`，把下游需要的上下文浓缩到资产对象中。
9. 判断 `generation_required` 和 `handling_policy`：
   - 人物：已有足够参考素材时绑定现有素材；缺素材时生成身份资产组。
   - 场景：已有场景参考图时绑定；缺素材时生成场景参考图。
   - 道具：默认正文控制，只有关键复杂道具才独立生成。
10. 写入 `asset_manifest.json`。
11. 为每个 shot 写入 `shot_asset_map.json`。
12. 根据 `required_reference_set` 和 `handling_policy` 展开 `asset_prompt_tasks.json`。
13. 校验所有映射资产都存在于资产清单，且每个需要生成提示词的资产都有对应 task。

## Quality Gate

- [ ] 人物命名唯一、稳定、全程一致。
- [ ] 未使用 `CHAR_001`、`ENV_001`、`PROP_001` 或抽象 Asset ID 作为主名称。
- [ ] 同一人物跨多张参考图仍是同一个 `asset_name`。
- [ ] 常规表情、动作、姿态没有拆成多个人物资产。
- [ ] 人物资产优先按“人脸大头特写 + 全身妆造图”组织。
- [ ] 场景没有因为普通光线、时间、天气变化被拆分。
- [ ] 只有空间结构或地点变化才新建场景资产。
- [ ] 道具只保留核心剧情道具。
- [ ] 普通背景道具没有强行生成独立资产图。
- [ ] 每个资产都有足够下游使用的 `generation_brief` 或 `visual_anchors`。
- [ ] 每个 shot 都存在映射记录。
- [ ] `shot_asset_map.json` 中的所有资产都存在于 `asset_manifest.json`。
- [ ] `asset_prompt_tasks.json` 不要求下游读取完整 `story.md`、`storyboard.json` 或完整 `asset_manifest.json`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `asset_executor`
- `completed_phases`: 追加 `asset_executor`
- `artifacts.asset_manifest`: `./outputs/asset_manifest.json`
- `artifacts.shot_asset_map`: `./outputs/shot_asset_map.json`
- `artifacts.asset_prompt_tasks`: `./outputs/asset_prompt_tasks.json`
- `next_phase.skill`: `asset_prompt_generation`

## Failure Handling

- 分镜动作太抽象导致无法判断出现主体：返回 `storyboard_director` 修正 `action_desc`。
- 人物因表情/动作被拆成多个资产：合并为同一个人物资产，并用文字动作控制状态。
- 场景因光线/时间变化被拆成多个资产：合并为同一个场景资产，光影交给提示词控制。
- 普通道具被强行独立生成：改为 `text_control_only` 或从资产清单移除。
- 某 shot 缺少映射：补写该 shot 的主体、场景、关键道具关系。
- 某资产缺少下游提示词生成所需上下文：补充 `generation_brief`、`usage_context` 或 `visual_anchors`。
