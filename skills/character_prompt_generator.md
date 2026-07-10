# Skill: character_prompt_generator
**Version**: 3.0.0

## Source Prompt
`skills/raw_prompts/character_prompt_generator.source.md`

## Purpose
Generate one four-panel identity reference prompt for one fixed character or persistent character variant.

The generator does not create new assets, rename assets, or expand one character into default reference variants.

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_type": "character",
  "asset_name": "林小满_雨夜居家装",
  "output_prompt_path": "./outputs/assets/characters/prompts/林小满_雨夜居家装.md"
}
```

## Rules

- `asset_name` is fixed by `asset_executor`.
- A base asset may use the stable character name alone. A persistent variant uses `人物名_变体名`.
- Reject names containing the suffix `状态` and return to `asset_executor`.
- Produce one 2x2 identity board: face close-up, full-body front, full-body three-quarter, full-body back.
- Keep the same identity, age, hair, body, costume, proportions and neutral low-intensity expression in all panels.
- Do not use an overhead view as a standard character identity panel.
- Use `story.md` for narrative context.
- Use `style_bible.md` for visual direction.
- Write exactly one prompt file to `output_prompt_path`.
- Do not use `task_id`.
- Do not use `asset_payload`.
- Do not use a `prompt_outputs` array as generator input.

## Output
```json
{
  "character_prompt_path": "./outputs/assets/characters/prompts/林小满_雨夜居家装.md"
}
```

## Quality Gate

- [ ] One asset name.
- [ ] One output path.
- [ ] One prompt file.
- [ ] Four required panels and no duplicate angle.
- [ ] Identity and persistent variant are identical across panels.
- [ ] No `task_id`.
- [ ] No `asset_payload`.
