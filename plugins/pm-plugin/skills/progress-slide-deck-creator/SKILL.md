---
name: progress-slide-deck-creator
description: Create a new dated progress slide deck from progress_update.md, project_plan.md, gantt_tasks.csv, project_schedule.xlsx, and a company progress deck template. Use for progress reporting snapshots only. This skill must not modify the original introduction deck, previous progress decks, the template deck, or baseline planning files; it creates a new dated PPTX and outline for the current progress update.
argument-hint: [progress_update.md path] [template.pptx path]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Progress Slide Deck Creator

Create a new dated progress report deck. Do not modify baseline decks or templates.

## Inputs

Default inputs:

- `project/progress_update.md`
- `project/project_plan.md`
- `project/gantt_tasks.csv`
- `project/project_schedule.xlsx`
- `tools/templates/slide_template_update.pptx` (progress deck template)
- `company_style/*.pdf`

If the user gives paths, use those paths.

## Outputs

- `progress_reports/YYYY-MM-DD_progress_deck.pptx`
- `progress_reports/YYYY-MM-DD_progress_deck_outline.md`
- Optional generated script in `scripts_generated/`

## Hard boundary

Do not overwrite or edit:

- Original introduction deck
- Previous progress decks
- Template deck
- `project_plan.md`
- `project_schedule.xlsx`
- `gantt_tasks.csv`

This skill creates a new dated progress deck only.

## Workflow

1. Read `progress_update.md` and determine the update date.
2. Read the project plan and schedule files only for context.
3. Read `company_style/*.pdf` for company name, terminology, tone, style, colors, or presentation conventions when available.
4. Locate the progress deck template. Prefer `company_style/progress_deck_template.pptx`.
5. Create an outline first at `progress_reports/YYYY-MM-DD_progress_deck_outline.md`.
6. Generate a project-local script in `scripts_generated/` to create the PPTX from the template. Do not bundle a fixed deck-generation script because templates vary by project.
7. Save the new deck under `progress_reports/` with the update date in the filename.
8. Verify that the template and previous decks were not overwritten.

## Deck content

Default slide sequence:

1. Title slide: project name, progress update date, reporting period
2. Executive progress summary
3. Completed since last update
4. Current work in progress
5. Blocked / delayed items
6. Schedule view or timeline status
7. Risks, issues, and decisions
8. Next actions and owner asks
9. Appendix / source notes, if useful

Use fewer slides if the update is small. Use more slides only when the progress update is large and needs clear separation.

## Style rules

- Use the provided template as the visual base.
- Preserve template layouts, logos, fonts, and colors where possible.
- Use company style PDFs as reference for company name, tone, and terminology.
- Keep slides concise and presentation-ready.
- Do not invent progress, dates, owners, or task completion.
- Mark unclear details as `TBD` or `Not confirmed`.
- Highlight `Potential change-control item` separately; do not treat it as accepted plan change.

## File naming

Use:

- `progress_reports/YYYY-MM-DD_progress_deck.pptx`
- `progress_reports/YYYY-MM-DD_progress_deck_outline.md`

If a file already exists, append a counter suffix:

- `YYYY-MM-DD_progress_deck_2.pptx`
- `YYYY-MM-DD_progress_deck_outline_2.md`

## Script generation requirements

When creating the project-local Python script:

- Prefer `python-pptx` for `.pptx` work in Claude Code.
- Open the template presentation.
- Add or update only slides in the new output presentation object.
- Save to a new dated output path.
- Never save back to the template path.
- Preserve the original template file.

## Verification

Before finishing:

- Confirm the output PPTX exists.
- Confirm the template file still exists and was not modified.
- Confirm the deck filename includes the update date.
- Confirm the outline matches the deck topics.
