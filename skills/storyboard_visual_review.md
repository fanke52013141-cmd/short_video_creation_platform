---
name: storyboard-visual-review
description: Review all generated storyboard images as an ordered visual sequence for face, costume, placement, eyeline, screen direction, scene, prop, lighting, action and causal continuity. Use after storyboard image generation and before video prompt generation. Do not review isolated asset sheets.
---

# Storyboard Visual Review

## Goal

Find image-level continuity failures that text-only storyboard review cannot observe.

Read `references/expert_methodologies.md` section `Continuity` before reviewing.

## Inputs

Read `storyboard.json`, `shot_asset_map.json`, `asset_manifest.json`, approved canonical asset images and every storyboard image in order.

## Procedure

1. Compare each image with its declared assets.
2. Compare adjacent images for identity, costume, position, facing, eyeline, screen direction, prop state and fixed scene anchors.
3. Compare three-image windows for action progression and causal clarity.
4. Distinguish an intentional camera/view change from an accidental continuity change.
5. Report the smallest rerun boundary: asset prompt/image or storyboard prompt/image.
6. Output JSON conforming to `schemas/storyboard_visual_review.schema.json` plus a concise Markdown report.

## Quality gate

- Inspect all ordered images, not thumbnails in isolation.
- Give visual evidence and affected shot IDs for every issue.
- Mark identity, structural space or impossible action discontinuity as P0.
- Pass only with no unresolved P0.
