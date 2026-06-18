---
name: project-replan-snapshot-builder
description: use this skill in claude code for lane a change or replan work when approved updates, delays, scope changes, new ideas, date changes, resource changes, budget changes, dependency changes, or owner change requests should produce a new static project plan snapshot. use when files such as update.md, confirmed update.md, project_plan.md, or previous timestamped project plan snapshots are present and the user wants a timestamped replan without modifying the current project plan or existing artifacts.
---

# Project Replan Snapshot Builder

Build a new timestamped project plan snapshot from `update.md` plus the current or latest project plan. This skill is for **Lane A: Change / Replan**, not progress tracking.

Read `references/replan_snapshot_contract.md` before acting if you need the exact output contract.

## Core rule

Do **not** update, overwrite, restructure, rename, or delete the current project plan or any existing artifacts. Create new timestamped files only.

## Required inputs

1. `update.md` from the change intake and clarification workflow.
2. A baseline plan:
   - Prefer the user-specified plan file.
   - Otherwise use `project/project_plan.md` if present.
   - Otherwise use `project_plan.md` in the repo root if present.
   - If multiple timestamped plans exist and the user says “latest plan,” use the newest `*_project_plan.md` by timestamp or modified time.

## Required outputs

Create a timestamp using local time in this format:

```text
YYYY-MM-DD_HHMM
```

Save outputs under `replans/` unless the repo clearly uses another replan folder:

```text
replans/<timestamp>_project_plan.md
replans/<timestamp>_plan_change_impact.md
replans/<timestamp>_plan_change_manifest.json
replans/<timestamp>_replan_summary.md
```

## Workflow

1. Confirm this is Lane A change/replan, not progress-only reporting.
2. Read `update.md` completely.
3. Read the baseline project plan completely.
4. Identify whether the update changes scope, schedule, resources, budget, dependencies, risks, quality, approvals, deliverables, milestones, or communication.
5. Identify conflicts between the update and baseline plan.
6. Build a new complete static plan snapshot incorporating the confirmed update.
7. Mark assumptions clearly. If information is missing, write `TBD` or `Open question` rather than inventing facts.
8. Write the timestamped plan snapshot and related change files.
9. Tell the user that the current active plan was not modified.

## Output file content requirements

### `<timestamp>_project_plan.md`

Use the same major sections as the baseline project plan when possible, but update them for the new replan snapshot. Include these additional fields near the top:

```markdown
Replan timestamp: YYYY-MM-DD HH:MM
Baseline plan used: <path>
Update source used: <path>
Snapshot status: Draft replan snapshot
Non-destructive note: This file is a new replan snapshot. It does not overwrite the current active project plan.
```

### `<timestamp>_plan_change_impact.md`

Include:

- Executive summary of change impact
- Baseline plan file used
- Update file used
- Affected deliverables
- Affected tasks and milestones
- Affected dependencies
- Schedule impact
- Budget/resource impact
- Risks/issues created or changed
- Decisions needed
- Files to generate next

### `<timestamp>_plan_change_manifest.json`

Create valid JSON. Include at minimum:

```json
{
  "timestamp": "YYYY-MM-DD_HHMM",
  "workflow_type": "lane_a_change_replan_snapshot",
  "baseline_plan": "path/to/baseline/project_plan.md",
  "update_source": "path/to/update.md",
  "new_project_plan": "replans/YYYY-MM-DD_HHMM_project_plan.md",
  "do_not_modify": [
    "project_plan.md",
    "existing Excel workbooks",
    "existing slide decks",
    "previous timestamped replan snapshots"
  ],
  "affected_areas": [],
  "downstream_outputs_required": {
    "excel_snapshot": true,
    "slide_deck_snapshot": true,
    "gantt_csv_snapshot": true,
    "gantt_chart_snapshot": true
  },
  "open_questions": [],
  "assumptions": []
}
```

### `<timestamp>_replan_summary.md`

Write a concise handoff summary for the next skill, including:

- What changed
- What new files were created
- What downstream artifacts should be generated
- What must not be modified

## Do not do these things

- Do not edit `project_plan.md` in place.
- Do not update `gantt_tasks.csv` in place.
- Do not update Excel or PowerPoint in this skill.
- Do not create progress reporting updates.
- Do not treat a status update as a replan unless it explicitly changes the plan.
