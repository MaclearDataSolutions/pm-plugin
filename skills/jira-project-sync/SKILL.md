---
name: jira-project-sync
description: use this skill after /gantt-chart-creator or after a replan to sync the project plan to Jira. Creates Epics for work packages, Stories for tasks (with originalEstimate set from plan duration), and Tasks for milestones (label "milestone", due date set). Reads project/gantt_tasks.csv and .pm-config.json. Stores all Jira issue IDs in project/jira_sync.json to prevent duplicates on re-runs.
argument-hint: [path to gantt_tasks.csv — default: project/gantt_tasks.csv]
allowed-tools: Read, Write, Edit, mcp__atlassian-rovo-mcp__getJiraProjectIssueTypesMetadata, mcp__atlassian-rovo-mcp__createJiraIssue, mcp__atlassian-rovo-mcp__editJiraIssue, mcp__atlassian-rovo-mcp__addCommentToJiraIssue, mcp__atlassian-rovo-mcp__searchJiraIssuesUsingJql
---

# Jira Project Sync

Map the project plan to Jira: create Epics, Stories, and milestone Tasks. Store all IDs in `project/jira_sync.json`. Safe to re-run — existing issues are updated, not duplicated.

## Inputs

- `.pm-config.json` — required fields: `jira_project_key`, `jira_cloud_id`, `project_name`
- `project/gantt_tasks.csv` — canonical task list (or path from argument)
- `project/jira_sync.json` — if present, load existing IDs to avoid duplicates

## Outputs

- `project/jira_sync.json` — maps every task ID to its Jira issue key

## jira_sync.json schema

```json
{
  "schema_version": "1.0",
  "project_name": "Client Onboarding Revamp",
  "jira_project_key": "COR",
  "jira_cloud_id": "macleardata.atlassian.net",
  "last_synced": "2026-06-17T10:00:00Z",
  "epics": [
    {
      "work_package": "Discovery",
      "jira_key": "COR-1",
      "jira_id": "10001",
      "summary": "Discovery"
    }
  ],
  "tasks": [
    {
      "task_id": "T1",
      "task_name": "Stakeholder interviews",
      "jira_key": "COR-2",
      "jira_id": "10002",
      "issue_type": "Story",
      "epic_key": "COR-1",
      "estimated_hours": 16
    }
  ],
  "milestones": [
    {
      "task_id": "M1",
      "task_name": "Discovery Complete",
      "jira_key": "COR-5",
      "jira_id": "10005",
      "issue_type": "Task",
      "milestone_date": "2026-07-15"
    }
  ],
  "pm_status_ticket": {
    "jira_key": "COR-100",
    "jira_id": "10100",
    "summary": "[Client Onboarding Revamp] PM Status"
  }
}
```

## Workflow

1. Read `.pm-config.json` → get `jira_project_key`, `jira_cloud_id`, `project_name`. If any field is missing, stop and ask the user to fill them in.
2. Read `project/gantt_tasks.csv` (or the path from the argument). Parse all rows.
3. If `project/jira_sync.json` exists, load it — use existing keys as the "already synced" registry.
4. Call `getJiraProjectIssueTypesMetadata` with `cloudId` and `projectIdOrKey` → get available issue type names. Identify the exact names for Epic, Story, Task (names vary by project configuration).
5. **Create or update Epics** — one per unique value in the "Work package" column:
   - If no existing Epic in jira_sync.json for this work package: call `createJiraIssue` with `issueTypeName` = Epic name, `summary` = work package name.
   - If Epic already exists: call `editJiraIssue` to update summary if it changed.
6. **Create or update Tasks/Stories** — for every row where `Milestone?` = `No` (or empty):
   - `summary` = Task name column
   - `description` = Task description column (if present)
   - `parent` = the Epic key for this row's work package
   - `additional_fields`: set `timeoriginalestimate` to Duration (business days) × 8 × 3600 (seconds). For example, 5 days = 144000 seconds.
   - If no existing issue in jira_sync.json: create with `createJiraIssue`.
   - If already exists: call `editJiraIssue` to update summary, description, and timeoriginalestimate.
7. **Create or update milestone Tasks** — for every row where `Milestone?` = `Yes`:
   - `issueTypeName` = Task
   - `summary` = Task name column
   - `additional_fields`: `labels` = ["milestone"], `duedate` = Milestone date column (format: YYYY-MM-DD)
   - If no existing milestone in jira_sync.json: `createJiraIssue`.
   - If already exists: `editJiraIssue` to update summary, labels, duedate.
8. **Handle removed tasks** (replan mode) — compare existing jira_sync.json task IDs against current gantt_tasks.csv. For any task_id in jira_sync.json but not in the current CSV, call `addCommentToJiraIssue` with: "This task was removed from the project plan in a replan on YYYY-MM-DD. Issue kept for audit trail." Do NOT delete or transition the issue.
9. **Create pm-status ticket** if `pm_status_ticket` is absent from jira_sync.json:
   - `issueTypeName` = Task
   - `summary` = `[{project_name}] PM Status`
   - `additional_fields`: `labels` = ["pm-status"]
10. Write updated `project/jira_sync.json` with all IDs, using ISO 8601 timestamp for `last_synced`.
11. Report: counts of Epics created/updated, tasks created/updated, milestones created/updated, pm-status ticket key.

## Estimation conversion

Duration column in gantt_tasks.csv is in business days. Convert to Jira `timeoriginalestimate` (seconds):
- 1 business day = 8 hours = 28800 seconds
- Formula: `seconds = duration_days × 28800`
- If duration is missing or zero, omit the timeoriginalestimate field.

## Rules

- Never delete Jira issues. Removed tasks get a comment, not a deletion.
- Never transition issue status — that is the team's responsibility.
- If `getJiraProjectIssueTypesMetadata` returns no Epic type, use Story for work packages and note the limitation in the report.
- If a task's work package does not match any existing Epic in the current sync, create a new Epic for it.
- Mark all estimates as "Planning assumption — confirm with team" in the description if Duration was marked as an assumption in gantt_tasks.csv.
