---
name: storyboard-sequence-review
description: Review a complete storyboard sequence before asset production for real shot boundaries, duration, causality, character, prop, space, eyeline and screen-direction continuity. Use after storyboard creation or revision. Do not generate storyboard images or rewrite the story.
---

# Storyboard Sequence Review

## Goal

Block continuity and production risks before asset generation while preserving the director's intent.

Read `references/methodology.md` section `Continuity` before reviewing.

## Inputs

```json
{
  "story_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "storyboard_path": "./outputs/storyboard.json",
  "output_json_path": "./outputs/reviews/storyboard_sequence_review.json",
  "output_markdown_path": "./outputs/reviews/storyboard_sequence_review.md"
}
```

## Procedure

1. Check every shot alone for duration, visible action, narrative purpose and a legitimate shot boundary.
2. Check every adjacent two-shot window for action phase, placement, eyeline, screen direction, props and cause before effect.
3. Check every three-shot window for local logic, reaction timing and spatial understanding.
4. Check the full sequence for story days, persistent character variants, scene structure, motif and emotional progression.
5. Classify only production-relevant findings as P0, P1 or P2. Do not rewrite shots without a finding.
6. Output the Markdown report and JSON conforming to `schemas/storyboard_sequence_review.schema.json`.

## Severity

- P0: cannot cut or generate coherently; block downstream work.
- P1: material risk; revise automatically when the fix preserves intent, otherwise flag.
- P2: safe production note.

## Quality gate

- Cover every shot exactly once in the one-shot pass.
- Cover all adjacent pairs and all available three-shot windows.
- Give shot IDs, evidence and the smallest actionable fix for every issue.
- Return `pass` only when no unresolved P0 remains.
