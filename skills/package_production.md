---
name: package-production
description: Build and validate the final short-video production handoff after all reviews pass. Use to create per-video folders with prompt.txt, manifest and references. Do not generate creative content or approve failed quality gates.
---

# Package Production

1. Require approved assets, storyboard sequence review, storyboard visual review, video segment plan and video prompts.
2. Run `scripts/package_production.py RUN_DIR`.
3. Run `scripts/validate_project.py RUN_DIR --phase all`.
4. Return the final manifest path and any blockers. Never mark completed when a required file is missing.
