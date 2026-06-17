# Artifact Snapshot Contract

This skill belongs to Lane A after a timestamped replan has already been created.

It uses the new timestamped project plan and manifest to generate new static planning artifacts. It never overwrites current active artifacts.

## Required inputs

- `<timestamp>_project_plan.md`
- `<timestamp>_plan_change_manifest.json`

Optional supporting inputs:

- `<timestamp>_plan_change_impact.md`
- Current `gantt_tasks.csv`
- Current `project_schedule.xlsx`
- Current or template slide deck
- Company style reference PDFs in `company_style/`
- PowerPoint template in `company_style/` or `Templates/`

## Required outputs

Use the same timestamp as the input replan snapshot.

- `<timestamp>_gantt_tasks.csv`
- `<timestamp>_gantt_chart.md`
- `<timestamp>_project_schedule.xlsx`
- `<timestamp>_project_replan_deck.pptx`
- `<timestamp>_artifact_snapshot_report.md`

Store outputs in `replans/` and/or `replans/<timestamp>/` depending on repo convention.

## Non-destructive rules

- Do not modify `project_plan.md`.
- Do not modify the baseline workbook.
- Do not modify old Gantt CSV files.
- Do not modify the original intro deck.
- Do not modify old progress decks.
- Do not overwrite templates.
- Always write new timestamped files.

## Script generation guidance

Do not assume workbook or deck structure. Inspect the actual files first. Generate project-local helper scripts only when needed and store them under `scripts_generated/`. The scripts should write timestamped output files, never overwrite input files.
