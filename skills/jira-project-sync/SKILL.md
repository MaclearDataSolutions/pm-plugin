---
name: jira-project-sync
description: use this skill after /gantt-chart-creator or after a replan to sync the project plan to Jira. Creates Epics for work packages, Stories for tasks (with originalEstimate set from plan duration), and Tasks for milestones (label "milestone", due date set). Reads project/gantt_tasks.csv and .pm-config.json. Stores all Jira issue IDs in project/jira_sync.json to prevent duplicates on re-runs.
argument-hint: [path to gantt_tasks.csv — default: project/gantt_tasks.csv]
allowed-tools: Read, Write, Edit, mcp__atlassian-rovo-mcp__getJiraProjectIssueTypesMetadata, mcp__atlassian-rovo-mcp__createJiraIssue, mcp__atlassian-rovo-mcp__editJiraIssue, mcp__atlassian-rovo-mcp__addCommentToJiraIssue, mcp__atlassian-rovo-mcp__searchJiraIssuesUsingJql, mcp__atlassian-rovo-mcp__getJiraIssue, mcp__atlassian-rovo-mcp__createIssueLink, mcp__atlassian-rovo-mcp__getIssueLinkTypes
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
  "schema_version": "1.1",
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
      "estimated_hours": 16,
      "start_date": "2026-07-01",
      "due_date": "2026-07-05",
      "is_subtask": false,
      "parent_task_id": null,
      "parent_jira_key": null
    },
    {
      "task_id": "T2",
      "task_name": "Interview prep",
      "jira_key": "COR-3",
      "jira_id": "10003",
      "issue_type": "Subtask",
      "epic_key": "COR-1",
      "estimated_hours": 8,
      "start_date": "2026-07-01",
      "due_date": "2026-07-02",
      "is_subtask": true,
      "parent_task_id": "T1",
      "parent_jira_key": "COR-2"
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
  "issue_links": [
    {
      "from_task_id": "T3",
      "from_jira_key": "COR-4",
      "to_task_id": "T1",
      "to_jira_key": "COR-2",
      "link_type": "is blocked by",
      "jira_link_id": "10050"
    }
  ],
  "pm_status_ticket": {
    "jira_key": "COR-100",
    "jira_id": "10100",
    "summary": "[Client Onboarding Revamp] PM Status"
  }
}
```

`schema_version` is `"1.1"`. Existing files at `"1.0"` are read normally — treat missing `start_date`, `due_date`, `is_subtask`, `parent_task_id`, `parent_jira_key` fields as `null` on first re-run.

## Workflow

1. Read `.pm-config.json` → get `jira_project_key`, `jira_cloud_id`, `project_name`. If any field is missing, stop and ask the user to fill them in.
2. Read `project/gantt_tasks.csv` (or the path from the argument). Parse all rows.
3. If `project/jira_sync.json` exists, load it — use existing keys as the "already synced" registry.
4. Call `getJiraProjectIssueTypesMetadata` with `cloudId` and `projectIdOrKey` → get available issue type names. Identify the exact names for Epic, Story, Task (names vary by project configuration).
5. **Create or update Epics** — one per unique value in the "Work package" column:
   - If no existing Epic in jira_sync.json for this work package: call `createJiraIssue` with `issueTypeName` = Epic name, `summary` = work package name.
   - If Epic already exists: call `editJiraIssue` to update summary if it changed.
6. **Create or update Tasks/Stories — Pass 1 (top-level tasks)** — for every row where `Milestone?` = `No` (or empty) AND `Parent task ID` column is blank or absent:
   - `summary` = Task name column
   - `description` = Task description column (if present)
   - `parent` = the Epic key for this row's work package
   - `additional_fields`: set `timeoriginalestimate` to Duration (business days) × 8 × 3600 (seconds). For example, 5 days = 144000 seconds. Set `duedate` = Estimated end column value (format: YYYY-MM-DD); set `start` = Estimated start column value (format: YYYY-MM-DD). Omit a date field entirely if its CSV value is blank or missing.
   - If no existing issue in jira_sync.json: create with `createJiraIssue`.
   - If already exists: call `editJiraIssue` to update summary, description, timeoriginalestimate, duedate, and start.
6a. **Create or update Subtasks — Pass 2** — for every row where `Milestone?` = `No` (or empty) AND `Parent task ID` column is non-empty:
   - Resolve the parent task's Jira key from `jira_sync.json` tasks array using `Parent task ID` value as `task_id`. If not found (parent was skipped or not yet synced), skip this subtask and flag: "Subtask {task_id} skipped — parent {parent_task_id} not found in jira_sync.json. Re-run /jira-project-sync to register it."
   - `issueTypeName` = the subtask issue type name discovered in step 4 via `getJiraProjectIssueTypesMetadata`. Try `Subtask` first, then `Sub-task` as fallback. If neither is present in the project's available types, flag: "No subtask issue type found for project {jira_project_key} — subtask {task_id} skipped." and continue.
   - `parent` = parent task's `jira_key` (the Story key, not the Epic key).
   - `summary` = Task name column.
   - `description` = Task description column (if present).
   - `additional_fields`: set `timeoriginalestimate`, `duedate`, `start` using the same rules as Step 6. Do NOT set `parent` to the Epic key — Jira inherits the Epic link from the parent Story automatically.
   - If no existing issue in jira_sync.json: create with `createJiraIssue`.
   - If already exists: call `editJiraIssue` to update summary, description, timeoriginalestimate, duedate, and start.
   - Write to `jira_sync.json` tasks array with `is_subtask: true`, `parent_task_id` = the CSV value, `parent_jira_key` = resolved parent Jira key.
7. **Create or update milestone Tasks** — for every row where `Milestone?` = `Yes`:
   - `issueTypeName` = Task
   - `summary` = Task name column
   - `additional_fields`: `labels` = ["milestone"], `duedate` = Milestone date column (format: YYYY-MM-DD)
   - If no existing milestone in jira_sync.json: `createJiraIssue`.
   - If already exists: `editJiraIssue` to update summary, labels, duedate.
7a. **Create issue links** — after all tasks, subtasks, and milestones exist in Jira:
   - Call `getIssueLinkTypes` with `cloudId` = jira_cloud_id. Find the link type where the outward description is "blocks" and the inward description is "is blocked by" (match case-insensitively). Store its `id` as `blocked_link_type_id`.
   - If no matching link type is found, report: "No 'blocks/is blocked by' link type found in this Jira project. Available types: {list names}. Issue links skipped." and continue to step 8.
   - Load existing `issue_links` from `jira_sync.json` (or empty array if absent) to identify already-created links.
   - For each task row in `gantt_tasks.csv` where `Depends on` is non-empty:
     - Parse the comma-separated predecessor task IDs (e.g. `T1, T2` → `["T1", "T2"]`).
     - For each predecessor task ID:
       - Look up the current task's `jira_key` and the predecessor's `jira_key` in `jira_sync.json`. If either is not found, skip and flag: "Link skipped — {task_id} or {predecessor_id} not in jira_sync.json."
       - Check `jira_sync.json issue_links` for an existing entry with matching `from_task_id` and `to_task_id`. If found, skip.
       - Call `getJiraIssue` with `cloudId`, `issueIdOrKey` = current task's jira_key, `fields: ["issuelinks"]`. Scan the returned `issuelinks` array for an existing `is blocked by` link pointing to the predecessor's jira_key. If found, skip.
       - Call `createIssueLink` with `cloudId` = jira_cloud_id, `issueLinkTypeId` = blocked_link_type_id, `inwardIssueKey` = current task's jira_key (the blocked task), `outwardIssueKey` = predecessor's jira_key (the blocking task). Record the returned link ID.
       - Append to `jira_sync.json issue_links`: `{ "from_task_id": current, "from_jira_key": current key, "to_task_id": predecessor, "to_jira_key": predecessor key, "link_type": "is blocked by", "jira_link_id": returned id }`.
   - **Removed dependencies (replan):** For each entry in `jira_sync.json issue_links`, check if the `from_task_id` row in the current CSV still lists `to_task_id` in its `Depends on` column. If the dependency was removed, call `addCommentToJiraIssue` on `from_jira_key`: "Dependency on {to_jira_key} was removed in a replan on {today YYYY-MM-DD}. Link kept for audit trail." Do NOT delete the Jira link.

8. **Handle removed tasks** (replan mode) — compare existing jira_sync.json task IDs against current gantt_tasks.csv. For any task_id in jira_sync.json but not in the current CSV, call `addCommentToJiraIssue` with: "This task was removed from the project plan in a replan on YYYY-MM-DD. Issue kept for audit trail." Do NOT delete or transition the issue.
9. **Create pm-status ticket** if `pm_status_ticket` is absent from jira_sync.json:
   - `issueTypeName` = Task
   - `summary` = `[{project_name}] PM Status`
   - `additional_fields`: `labels` = ["pm-status"]
10. Write updated `project/jira_sync.json` with all IDs, using ISO 8601 timestamp for `last_synced`.
11. Report: counts of Epics created/updated, tasks created/updated (top-level + subtasks separately), milestones created/updated, issue links created/skipped, pm-status ticket key.

## Estimation conversion

Duration column in gantt_tasks.csv is in business days. Convert to Jira `timeoriginalestimate` (seconds):
- 1 business day = 8 hours = 28800 seconds
- Formula: `seconds = duration_days × 28800`
- If duration is missing or zero, omit the timeoriginalestimate field.

## Rules

- Never delete Jira issues. Removed tasks get a comment, not a deletion.
- Never transition issue status — use `/jira-board-refresh` to sync completion status to the Jira board.
- If `getJiraProjectIssueTypesMetadata` returns no Epic type, use Story for work packages and note the limitation in the report.
- If a task's work package does not match any existing Epic in the current sync, create a new Epic for it.
- Mark all estimates as "Planning assumption — confirm with team" in the description if Duration was marked as an assumption in gantt_tasks.csv.
