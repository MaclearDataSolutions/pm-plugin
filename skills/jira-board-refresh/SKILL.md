---
name: jira-board-refresh
description: use this skill in a project workspace to sync task completion status to the Jira board. Reads project/gantt_tasks.csv (Status column) and optionally project/progress_clarification_log.md, builds a target status map, shows a preview of all planned transitions, waits for YES confirmation, then transitions Tasks/Stories, Epics (via roll-up), and milestones to match. Writes project/jira_board_refresh.md. Requires project/jira_sync.json — run /jira-project-sync first if missing.
allowed-tools: Read, Write, mcp__atlassian-rovo-mcp__getTransitionsForJiraIssue, mcp__atlassian-rovo-mcp__transitionJiraIssue, mcp__atlassian-rovo-mcp__getJiraIssue, mcp__atlassian-rovo-mcp__searchJiraIssuesUsingJql
---

# Jira Board Refresh

Sync task completion status from the project plan to the Jira board. Shows a preview of all planned transitions and waits for `YES` confirmation before making any changes.

## Inputs

| Source | Required | Purpose |
|--------|----------|---------|
| `.pm-config.json` | Yes | `jira_project_key`, `jira_cloud_id`, `project_name` |
| `project/gantt_tasks.csv` | Yes | Canonical task list with `Status` column |
| `project/jira_sync.json` | Yes | Maps task IDs to Jira issue keys |
| `project/progress_clarification_log.md` | No | Supplements CSV with Lane B confirmed completions |

## Outputs

- Jira board updated (transitions applied after confirmation)
- `project/jira_board_refresh.md` — timestamped report of every transition attempted

## Status Resolution

The skill builds a single `task_id → target_status` map. **CSV wins on conflict; log supplements blanks.**

1. **CSV (primary):** Read every row in `gantt_tasks.csv`. Map each Task ID to its `Status` value. If `Status` is blank or the column is absent, default to `To Do`.
2. **Log (supplementary):** If `progress_clarification_log.md` exists, scan for task names explicitly marked as completed or in-progress. Match by task name to the CSV task list. Override only where CSV is blank or `To Do`; never override `In Progress` or `Done` from CSV.

Conflict resolution:

| CSV | Log | Resolved |
|-----|-----|----------|
| `Done` | `In Progress` | `Done` |
| `In Progress` | `Done` | `In Progress` |
| `To Do` | `Done` | `Done` |
| blank | `In Progress` | `In Progress` |

**Jira transition discovery:** Call `getTransitionsForJiraIssue` on the first task in `jira_sync.json` to discover available transition names and IDs. Map canonically:
- `To Do` → transition name containing "To Do", "Backlog", or "Open"
- `In Progress` → transition name containing "In Progress" or "Start"
- `Done` → transition name containing "Done", "Closed", or "Resolved"

If ALL three status mappings fail (no usable transitions found at all), stop before building the transition queue and report the available transition names so the user can investigate the Jira workflow. If only some mappings fail, issues requiring that unmapped status are skipped and flagged in the report with the available transition names listed.

Note: transition discovery uses the first task in `jira_sync.json`. If Epic or milestone issues use a different Jira workflow with different transition names, their transitions may not map correctly. If an Epic or milestone transition fails with "transition not found", check the Jira workflow configuration for that issue type.

## Transition Logic

### Tasks and Stories

For each entry in `jira_sync.json` tasks array:
1. Call `getJiraIssue` with `cloudId` = jira_cloud_id, `issueIdOrKey` = jira_key to get the issue. Extract the current status name from the response.
2. Look up `target_status` from the resolved map using the task's `task_id`. If not found in the map, default to `To Do`.
3. If current status name already matches target: mark as "no change needed", skip.
4. Otherwise: queue a transition to the target status using the transition ID discovered in the discovery step.

### Epic Roll-up

After resolving all task statuses, evaluate each Epic in `jira_sync.json` epics array. Determine Epic target by looking at the resolved statuses of all tasks whose `epic_key` matches this Epic's `jira_key`:

| Child task states | Epic target |
|------------------|-------------|
| All `Done` | `Done` |
| Any `In Progress`, none blocked | `In Progress` |
| All `To Do` | `To Do` |
| Mixed (`Done` + `To Do`, no `In Progress`) | Skip — flag as "Epic status indeterminate — mixed child states, manual review recommended" |
| No child tasks in `jira_sync.json` | Skip — flag as "Epic has no registered child tasks — run `/jira-project-sync` to register them" |

Call `getJiraIssue` with `cloudId` = jira_cloud_id, `issueIdOrKey` = Epic's `jira_key` to get current status before queuing.

### Milestones

For each entry in `jira_sync.json` milestones array, transition to `Done` only when **both** conditions are met:
- `milestone_date` ≤ today's date (compare as YYYY-MM-DD strings)
- All tasks in the same work package are `Done`

To find the work package for a milestone:
1. Find the milestone's row in `gantt_tasks.csv` by matching `Task ID`.
2. Read that row's `Work package` column value (exact column name as produced by `/gantt-chart-creator`: `Work package` with capital W, lowercase p).
3. Find the Epic in `jira_sync.json` epics array where `work_package` equals that value → get its `jira_key`.
4. Find all tasks in `jira_sync.json` tasks array where `epic_key` equals that Epic `jira_key`.
5. Check that every task in step 4 has resolved status `Done`.

If step 3 finds no matching Epic (work package name not in `jira_sync.json` epics): skip + flag as "Milestone {task_id} work package '{work_package}' not found in jira_sync.json — run `/jira-project-sync` to register it."

If step 4 finds no tasks for the Epic (Epic has no registered children): skip + flag as "Milestone {task_id} Epic has no registered child tasks — cannot determine work package completion."

If only the date condition is met but tasks are incomplete: skip and flag as "Milestone date passed but work package not complete."

If neither condition is met: mark as "no change needed", skip.

### pm-status ticket exclusion

The pm-status ticket (`jira_sync.json → pm_status_ticket`) is excluded from all transitions. It is managed exclusively by `/pm-status-broadcast`.

## Preview and Confirm

After building the full transition queue, display:

```
Jira Board Refresh — Preview
─────────────────────────────────────────────────────────────────────
 Issue     Summary                          Current         → Target
─────────────────────────────────────────────────────────────────────
 COR-2     Stakeholder interviews           To Do           → In Progress
 COR-3     Requirements doc                 In Progress     → Done
 COR-5     Discovery Complete (milestone)   To Do           → Done
 COR-1     Discovery (Epic)                 In Progress     → Done
 COR-8     Workshop facilitation            To Do           → To Do     [skip]
─────────────────────────────────────────────────────────────────────
 4 transitions queued. 1 skipped (no change). 0 flagged.

Flagged (will not transition):
  COR-11  Phase 2 Complete (milestone) — date passed but work package incomplete

Proceed? Reply YES to apply, anything else cancels.
```

Wait for the user's reply:
- `YES` (case-insensitive): apply all queued transitions one at a time
- Anything else: cancel — write report with "Cancelled at preview" header and stop. No Jira API calls after cancellation.

## Report Format

Write `project/jira_board_refresh.md` after execution (or after cancellation):

```markdown
# Jira Board Refresh Report

Generated: YYYY-MM-DD
Project: {project_name} ({jira_project_key})
Status source: CSV + Lane B log  (or: CSV only — log not found)

## Transitions Applied

| Issue | Summary | From | To | Result |
|-------|---------|------|----|--------|
| COR-2 | Stakeholder interviews | To Do | In Progress | Success |
| COR-3 | Requirements doc | In Progress | Done | Success |

## Skipped (no change needed)

| Issue | Summary | Status |
|-------|---------|--------|
| COR-8 | Workshop facilitation | To Do |

## Flagged (not transitioned)

| Issue | Summary | Reason |
|-------|---------|--------|
| COR-11 | Phase 2 Complete | Milestone date passed but work package incomplete |

## Errors

| Issue | Summary | Error |
|-------|---------|-------|
(none)
```

## Workflow

1. Read `.pm-config.json` → get `jira_project_key`, `jira_cloud_id`, `project_name`. Stop if any required field is missing: "`.pm-config.json` is missing required fields: {list}."
2. Read `project/jira_sync.json`. If absent: stop with "Run `/jira-project-sync` first to create the task registry."
3. Read `project/gantt_tasks.csv`. Build the primary status map: `task_id → Status`. If `Status` column is absent or blank for a row, default to `To Do`.
4. If `project/progress_clarification_log.md` exists: scan for task names explicitly marked completed or in-progress. Supplement the map where CSV status is blank or `To Do`. If the log is absent, note "Lane B log not found — using CSV status only" in the report header.
5. Call `getTransitionsForJiraIssue` with `cloudId` = jira_cloud_id, `issueIdOrKey` = first task's jira_key, to discover transition names and IDs. Map transitions to `To Do`, `In Progress`, and `Done` by name matching. If ALL three mappings fail (no usable transitions found), stop and list the available transition names so the user can investigate the Jira workflow configuration. If only some mappings fail, continue — issues requiring an unmapped status will be skipped and flagged at execution time.
6. **Tasks/Stories:** For each task in `jira_sync.json` tasks array: call `getJiraIssue` with `cloudId` and the task's `jira_key`, extract current status from the response, resolve target status from the map, queue transition if status differs.
7. **Epics:** For each Epic in `jira_sync.json` epics array: evaluate child task statuses, call `getJiraIssue`, queue or flag.
8. **Milestones:** For each milestone in `jira_sync.json` milestones array: check date and work-package completion, call `getJiraIssue`, queue or flag.
9. Display the preview table with all queued transitions, skips, and flags. Wait for `YES`.
10. If cancelled: write `project/jira_board_refresh.md` with "Cancelled at preview" header. Stop.
11. If confirmed: apply transitions one at a time via `transitionJiraIssue` with `cloudId`, `issueIdOrKey`, and the discovered `transitionId`. Record each result (success or error).
12. Write `project/jira_board_refresh.md` with full results.
13. Report summary: "{N} transitions applied, {N} skipped, {N} flagged, {N} errors. Report written to project/jira_board_refresh.md."

## Error Handling

| Condition | Behaviour |
|-----------|-----------|
| `jira_sync.json` missing | Stop: "Run `/jira-project-sync` first to create the task registry." |
| Task in CSV but not in `jira_sync.json` | Skip + flag: "Task ID {id} not registered — run `/jira-project-sync`." |
| Transition not found for target status | Skip + flag with available transition names listed |
| API error on a single transition | Record error in report, continue with remaining transitions |
| `progress_clarification_log.md` absent | Proceed CSV-only; note in report header |
| Epic roll-up indeterminate | Skip + flag: "mixed child states — manual review recommended" |
| Epic has no child tasks in `jira_sync.json` | Skip + flag: "Epic {epic_key} has no registered child tasks — run `/jira-project-sync`." |

## Rules

- Never transition issues without explicit `YES` confirmation from the user.
- Never delete or create Jira issues — transitions only.
- Always write `project/jira_board_refresh.md`, even on cancel or partial failure.
- Never invent status values. If a task has no `Status` in the CSV and no match in the log, it is `To Do`.
- The pm-status ticket is excluded from all transitions.
- If no transitions are queued (all issues already match target status): write `project/jira_board_refresh.md` with a "Board already in sync — no transitions needed." header (all four tables empty), skip the preview step, and report to the user.
