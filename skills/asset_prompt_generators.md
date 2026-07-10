---
name: asset-prompt-generators
description: Dispatch one approved asset manifest row at a time to the character, scene or prop prompt generator. Use after asset planning. Do not batch multiple assets into one model call or redefine assets.
---

# Asset Prompt Generators

1. Read `asset_manifest.json` and select the next `generation_required=true` row without a prompt file.
2. Pass only `story.md`, `style_bible.md`, `asset_type`, `asset_name` and `output_prompt_path`.
3. Dispatch to `character_prompt_generator`, `scene_prompt_generator` or `prop_prompt_generator`.
4. Validate that exactly one prompt file was created.
5. Repeat until the deterministic image queue reports no missing prompts.

Never pass the full task queue into a child generator.
