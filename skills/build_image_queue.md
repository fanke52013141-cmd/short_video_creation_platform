---
name: build-image-queue
description: Build the deterministic image generation queue from approved asset manifest rows after all required prompt files exist. Do not create prompts or decide which assets are needed.
---

# Build Image Queue

Run `python scripts/build_image_queue.py RUN_DIR`. Stop on missing prompt paths. Do not manually edit task identifiers or output paths.
