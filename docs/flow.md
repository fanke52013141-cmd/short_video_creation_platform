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
- Source prompt: `skills/raw_prompts/story_generation.source.md`
- Input: `RUN/inputs/idea_brief.md`
- Output:
  - `RUN/outputs/story.md`
- Contract:
  - 只优化剧本。
  - 不输出 `story.json`。
  - 不拆镜头。
  - 不拆角色、场景、道具或资产。
  - 不写图片提示词或视频提示词。
- Boundary: 镜头结构化由 `storyboard_director` 处理；人物、场景、道具和资产拆分由 `asset_executor` 处理。

## 2. Story To User-Confirmed Style Bible

- Skill: `art_direction`
- Source prompt: `skills/raw_prompts/art_direction.source.md`
- Input:
  - 用户已确认锁定的 `RUN/outputs/story.md`
  - 可选：用户参考图、艺术风格、视觉偏好或禁用方向
- Output:
  - `RUN/outputs/style_bible.md`
- Contract:
  - 不输出 `art_direction.json`。
  - 如果用户已有艺术风格或参考图，优先继承并补全执行规则。
  - 如果用户没有明确视觉方向，先提出 2-3 个候选方案，让用户选择，不直接定稿。
  - 最终 `style_bible.md` 只定义画面风格、整体色调、光线风格和 AI 视觉执行要求。
  - 具体构图、景别、机位和镜头调度由 `storyboard_director` 负责。
  - 不输出独立 `构图倾向` 字段，不输出独立 `禁止出现的视觉元素` 字段。

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
  - `shot_id`: 镜头编号，`S001`、`S002`...
  - `scene_id`: 场景 / 时空单元编号，`SC001`、`SC002`...，由导演创建，可被多个 shot 复用
  - `duration_seconds`: 建议时长，必须 `>0` 且 `<=15`
  - `framing`: 景别
  - `camera_move`: 运镜
  - `action_desc`: 具象动作描述
- Boundary:
  - 导演负责具体构图、景别、机位、镜头调度和分镜结构化。
  - 导演不得输出人物、场景、道具、资产拆分字段。
  - 导演不得输出 `characters_in_shot`、`location`、资产 ID、图片提示词、视频提示词、音色或外部交接内容。
- Quality Gate: 分镜阶段内部完成相邻逻辑检查；不再存在独立 `storyboard_sequence_review` 节点。

## 4. Storyboard To Seedance Asset Manifest And Shot Map

- Skill: `asset_executor`
- Input:
  - `RUN/outputs/story.md`
  - `RUN/outputs/storyboard.json`
  - 可选：用户参考图 / 视频 / 文字素材
- Output:
  - `RUN/outputs/asset_manifest.json`
  - `RUN/outputs/shot_asset_map.json`
- Schemas:
  - `schemas/asset_manifest.schema.json`
  - `schemas/shot_asset_map.schema.json`
- Responsibilities:
  1. 遍历故事和分镜，提取需要稳定控制的人物、场景和核心剧情道具。
  2. 为人物选择 `主体1/主体2` 或稳定具象名，例如 `林小满`、`警察`。
  3. 为同一人物绑定多张参考图，但不因表情、动作、姿态拆分新人物资产。
  4. 为场景选择 `场景1/场景2` 或具象场景名，例如 `雨夜客厅场景`。
  5. 不因普通光线、时间、天气变化拆分新场景资产。
  6. 道具只保留核心剧情道具；普通道具默认沿用参考素材或正文控制。
  7. 建立每个 shot 对应哪些稳定资产名的映射关系。

## 5. Asset Prompt Generation

三路可并行执行，互不依赖。

### 5-A Character Prompts

- Skill: `character_prompt_generator`
- Input:
  - `RUN/outputs/story.md`
  - `RUN/outputs/style_bible.md`
  - 从 `asset_manifest.json` 切出的单个人物主体
- Output:
  - 人脸大头特写提示词
  - 全身妆造提示词
- Boundary: 不为表情、动作、姿态拆新人物资产。

### 5-B Scene Prompts

- Skill: `scene_prompt_generator`
- Input:
  - `RUN/outputs/story.md`
  - `RUN/outputs/style_bible.md`
  - 从 `asset_manifest.json` 切出的单个场景
- Output:
  - `RUN/outputs/assets/scenes/{场景资产名}.md`
- Boundary: 不为普通光影、时段、天气变化拆新场景资产。

### 5-C Prop Prompts

- Skill: `prop_prompt_generator`
- Input:
  - `RUN/outputs/story.md`
  - 从 `asset_manifest.json` 切出的单个道具
- Output:
  - 只有 `generation_required=true` 且 `handling_policy=generate_independent_prop` 时，输出 `RUN/outputs/assets/props/{道具资产名}.md`
- Boundary: 普通道具不强行生成独立图片，后续写入视频提示词正文。

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
  - 人物的人脸大头特写和全身妆造是两个独立任务，不合成一张图。
  - 场景参考图是单张空间参考图。
  - 道具只有 `generation_required=true` 且 `handling_policy=generate_independent_prop` 时才生成独立图。

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

用户随后生成分镜参考图，并回填到 `RUN/outputs/storyboards/S001.png`、`S002.png` 等。

## 7. Video Prompt Generation

- Skill: `video_prompt_generator`
- Input:
  - `RUN/outputs/storyboard.json`
  - `RUN/outputs/storyboards/`
  - `RUN/outputs/shot_asset_map.json`
  - `RUN/outputs/assets/`
  - 可选 `reference_media`：用户额外提供的图片、音频、视频素材及其角色
- Output:
  - `RUN/outputs/video_prompts.md`
  - `RUN/outputs/video_prompts.json`
- Supported task types:
  - `pipeline_shot_generation`: 默认分镜流水线生成。
  - `multimodal_reference`: 多图片 / 音频 / 视频参考生成新视频。
  - `video_edit`: 严格编辑已有视频对象。
  - `video_extend`: 向前或向后延长已有视频对象。
  - `combined_task`: 参考一个素材，同时编辑或延长另一个素材。
  - `track_stitch`: 多段视频轨道衔接。
- Merge rule:
  - 合并对象是连续 `S###`，不是 `SC###`。
  - `scene_id` 只是合并边界。
  - 强连续动作在同场景且总时长 `<=15s` 时优先合并。
  - 景别变化不是禁止合并的理由。
  - 跨场景、超 15 秒或动作不连续时必须拆分。
  - 每条 `V###` 必须在 `video_prompts.json` 中写入 `merge_decision`。
- Anchor rule:
  - 同一场景内连续多镜头，每个视频提示词必须引入 `参考@上一分镜_站位，保持人物空间关系、朝向和相对位置不变`。
  - 场景切换时不引入上一分镜，避免错误约束。
- Asset declaration rule:
  - 每条 `V###` 必须包含 `【自检通过项】`、`【资产声明区】`、`【中文视频提示词】`。
  - 所有素材先声明再引用。
- Operation object rule:
  - 编辑对象正文必须写 `严格编辑 @资产名`，禁止写 `参考@资产名`。
  - 延长对象正文必须写 `向前延长 @资产名` 或 `向后延长 @资产名`，禁止写 `参考@资产名`。
- Prop rule: 道具资产不使用 `@PROP`，只写入视频提示词正文描述。
- Risk rule: 若包含奔跑、跳跃、翻滚、剧烈打斗、快速追逐等高强度动作，必须在 `V###` 最前面输出 `【生成风险提示】`。

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
