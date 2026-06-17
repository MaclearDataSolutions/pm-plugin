# Replan Snapshot Contract

This skill belongs to Lane A: Change / Replan. It handles changes that alter the approved plan, such as new ideas, owner requests, delays that require replanning, scope changes, date changes, budget changes, resource changes, or dependency changes.

Lane A is non-destructive. It never overwrites the current active project plan. It creates a new timestamped plan snapshot that can be reviewed and promoted later.

## Required inputs

- `update.md`: consolidated and confirmed change request from the update intake/clarifier workflow.
- The latest available current plan, usually `project_plan.md`, or the newest `*_project_plan.md` snapshot if the user asks to build from the latest snapshot.

## Required outputs

Use a timestamp prefix in local time. Recommended format: `YYYY-MM-DD_HHMM`.

- `<timestamp>_project_plan.md`
- `<timestamp>_plan_change_impact.md`
- `<timestamp>_plan_change_manifest.json`
- `<timestamp>_replan_summary.md`

Store outputs in `replans/` unless the repo uses another clearly established folder.

## Non-destructive rules

- Do not modify `project_plan.md`.
- Do not modify previous timestamped plan snapshots.
- Do not modify Excel files, CSV files, or slide decks.
- Do not remove, rename, or archive existing files.
- Do not silently resolve unclear changes. Mark them as assumptions or open questions.

## Plan snapshot requirements

The timestamped plan should be a complete static plan that can stand alone. It should include the updated schedule logic, scope, deliverables, milestones, task plan, dependencies, risks, assumptions, decisions, and open questions.

The plan should clearly identify:

- Source baseline plan used
- Source update file used
- Timestamp created
- Whether it is a draft replan or approved replan
- What changed from the baseline
- What was not changed
- Open questions and assumptions

## Manifest requirements

The manifest should describe what downstream artifacts must be generated in the artifact snapshot step. Include affected artifacts such as Excel workbook, Gantt CSV, Gantt chart markdown, and slide deck. The manifest must point to the new timestamped project plan snapshot, not the old plan.
