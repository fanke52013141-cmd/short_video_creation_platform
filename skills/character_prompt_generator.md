# Skill: character_prompt_generator
**Version**: 2.4.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
Generate one image prompt for one fixed character-state asset.

The generator does not create new assets, rename assets, or expand one character into default reference variants.

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_type": "character",
  "asset_name": "林小满_雨夜接电话状态",
  "output_prompt_path": "./outputs/assets/characters/林小满_雨夜接电话状态.md"
}
```

## Rules

- `asset_name` is fixed by `asset_executor`.
- `asset_name` should include the stable character name plus the state.
- Use `story.md` for narrative context.
- Use `style_bible.md` for visual direction.
- Write exactly one prompt file to `output_prompt_path`.
- Do not use `task_id`.
- Do not use `asset_payload`.
- Do not use a `prompt_outputs` array as generator input.

## Output
```json
{
  "character_prompt_path": "./outputs/assets/characters/林小满_雨夜接电话状态.md"
}
```

## Quality Gate

- [ ] One asset name.
- [ ] One output path.
- [ ] One prompt file.
- [ ] No `task_id`.
- [ ] No `asset_payload`.
