# Generated Media Review Protocol

该协议用于审查外部平台或内部工具生成的图片、视频结果。它发生在 `external_generation_handoff` 之后、`continuity_review` 之前。

## 输入

- `outputs/06_external_results/image_result_manifest.json`
- `outputs/06_external_results/shot_result_manifest.json`
- `outputs/06_external_results/external_generation_notes.md`（可选）
- 用户提供的截图、视频路径或人工备注

## 必查维度

### 角色

- 是否变脸、年龄漂移、服装漂移。
- 人物身份四宫格中的关键轮廓是否保持。
- 角色状态变体是否用错。

### 场景

- 空间方向是否反了。
- 固定物件是否消失或换位置。
- 光线、材质、时代感是否偏离风格圣经。

### 道具

- 母题道具是否存在。
- 道具状态是否和前后镜头一致。
- 文字类道具是否需要后期修正。

### 镜头与动作

- 运镜是否符合提示词。
- 动作是否完成。
- 情绪节奏是否可剪辑。

### 声音

- 有声镜头是否使用正确音色。
- 台词、旁白、录音留言或广播是否与分镜意图一致。

## 严重级别

- `P0`：最佳 take 不可用，必须重生成或回上游修正。
- `P1`：影响叙事清晰度或连续性，建议修正；若继续必须用户接受。
- `P2`：生产注意事项，可进入剪辑但需记录。

## 输出

- `outputs/06_external_results/generated_media_review.md`
- `outputs/06_external_results/generated_media_review.json`

`generated_media_review.json` 必须满足 `schemas/generated_media_review.schema.json`。
