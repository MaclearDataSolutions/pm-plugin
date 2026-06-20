---
name: gantt-chart-creator
description: use this skill in claude code when the user needs to reconstruct project flow and create a gantt chart plus excel project management view from project_plan.md or visible repo planning files. use for requests to produce gantt_chart.md, gantt_chart.xlsx, gantt_tasks.csv, task list, timeline, estimated durations, milestones, dependencies, progress, owners, status, and resource requirements. base outputs only on visible repo information, label unclear facts as unknown, and label estimates as assumptions. do not rely on a bundled python script; generate any excel script in the repo at runtime from the finalized markdown schedule.
---

# Gantt Chart Creator

Create `project/gantt_chart.md` first. Then generate a temporary Python script inside the user's repo to create `project/gantt_chart.xlsx` and `project/gantt_tasks.csv` from the finalized table in `project/gantt_chart.md`.

This skill intentionally does **not** include a prewritten Excel-generation `.py` file. Claude Code must create the script at runtime based on the repo contents and the finalized Markdown schedule.

## Goal

Reconstruct the project flow from the visible repository files and produce a basic project management view including:

- task list
- timeline
- task bars / estimated durations
- milestones
- dependencies
- progress
- owner or responsible role
- status
- resource requirements

Base the output on what is visible in the repo. Do not invent confirmed facts. If something is not clear, mark it as `Unknown`, `TBD`, or `Planning assumption - confirm`.

## Source file priority

1. Use the file the user names explicitly.
2. If no file is named, use `project/project_plan.md`.
3. Read supporting visible files when present, especially `project/filled_questionnaire.md`, `project/empty_questionnaire.md`, existing `project/gantt_chart.md`, and existing `project/gantt_tasks.csv`.
4. Check for `excel_template.json` (or any `excel_template_*.json`) in `tools/templates/`. If found, treat it as the available Excel template for this run.
5. If `project/project_plan.md` is missing, ask the user to create it first from the questionnaire/project-plan workflow.

## Main workflow

0b. If `meta.template_enabled` is `true`, read `source_table.columns` from the template. Use these column names, order, `align` values, `type`, `required`, and `default` values when writing the `## Project management source table` in `gantt_chart.md`. Do not freely choose column names or order when the template is active.

**`Parent task ID` column:** Optional. If a task row has a value here (e.g. `T2`), that task is a subtask of the referenced task in Jira. Leave blank for top-level tasks. Validation: a task cannot reference itself as its own parent; a task whose `Task ID` is referenced as a parent must not itself have a `Parent task ID` value (only one level of nesting).

**`Story points` column:** Auto-estimated using Fibonacci scale (1, 2, 3, 5, 8, 13, 21). Estimate each task based on: task description and name (clear/well-scoped = lower; vague/multi-part = higher), duration (longer tends higher, but approval steps stay low), dependencies (many predecessors = coordination risk, bump up), and resource requirements (multiple people or vendors = bump up). Rough guide: 1=trivial; 2=simple; 3=moderate; 5=non-trivial; 8=complex; 13=very large (consider splitting); 21=extremely large (strongly recommend splitting). Leave blank for milestone rows. Mark every auto-estimate in the `Assumption / unknown notes` column as: "Story points: planning assumption — confirm with team."

1. Read the full `project/project_plan.md` and any relevant visible repo files.
2. Identify the best available task table. Prefer a table with task, duration, dependencies, owner, status, progress, or resource columns.
3. Preserve the visible task order from the Markdown. Treat that order as the project flow when dependency data is missing.
4. Estimate missing durations and dates only to make a usable draft schedule. Label every estimate as an assumption.
5. Preserve visible owners, progress, status, milestones, and resource requirements. If not visible, write `Unknown` instead of guessing.
6. Create `project/gantt_chart.md` first. It must include a Mermaid Gantt chart and a detailed project management source table.
7. After `project/gantt_chart.md` is complete, generate a new local Python script in the repo at `tools/scripts/create_gantt_excel.py`.
8. The generated script must read the finalized source table from `project/gantt_chart.md`, then create `project/gantt_chart.xlsx` and `project/gantt_tasks.csv`.
9. Run the generated script, inspect the outputs, and update the script if needed.
10. Keep or remove the generated script according to the user's repo convention. If unsure, keep it and mention that it is generated.

## Runtime script requirement

Do not use a bundled script from this skill to create Excel. Instead, generate the Python script during the task.

The runtime-generated script should:

- read `project/gantt_chart.md`
- extract the `Project management source table`
- normalize dates, durations, dependencies, milestones, owners, progress, status, and resources
- create `project/gantt_tasks.csv`
- create `project/gantt_chart.xlsx`
- include helpful formatting in the workbook
- write clear errors when the Markdown table is missing or malformed

Use common Python libraries available in the repo environment when possible, such as `openpyxl` or `pandas` plus an Excel writer. If dependencies are missing, install them only with the user's permission or generate a simpler CSV-only fallback and explain the limitation.

When `meta.template_enabled` is `true`, the generated script must read `tools/templates/excel_template.json` at runtime for sheet names, column definitions, widths, colors, and filters. Do not hardcode those values in the generated script. The workbook sheet structure must match `excel.sheets` in the template.

## Rules for uncertainty

- Do not invent confirmed dates, owners, vendors, budgets, progress, approvals, or resource commitments.
- If a duration is missing, estimate it and mark the estimate basis.
- If a start date is missing, use a visible project start date, a user-provided start date, or today's date as a planning assumption.
- If dependency data is missing, use the visible Markdown task order as a provisional flow and mark it as an assumption.
- If owner, progress, status, or resources are missing, write `Unknown` unless the information is explicitly visible elsewhere in the repo.
- If a task appears to be a milestone only because of wording, mark it as an assumption, not confirmed.

## Required `gantt_chart.md` structure

Always write this structure:

```markdown
# Gantt Chart and Project Management View

## Source and evidence

## Project flow summary

## Schedule summary

## Mermaid Gantt chart

```mermaid
...
```

## Project management source table

| Task ID | Work package | Task | Task description | Owner / role | Resource requirements | Estimated start | Estimated end | Duration (business days) | Story points | Timeline basis | Task bar | Milestone? | Milestone date | Depends on | Parent task ID | Progress | Status | Source evidence | Assumption / unknown notes |
|---|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---:|---|---|---|---|---|---|

When `meta.template_enabled` is `true`, derive this header row and separator row from `source_table.columns` in the template instead of using the hardcoded column list above. Use `align: "right"` → `---:` and `align: "left"` → `---` for each column.

## Milestones

## Dependencies and project flow

## Resource requirements

## Progress and status view

## Assumptions used for estimates

## Unknowns to confirm

## Excel export notes
```

## Excel output standards

Create `gantt_chart.xlsx` from the finalized source table in `gantt_chart.md` using a Python script generated at runtime in the repo.

The workbook must include these sheets:

1. `Project View`
   - full project management source table
2. `Gantt Timeline`
   - one row per task
   - date columns across the schedule
   - visible task bars for active days
3. `Milestones`
   - task ID, milestone, date, owner, status, notes
4. `Resources`
   - task ID, task, owner, resource requirements, status
5. `Assumptions Unknowns`
   - estimates, assumptions, and missing information requiring confirmation

## Quality checklist

Before finishing, verify:

- `project/gantt_chart.md` exists and was written before Excel.
- The project flow comes from visible task order and dependencies.
- Every task has task, estimated start, estimated end, duration, owner/status/progress/resource fields, even when the value is `Unknown`.
- The `Parent task ID` column is present in the source table. Values are either blank or a valid `Task ID` from the same table. No task is its own parent, and no parent task itself has a non-blank `Parent task ID`.
- The `Story points` column is present in the source table. Every non-milestone task row has a Fibonacci value (1, 2, 3, 5, 8, 13, or 21). Milestone rows have a blank `Story points` value. Every auto-estimated value has "Story points: planning assumption — confirm with team" in its `Assumption / unknown notes` column.
- Every task row has a `Status` value in the `Status` column (`To Do`, `In Progress`, or `Done`). Default to `To Do` for all newly generated tasks.
- Estimated durations and dates are clearly marked as assumptions or estimates.
- The Mermaid chart starts with `gantt` and includes `dateFormat YYYY-MM-DD`.
- No prewritten Excel-generation Python file from this skill was used.
- A new Python script was generated in `tools/scripts/` at runtime to create Excel.
- `project/gantt_chart.xlsx` exists and is based on the finalized Markdown source table.
- `project/gantt_tasks.csv` exists for import into other tools.
- If `tools/templates/excel_template.json` exists and `meta.template_enabled` is `true`, the source table column names and order in `project/gantt_chart.md` exactly match `source_table.columns[].name` in the template.
