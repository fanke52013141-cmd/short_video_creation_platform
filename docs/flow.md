# Workflow

路径约定：仓库根目录保存流程资产；真实创作在 `local_runs/YYYY-MM-DD/project_slug/` 中执行。下文的 `RUN` 代表这个 active run 目录。

执行边界：本仓库负责剧本、风格圣经、导演分镜、资产清单、资产提示词、分镜生图提示词和最终视频提示词。图片与视频生成可在即梦网页端、ChatGPT 网页端、Codex 或其他外部图像工具中执行；流程终点是进入即梦画布生产。

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
- Input: `RUN/inputs/idea_brief.md`
- Output: `RUN/outputs/story.md`
- Contract: 只优化剧本；不输出 `story.json`；不拆镜头、资产或提示词。

## 2. Story To User-Confirmed Style Bible

- Skill: `art_direction`
- Input:
  - 用户已确认锁定的 `RUN/outputs/story.md`
  - 可选：用户参考图、艺术风格、视觉偏好或禁用方向
- Output: `RUN/outputs/style_bible.md`
- Contract:
  - 用户已有风格时继承并补全。
  - 用户没有明确视觉方向时，先给 2-3 个候选方案。
  - 最终只定义画面风格、整体色调、光线风格和 AI 视觉执行要求。
  - 不做具体构图、景别、机位或分镜。

## 3. Story And Style To Storyboard

- Skill: `storyboard_director`
- Input:
  - `RUN/outputs/story.md`
  - `RUN/outputs/style_bible.md`
- Output: `RUN/outputs/storyboard.json`
- Shot fields:
  - `shot_id`
  - `scene_id`
  - `duration_seconds`
  - `framing`
  - `camera_move`
  - `action_desc`
- Boundary: 导演负责具体构图、景别、机位、镜头调度和分镜结构化；不得输出人物、场景、道具、资产拆分字段或提示词。

## 4. Storyboard To Seedance Asset Manifest And Shot Map

- Skill: `asset_executor`
- Input:
  - `RUN/outputs/story.md`
  - `RUN/outputs/storyboard.json`
  - 可选：用户参考图 / 视频 / 文字素材
- Output:
  - `RUN/outputs/asset_manifest.json`
  - `RUN/outputs/shot_asset_map.json`
- Responsibilities:
  1. 遍历故事和分镜，固定需要稳定控制的人物、场景和核心剧情道具。
  2. 为人物选择 `主体1/主体2` 或稳定具象名，例如 `林小满`、`警察`。
  3. 为场景选择 `场景1/场景2` 或具象场景名，例如 `雨夜客厅场景`。
  4. 不因表情、动作、姿态拆人物资产。
  5. 不因普通光线、时间、天气变化拆场景资产。
  6. 普通道具默认沿用参考素材或正文控制。
  7. 建立每个 shot 对应哪些稳定资产名的映射关系。
  8. 在 `asset_manifest.json` 里为需要生成提示词的资产写入 `prompt_outputs`。

## 5. Asset Prompt Generation

三路可并行执行，互不依赖。三类生成器都使用同一种极简输入：

```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_type": "character | scene | prop",
  "asset_name": "资产执行官固定的资产名",
  "output_prompt_path": "本次要写出的提示词文件"
}
```

不需要：

- `task_id`
- `asset_payload`
- `asset_prompt_tasks.json`
- 额外任务队列

剧本是必要输入，因为人物设定、场景气质和道具意义都需要完整剧情上下文。资产执行官只固定资产，不把剧情压缩成复杂 payload。

### 5-A Character Prompts

- Skill: `character_prompt_generator`
- Input example:
  ```json
  {
    "story_markdown_path": "./outputs/story.md",
    "style_bible_path": "./outputs/style_bible.md",
    "asset_type": "character",
    "asset_name": "林小满",
    "output_prompt_path": "./outputs/assets/characters/林小满_人脸大头特写.md"
  }
  ```
- Output: `output_prompt_path` 指向的一份单图提示词 Markdown。
- Boundary: 不为表情、动作、姿态拆新人物资产。

### 5-B Scene Prompts

- Skill: `scene_prompt_generator`
- Input example:
  ```json
  {
    "story_markdown_path": "./outputs/story.md",
    "style_bible_path": "./outputs/style_bible.md",
    "asset_type": "scene",
    "asset_name": "雨夜客厅场景",
    "output_prompt_path": "./outputs/assets/scenes/雨夜客厅场景.md"
  }
  ```
- Output: `output_prompt_path` 指向的一份单场景参考图提示词 Markdown。
- Boundary: 不为普通光影、时段、天气变化拆新场景资产。

### 5-C Prop Prompts

- Skill: `prop_prompt_generator`
- Input example:
  ```json
  {
    "story_markdown_path": "./outputs/story.md",
    "style_bible_path": "./outputs/style_bible.md",
    "asset_type": "prop",
    "asset_name": "旧皮箱",
    "output_prompt_path": "./outputs/assets/props/旧皮箱.md"
  }
  ```
- Output: `output_prompt_path` 指向的一份单物体参考图提示词 Markdown。
- Boundary: 只处理已被资产执行官判定为需要独立生成的核心道具。普通道具不进入此生成器。

## 5.5 Asset Image Generation

- Skill: `image_generation_executor`
- Input:
  - `RUN/outputs/asset_manifest.json`
  - `RUN/outputs/style_bible.md`
  - `RUN/outputs/assets/**/*.md` 中的单资产提示词
  - `generation_mode`: `jimeng_web_manual | chatgpt_web | codex_direct | external_manual`
- Output:
  - `RUN/outputs/image_generation_queue.json`
  - `RUN/outputs/image_generation_queue.md`
  - 生成后的单张资产图片，保存到 `RUN/outputs/assets/**`
- Contract:
  - 一个 `asset_image_task` 只生成一张图片。
  - 禁止拼接图、四宫格、对比图、角色设定表、scene sheet、contact sheet。
  - 人物的人脸大头特写和全身妆造是两个独立输出，不合成一张图。

## 6. Storyboard Image Prompt Generation

- Skill: `storyboard_prompt_generator`
- Input:
  - `RUN/outputs/storyboard.json`
  - `RUN/outputs/style_bible.md`
  - `RUN/outputs/shot_asset_map.json`
  - `RUN/outputs/assets/**` 中已有资产参考图
- Output: `RUN/outputs/storyboard_prompts.md`
- Responsibility: 把导演分镜的叙事语言转化为 AI 生图语言。

## 7. Video Prompt Generation

- Skill: `video_prompt_generator`
- Input:
  - `RUN/outputs/storyboard.json`
  - `RUN/outputs/storyboards/`
  - `RUN/outputs/shot_asset_map.json`
  - `RUN/outputs/assets/`
  - 可选 `reference_media`
- Output:
  - `RUN/outputs/video_prompts.md`
  - `RUN/outputs/video_prompts.json`
- Merge rule:
  - 合并对象是连续 `S###`，不是 `SC###`。
  - `scene_id` 只是合并边界。
  - 强连续动作在同场景且总时长 `<=15s` 时优先合并。
  - 景别变化不是禁止合并的理由。
  - 跨场景、超 15 秒或动作不连续时必须拆分。
  - 每条 `V###` 必须在 `video_prompts.json` 中写入 `merge_decision`。

## Final Canvas Handoff

只交付以下内容：

| 交付物 | 内容 | 说明 |
|---|---|---|
| `outputs/story.md` | 完整剧本 | 供画布理解叙事 |
| `outputs/video_prompts.md` | 完整视频提示词 | 逐条复制使用 |
| `outputs/video_prompts.json` | 结构化视频计划 | 用于校验和后续自动化 |
| `outputs/assets/characters/` | 全部有效角色资产 | 废弃/被替换的图片不包含 |
| `outputs/assets/scenes/` | 全部有效场景资产 | 废弃/被替换的图片不包含 |
| `outputs/storyboards/` | 全部分镜参考图 | 用于视频生成时的首帧/站位参考 |

道具资产不单独交付，写入视频提示词正文描述。
