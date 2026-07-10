---
name: select-vertical
description: Select and resolve a short-video vertical package before production. Use when starting a run, switching between narrative, advertising, education, ecommerce, or another vertical, or explaining which strategy Skills the shared pipeline will invoke. Do not generate story, images, or storyboard content itself.
---

# Select a vertical package

## Inputs

- User goal and intended video category.
- `config/pipeline.yaml`.
- Candidate profiles in `config/verticals/`.
- Active run `checkpoint.json`.

## Procedure

1. Match the user's explicit vertical to a profile `id`. If no profile matches, stop and create or request a new profile instead of borrowing a misleading one.
2. Read `skill_overrides` from the selected profile.
3. Resolve each pipeline `strategy_slot`: use the override when present, otherwise use the slot's `default_skill`.
4. Verify that every resolved Skill exists or is an explicitly tracked migration target.
5. Write the selected id to `checkpoint.json` at `vertical.id` and store the resolved mapping at `vertical.resolved_skills`.
6. Do not change stable-core stages.

## Resolution example

For `advertising`, `content_strategy` resolves to `advertising-content-strategy`, while `asset_registry` remains `asset-executor` because it is a stable-core stage.

## Failure handling

- Missing profile: stop before content generation.
- Unknown strategy slot: fail validation; do not silently ignore it.
- Missing override Skill: mark the run blocked and identify the missing Skill.

## Verification

- Selected profile id is unique.
- Every strategy slot resolves to one Skill.
- Stable-core stage definitions are unchanged.
- Run `python scripts/validate_vertical_config.py`.

