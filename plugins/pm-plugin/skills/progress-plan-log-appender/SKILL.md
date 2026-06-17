---
name: progress-plan-log-appender
description: Append a dated progress update note to project_plan.md without rewriting existing plan content. Use after progress-update-clarifier confirms project/progress_update.md and the user wants to record progress in the plan. This skill must only append a progress log entry and must not revise baseline scope, milestones, WBS, schedule, budget, risks, or any existing plan section.
argument-hint: [project_plan.md path] [progress_update.md path]
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash
---

# Progress Plan Log Appender

Append progress-only notes to `project_plan.md`. Never replan.

## Inputs

Default inputs:

- `project/project_plan.md`
- `project/progress_update.md`

If arguments are provided, treat the first as the plan path and the second as the progress update path.

Optional supporting input:

- `project/progress_clarification_log.md`

## Outputs

- Updated `project/project_plan.md` with a new dated progress note appended only
- `project/project_plan_append_log.md`

## Hard boundary

Do not edit existing plan sections. Do not restructure, summarize, rewrite, delete, sort, or normalize existing content.

Allowed operation:

- Append a new dated section under `# Progress Update Log`, or create that section at the end if it does not exist.

Disallowed operations:

- Changing the baseline plan
- Changing task IDs
- Changing milestones
- Changing dates
- Changing WBS or dependencies
- Changing risks, budget, scope, or resources
- Regenerating a plan from progress

If the progress update contains plan-changing information, append it only as a note marked `Potential change-control item`; do not incorporate it into the plan body.

## Workflow

1. Read `project_plan.md` and `progress_update.md`.
2. Determine the update date from `progress_update.md`. If missing, use today from the system date and mark `Date inferred from run date`.
3. Create a backup copy of the project plan before appending:
   - `project/project_plan_backup_YYYY-MM-DD_HHMMSS.md`
4. Build a concise dated progress entry.
5. Append it to `project_plan.md`:
   - If `# Progress Update Log` exists, append a new `## YYYY-MM-DD` subsection under it.
   - If it does not exist, append a separator, then `# Progress Update Log`, then the dated subsection at the very end of the file.
6. Write `project_plan_append_log.md` describing exactly what was appended.

## Appended entry format

Use this exact structure:

```markdown

---

# Progress Update Log

## YYYY-MM-DD

### Summary
[Short progress summary]

### Completed since last update
- [Completed item]

### In progress
- [In-progress item]

### Blocked / delayed
- [Blocked or delayed item]

### Risks, issues, and decisions
- [Risk, issue, or decision]

### Next actions
- [Action] — Owner: [owner or TBD] — Due: [date or TBD]

### Notes
- [Additional status note]
```

If `# Progress Update Log` already exists, append only the `## YYYY-MM-DD` section and its subsections.

## Verification

Before finishing:

- Confirm no existing content before the new appended entry was changed.
- Report the update date and the exact heading appended.
- If possible, compare file length or use a diff to verify the change is append-only.
