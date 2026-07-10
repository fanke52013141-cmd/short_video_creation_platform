# Storyboard Prompts

## S001

## 分镜角色
frame_role: first_frame

## 上一分镜站位参考
uses_previous_storyboard_reference: false
source_shot_id: none
source_path: none
reference_purpose: none
reason: 第一条分镜，建立雨夜客厅场景和林小满的初始站位。

## 资产声明区
@林小满_雨夜居家装（人物资产）
@雨夜客厅场景（场景资产）
手机（关键道具，正文控制）

## 中文分镜图提示词
中景，林小满坐在沙发边缘，手机贴近耳边，右手摩挲毛毯边缘，视线落向茶几。窗外冷蓝雨光与室内暖黄台灯形成对比。画面无字幕、无 Logo、无水印。

## S002

## 分镜角色
frame_role: last_frame

## 上一分镜站位参考
uses_previous_storyboard_reference: true
source_shot_id: S001
source_path: ./outputs/storyboards/S001.png
reference_purpose: placement_anchor
reason: 同一 scene_id，人物、手机和沙发位置延续；当前分镜是同一情绪动作的近景落点。

## 资产声明区
@林小满_雨夜居家装（人物资产）
@雨夜客厅场景（场景资产）
手机（关键道具，正文控制）

## 中文分镜图提示词
参考上一分镜 S001 的站位关系，只继承人物相对位置、朝向、空间比例和场景连续性；当前画面动作、表情和景别以 S002 为准。近景，林小满轻轻吸气，嘴唇微张又抿紧，眼眶泛红但没有眼泪，手指捏紧手机边缘。画面无字幕、无 Logo、无水印。
