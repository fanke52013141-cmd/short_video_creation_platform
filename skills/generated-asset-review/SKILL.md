---
name: generated-asset-review
description: Review generated or imported character, scene and prop reference images against the approved asset manifest and style bible. Use before storyboard image prompting. Do not redesign approved assets or review storyboard sequences.
---

# Generated Asset Review

## Goal

Approve only reference images that reliably lock identity, space or prop form for downstream generation.

## Minimum inputs

Read one asset per call: its manifest row, canonical image, prompt and `style_bible.md`.

## Review rules

- Character quad: same person, age, hair, body and costume across face close-up, full front, three-quarter and back views; neutral readable pose; no duplicated panels.
- Scene quad: establishing wide, eye-level primary direction, reverse/side direction and top-down spatial layout; doors, windows, fixed furniture and paths must agree.
- Prop quad: primary three-quarter, side/back, critical detail and scale/interaction view; state must match the variant name.
- Reject text, logos, watermarks, unintended extra subjects and conflicts with the style bible.
- Return the smallest regeneration instruction and never alter `asset_name` during review.

## Output

Return `pass | revise_required`, P0/P1/P2 findings, evidence, regeneration instruction and `rerun_from=asset_image_generation` when needed.
