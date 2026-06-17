---
name: replan-artifact-snapshot-builder
description: use this skill in claude code for lane a change or replan workflows after a timestamped project plan snapshot has been created. use when the user wants new timestamped static planning artifacts, such as excel, gantt csv, gantt markdown, or powerpoint, based on a timestamped *_project_plan.md and *_plan_change_manifest.json without modifying current excel files, current slide decks, current gantt files, templates, or the active project_plan.md.
---

# Replan Artifact Snapshot Builder

Generate new timestamped Excel, Gantt, CSV, and slide deck artifacts from a timestamped replan snapshot. This is the artifact step for **Lane A: Change / Replan**.

Read `references/artifact_snapshot_contract.md` before acting if you need the exact output contract.

## Core rule

Create new timestamped artifacts only. Do **not** overwrite or modify the current active Excel workbook, CSV, Gantt chart, original slide deck, previous progress decks, templates, or `project_plan.md`.

## Required inputs

1. A timestamped project plan snapshot, such as:

```text
replans/2026-06-12_1530_project_plan.md
```

2. Its matching manifest:

```text
replans/2026-06-12_1530_plan_change_manifest.json
```

Optional supporting inputs:

```text
replans/<timestamp>_plan_change_impact.md
project/gantt_tasks.csv
project/project_schedule.xlsx
project/gantt_chart.md
company_style/*.pdf
company_style/*.pptx
Templates/*.pptx
```

## Timestamp rule

Use the timestamp from the input replan files. Do not create a different timestamp unless no timestamp exists. If no timestamp exists, create one using local time in `YYYY-MM-DD_HHMM` format.

## Required outputs

Save outputs under the same replan folder or a timestamped subfolder:

```text
replans/<timestamp>_gantt_tasks.csv
replans/<timestamp>_gantt_chart.md
replans/<timestamp>_project_schedule.xlsx
replans/<timestamp>_project_replan_deck.pptx
replans/<timestamp>_artifact_snapshot_report.md
```

If the repo uses a `Replan_Snapshots/` or `Artifacts/replans/` folder, follow the established repo convention but keep the timestamp prefix.

## Workflow

1. Read the manifest first.
2. Read the timestamped project plan snapshot.
3. Read optional change impact file when available.
4. Inspect current baseline artifacts only as source/reference files.
5. Generate new timestamped task CSV and Gantt markdown from the timestamped plan snapshot.
6. Generate a new timestamped Excel workbook. Use the current workbook as a template/reference if useful, but save to a new timestamped file.
7. Generate a new timestamped replan slide deck. Use a template deck and company style references if present, but save to a new timestamped file.
8. Create an artifact snapshot report explaining what was generated and confirming that original files were not modified.

## Excel generation rules

- Use the timestamped project plan as the source of truth.
- If using an existing workbook, open it as a template/reference only.
- Save as `<timestamp>_project_schedule.xlsx`.
- Do not modify or save over the existing workbook.
- Include sheets such as:
  - Replan Summary
  - Gantt Tasks
  - Milestones
  - Risks and Issues
  - Assumptions and Open Questions
- Preserve company formatting when safely possible, but correctness and non-destructive output are more important.

If a project-local script is needed, generate it under:

```text
scripts_generated/create_replan_excel_snapshot.py
```

The script must accept input and output paths and must not overwrite input files.

## Slide deck generation rules

- Use the timestamped project plan and manifest as source of truth.
- Use `company_style/*.pdf` for company name, tone, terminology, and visual reference.
- Use an available `.pptx` template if present.
- Save as `<timestamp>_project_replan_deck.pptx`.
- Do not modify or overwrite the template, original intro deck, or any previous progress/replan deck.
- Include slides such as:
  - Title / replan snapshot date
  - Why the replan was needed
  - What changed
  - Updated scope and deliverables
  - Updated timeline / Gantt summary
  - Key risks and decisions
  - Next steps / approvals needed

If a project-local script is needed, generate it under:

```text
scripts_generated/create_replan_slide_deck.py
```

The script must accept input and output paths and must not overwrite input files.

## Artifact snapshot report

Create `<timestamp>_artifact_snapshot_report.md` with:

- Inputs used
- Outputs created
- Timestamp applied
- Baseline/reference files inspected
- Confirmation that no current artifacts were modified
- Any assumptions or missing information
- Recommended review steps

## Do not do these things

- Do not update the active `project_plan.md`.
- Do not update the active `project_schedule.xlsx`.
- Do not update the active `gantt_tasks.csv`.
- Do not overwrite the current slide deck or template deck.
- Do not create progress-only reports in this skill.
- Do not use `progress_update.md` as the source of truth for this workflow.
