# Create Plan

1. Analyze Requirements - Parse the `USER_PROMPT` to understand the core problem and desired outcome
2. Explore Codebase - Understand existing patterns, architecture, relevant files, and prior specs to back-reference. If the `AI_DOCS/` directory is present, read it for AI/agent-facing documentation; likewise `APP_DOCS/` for application documentation. Skip either when its directory does not exist.
3. Design Solution - Develop technical approach including architecture decisions and implementation strategy
4. Author HTML Plan - Read `TEMPLATE` in full and fill it in: every placeholder replaced, the blocks marked `repeat` duplicated as many times as the plan needs
5. Generate Images - Run the Create sub-workflow in `workflows/image-generation.md` to fill the `{{...IMAGE` slots. Parallelize the image generation as there's no reason to block here.
6. Surface Questionables - If `QUESTIONABLE` is true, populate the conditional Questionables section with open decisions/assumptions/risks; otherwise omit the section
7. Generate Filename - Create a descriptive kebab-case filename based on the plan's main topic
8. Save - Write the plan to `PLAN_FILE` and provide a summary of key components
9. Open in Browser - Open the saved plan in `BROWSER` (e.g. `open -a "Google Chrome" PLAN_FILE`)
