# Workflow

路径约定：仓库根目录保存流程资产；真实创作在 `local_runs/YYYY-MM-DD/project_slug/` 中执行。下文的 `RUN` 代表这个 active run 目录。

执行边界：本仓库负责剧本、风格圣经、分镜、资产清单、资产提示词、分镜生图提示词和最终视频提示词。图片与视频生成在即梦网页端人工执行；流程终点是进入即梦画布生产。

## 0. Initialize Local Run

- Script: `scripts/init_local_run.ps1`
- Output:
  - `RUN/checkpoint.json`
  - `RUN/inputs/idea_brief.md`
  - `RUN/outputs/assets/characters/`
  - `RUN/outputs/assets/scenes/`
  - `RUN/outputs/assets/props/`
  - `RUN/outputs/storyboards/`

## 1. Idea To Story

- Skill: `story_generation`
- Source prompt: `skills/raw_prompts/story_generation.source.md`
- Input: `RUN/inputs/idea_brief.md`
- Output:
  - `RUN/outputs/story.md`
  - `RUN/outputs/story.json`
- Schema: `schemas/story.schema.json`
- Contract: `story.json` 只保留下游必要字段：场景列表、角色列表、剧情段落和生产备注。

## 2. Story To One-Page Style Bible

- Skill: `art_direction`
- Source prompt: `skills/raw_prompts/art_direction.source.md`
- Input:
  - `RUN/outputs/story.md`
- Output:
  - `RUN/outputs/style_bible.md`
- Contract: 不输出 `art_direction.json`。`style_bible.md` 必须一页以内，只允许定义整体色调、光线风格、构图倾向和禁止出现的视觉元素。

## 3. Story And Style To Storyboard

- Skill: `storyboard_director`
- Source prompt: `skills/raw_prompts/storyboard_director.source.md`
- Input:
  - `RUN/outputs/story.md`
  - `RUN/outputs/style_bible.md`
- Output:
  - `RUN/outputs/storyboard.json`
- Schema: `schemas/storyboard.schema.json`
- Shot fields:
  - `shot_id`: `S001`、`S002`...
  - `scene_id`: 关联场景
  - `duration_seconds`: 建议时长，必须 `>0` 且 `<=15`
  - `framing`: 景别
  - `camera_move`: 运镜
  - `action_desc`: 具象动作描述
  - `characters_in_shot`: 出现角色名，使用特征名，不使用 `CharA`
  - `location`: 场景名
- Boundary: 导演不得输出资产草表、资产 ID、提示词、音色或外部交接内容。
- Quality Gate: 分镜阶段内部完成相邻逻辑检查；不再存在独立 `storyboard_sequence_review` 节点。

## 4. Storyboard To Asset Manifest And Shot Map

- Skill: `asset_executor`
- Input:
  - `RUN/outputs/story.md`
  - `RUN/outputs/storyboard.json`
- Output:
  - `RUN/outputs/asset_manifest.json`
  - `RUN/outputs/shot_asset_map.json`
- Schemas:
  - `schemas/asset_manifest.schema.json`
  - `schemas/shot_asset_map.schema.json`
- Responsibilities:
  1. 遍历故事和分镜，提取所有需要生产的角色、场景、道具资产。
  2. 为每个资产定义“特征 + 状态”命名。
  3. 建立每个 shot 对应哪些资产的映射关系。

## 5. Asset Prompt Generation

三路可并行执行，互不依赖。

### 5-A Character Prompts

- Skill: `character_prompt_generator`
- Input:
  - `RUN/outputs/story.md`
  - 从 `asset_manifest.json` 切出的单个角色及其全部状态
- Output:
  - `RUN/outputs/assets/characters/{角色资产名}.md`

### 5-B Scene Prompts

- Skill: `scene_prompt_generator`
- Input:
  - `RUN/outputs/story.md`
  - 从 `asset_manifest.json` 切出的单个场景
- Output:
  - `RUN/outputs/assets/scenes/{场景资产名}.md`

### 5-C Prop Prompts

- Skill: `prop_prompt_generator`
- Input:
  - `RUN/outputs/story.md`
  - 从 `asset_manifest.json` 切出的单个道具
- Output:
  - `RUN/outputs/assets/props/{道具资产名}.md`

用户随后在即梦生成资产图片，并回填到对应资产目录。

## 6. Storyboard Image Prompt Generation

- Skill: `storyboard_prompt_generator`
- Input:
  - `RUN/outputs/storyboard.json`
  - `RUN/outputs/style_bible.md`
  - `RUN/outputs/shot_asset_map.json`
  - `RUN/outputs/assets/**` 中已有资产参考图
- Output:
  - `RUN/outputs/storyboard_prompts.md`
- Responsibility: 把导演分镜的叙事语言转化为 AI 生图语言。导演分镜不是生图提示词，不得直接复制为图片提示词。

用户随后在即梦生成分镜参考图，并回填到 `RUN/outputs/storyboards/S001.png`、`S002.png` 等。

## 7. Video Prompt Generation

- Skill: `video_prompt_generator`
- Input:
  - `RUN/outputs/storyboard.json`
  - `RUN/outputs/storyboards/`
  - `RUN/outputs/shot_asset_map.json`
  - `RUN/outputs/assets/`
- Output:
  - `RUN/outputs/video_prompts.md`
- Merge rule: 相邻 shot 只有同时满足以下三项才允许合并为一个 `V###`：
  1. 同一 `scene_id`。
  2. 合并后时长之和 `<=15s`。
  3. 动作描述连续，无场景切换、无时间跳跃。
- Anchor rule:
  - 同一场景内连续多镜头，每个视频提示词必须引入 `参考@上一分镜_站位，保持人物空间关系、朝向和相对位置不变`。
  - 场景切换时不引入上一分镜，避免错误约束。
- Prop rule: 道具资产不使用 `@PROP`，只写入视频提示词正文描述。

## Final Jimeng Canvas Handoff

只交付以下内容：

| 交付物 | 内容 | 说明 |
|---|---|---|
| `outputs/story.md` | 完整剧本 | 供导演在即梦画布理解叙事 |
| `outputs/video_prompts.md` | 完整视频提示词 | 逐条复制到即梦使用 |
| `outputs/assets/characters/` | 全部有效角色资产 | 废弃/被替换的图片不包含 |
| `outputs/assets/scenes/` | 全部有效场景资产 | 废弃/被替换的图片不包含 |
| `outputs/storyboards/` | 全部分镜参考图 | 用于视频生成时的首帧/站位参考 |

道具资产不单独交付，写入视频提示词正文描述。
