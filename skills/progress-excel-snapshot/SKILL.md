---
name: progress-excel-snapshot
description: Add a new dated progress worksheet to the existing project Excel workbook from progress_update.md without modifying existing worksheets. Use after progress_update.md is confirmed and the user wants to record progress in Excel. This skill must preserve the current workbook, formulas, existing sheets, prior progress sheets, and baseline schedule; it only creates one new dated worksheet and an update report.
argument-hint: [workbook.xlsx path] [progress_update.md path]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Progress Excel Snapshot

Add a progress-only snapshot sheet to the project workbook. Do not replan and do not edit existing worksheets.

## Inputs

Default inputs:

- `project/project_schedule.xlsx`
- `project/progress_update.md`

Optional inputs:

- `project/gantt_tasks.csv`
- `project/progress_clarification_log.md`

If arguments are provided, treat the first as workbook path and the second as progress update path.

## Outputs

- Updated workbook with one new dated progress worksheet
- `project/excel_progress_snapshot_report.md`
- Optional generated script in `scripts_generated/`

## Hard boundary

Progress tracking is snapshot-based. Do not alter existing worksheets, charts, formulas, named ranges, formatting, prior progress sheets, or baseline schedule data. Only add one new worksheet for this update.

If a needed report cannot be produced without editing existing sheets, stop and explain the limitation.

## Workflow

1. Read `progress_update.md` and determine the update date.
2. Locate the workbook. Prefer `project/project_schedule.xlsx` unless the user gives another path.
3. Create a backup before modification:
   - `project/project_schedule_backup_YYYY-MM-DD_HHMMSS.xlsx`
4. Generate a project-local script in `scripts_generated/` to add the new worksheet. Do not rely on a pre-bundled script because workbook structures vary by project.
5. Use the script to load the workbook, create a new sheet, write the progress snapshot, and save the workbook.
6. Write `excel_progress_snapshot_report.md` with sheet name, source files, and confirmation that existing sheets were preserved.

## Worksheet naming

Use the update date as the sheet title:

- `YYYY-MM-DD`

If a sheet with that title already exists, use:

- `YYYY-MM-DD_2`
- `YYYY-MM-DD_3`

Keep worksheet names within Excel's worksheet title limits and avoid invalid characters.

## New sheet content

The new worksheet should include:

1. Title: `Progress Snapshot - YYYY-MM-DD`
2. Update summary
3. Completed since last update
4. In progress
5. Blocked / delayed
6. Risks and issues
7. Decisions made
8. Next actions
9. Source files reviewed
10. Potential change-control items, if any

Include a small status table when progress items can be structured:

| Category | Item | Owner | Status | Date | Notes |
|---|---|---|---|---|---|

## Timeline bar shading

When the snapshot sheet includes a timeline or mini-Gantt view, shade each task bar cell based on the task's `Progress` value, not a flat colour.

Use the colour scale from `tools/templates/excel_template.json` → `excel.sheets[Gantt Timeline].bar_progress_colors` when the file is present. If the file is absent, fall back to this default scale:

| Progress range | Hex colour | Meaning |
|---|---|---|
| 0% | `F2F2F2` | Not started |
| 1–25% | `DEEAF1` | Just started |
| 26–50% | `BDD7EE` | In progress |
| 51–75% | `70ADDB` | More than half done |
| 76–99% | `2E75B6` | Nearly complete |
| 100% | `1F3864` | Complete |

Rules:
- Read the `Progress` column from `gantt_tasks.csv` (or the baseline Gantt sheet if CSV is unavailable) to get the current percentage for each task.
- Apply the matching colour as a `PatternFill` on the bar cell(s) for that task row in the timeline section of the snapshot sheet.
- If progress data is missing for a task, use `F2F2F2` (not-started grey) and note it in the snapshot report.
- Do not apply this shading to cells outside the bar area (empty week columns keep their alternating row fill).

## Script generation requirements

When creating the project-local Python script:

- Prefer `openpyxl` for `.xlsx` workbook modification in Claude Code.
- Load the workbook with formulas and existing content preserved.
- Do not delete or rename sheets.
- Do not modify cells in existing sheets.
- Add a new sheet using the chosen dated title.
- Apply simple readable formatting to the new sheet only.
- Read `tools/templates/excel_template.json` at runtime to get `bar_progress_colors` for timeline bar shading. Do not hardcode the colour scale in the script.
- Save to the same workbook path only after a backup exists.

## Verification

After saving:

- List sheet names before and after.
- Confirm the only structural change is one added worksheet.
- Confirm the new sheet contains the progress update date and summary.
- Create `excel_progress_snapshot_report.md`.

If verification fails, restore from backup or stop and explain the issue.
