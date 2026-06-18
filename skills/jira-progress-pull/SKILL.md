---
name: jira-progress-pull
description: use this skill during Lane B progress tracking to pull actual hours logged in Jira against plan estimates. Reads project/jira_sync.json for task issue keys, calls getJiraIssue for each task to read timeoriginalestimate and worklog totals, and produces project/effort_vs_actuals.md. Run after /progress-update-clarifier and before /pm-status-broadcast.
allowed-tools: Read, Write, mcp__atlassian-rovo-mcp__getJiraIssue, mcp__atlassian-rovo-mcp__searchJiraIssuesUsingJql
---

# Jira Progress Pull

Read actual hours logged in Jira against plan estimates. Produces `project/effort_vs_actuals.md` for use by `pm-status-broadcast` and `progress-slide-deck-creator`.

## Inputs

- `.pm-config.json` — required: `jira_cloud_id`, `project_name`
- `project/jira_sync.json` — provides all task issue keys and their estimated_hours

## Outputs

- `project/effort_vs_actuals.md`

## effort_vs_actuals.md format

```markdown
# Effort vs Actuals

Generated: YYYY-MM-DD
Project: {project_name}
Jira project: {jira_project_key}

## Summary

| Metric | Value |
|--------|-------|
| Total estimated hours | 240h |
| Total actual hours logged | 98h |
| Variance | -59.2% (under-spending) |
| Tasks with no time logged | 8 of 12 |

## By task

| Task ID | Task | Estimated (h) | Actual (h) | Variance % | Status |
|---------|------|--------------|------------|------------|--------|
| T1 | Stakeholder interviews | 16 | 18 | +12.5% | Over estimate |
| T2 | Requirements doc | 24 | 22 | -8.3% | Under estimate |
| T3 | Workshop facilitation | 8 | 0 | — | No time logged |

## Notes

- Actuals sourced from Jira worklogs as of YYYY-MM-DD
- Estimated hours sourced from project/jira_sync.json (set at /jira-project-sync time)
- Tasks with no worklogs show 0h actual and "No time logged" status
- Milestones are excluded from this table (they have no work estimate)
```

## Workflow

1. Read `.pm-config.json` → get jira_cloud_id, project_name, jira_project_key.
2. Read `project/jira_sync.json` → get the `tasks` array. Each entry has `jira_key` and `estimated_hours`.
3. For each task in the `tasks` array:
   - Call `getJiraIssue` with `cloudId` = jira_cloud_id, `issueIdOrKey` = jira_key, `fields` = ["timeoriginalestimate", "worklog", "summary", "status"]
   - Extract `timeoriginalestimate` (field is in seconds; convert to hours: `hours = seconds / 3600`). Use `estimated_hours` from jira_sync.json as fallback if the field is null.
   - Extract `worklog.worklogs` array → sum all `timeSpentSeconds` values → convert to hours.
   - Record: task_id, task_name, estimated_hours, actual_hours, variance_percent.
4. Calculate variance_percent for each task: `round((actual - estimated) / estimated * 100, 1)`. If estimated = 0, write `null`.
5. Calculate totals: sum all estimated_hours and all actual_hours across tasks.
6. Calculate overall variance_percent: `round((total_actual - total_estimated) / total_estimated * 100, 1)`.
7. Count tasks with actual_hours = 0 ("no time logged").
8. Write `project/effort_vs_actuals.md` using the format above.
9. Report: total estimated, total actual, overall variance, number of tasks with no time logged.

## Jira worklog field details

- `getJiraIssue` returns `worklog` only if `"worklog"` is explicitly included in the `fields` parameter.
- The worklog object has structure: `{"startAt": 0, "maxResults": 20, "total": N, "worklogs": [{"timeSpentSeconds": 3600, ...}]}`
- If `worklog.total > worklog.maxResults`, there are more worklogs than returned. In this case, note "Partial worklog — Jira returned first 20 entries only" in the task row's notes column.
- `timeoriginalestimate` is the total original estimate in seconds. It is set when the issue is created/edited via the `additional_fields` parameter.

## Rules

- Read-only skill — never create, edit, or transition Jira issues.
- If jira_sync.json is missing: stop with "Run /jira-project-sync first to create the task registry."
- If a task's jira_key returns a 404: note "Issue not found in Jira" and continue with remaining tasks.
- Milestones (from `jira_sync.milestones`) are excluded — they have no work estimate.
