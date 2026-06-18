---
name: pm-status-broadcast
description: use this skill at the end of a Lane B progress run to broadcast structured status to Jira. Reads project/progress_clarification_log.md and project/effort_vs_actuals.md, builds a JSON status block, and overwrites the description of the pm-status Jira ticket (created by jira-project-sync). Personal PM reads this ticket via /personal-pm-dashboard. Run after /progress-update-clarifier and optionally after /jira-progress-pull.
allowed-tools: Read, Write, mcp__atlassian-rovo-mcp__searchJiraIssuesUsingJql, mcp__atlassian-rovo-mcp__getJiraIssue, mcp__atlassian-rovo-mcp__editJiraIssue, mcp__atlassian-rovo-mcp__createJiraIssue
---

# PM Status Broadcast

Write a structured JSON status block to the Jira pm-status ticket. This is the communication channel between Project PM and Personal PM.

## Inputs

- `.pm-config.json` — required: `jira_project_key`, `jira_cloud_id`, `project_name`
- `project/jira_sync.json` — provides `pm_status_ticket.jira_key`
- `project/progress_clarification_log.md` — source for RAG status, percent complete, risks, delays, current phase
- `project/gantt_tasks.csv` — source for next milestone name and date
- `project/effort_vs_actuals.md` — source for effort totals (optional — use zeros if absent)

## Outputs

- Updates the description of the Jira pm-status ticket (`pm_status_ticket.jira_key` from jira_sync.json)

## pm-status ticket description format

The description is **overwritten** (not appended) on every run. Format:

```
<!-- pm-status-v1 -->
```json
{
  "schema_version": "1.0",
  "project_name": "Client Onboarding Revamp",
  "jira_project_key": "COR",
  "last_updated": "2026-06-17T10:00:00Z",
  "progress": {
    "percent_complete": 45,
    "current_phase": "Implementation",
    "rag_status": "amber"
  },
  "next_milestone": {
    "name": "Phase 1 Complete",
    "target_date": "2026-07-15",
    "on_track": false,
    "days_variance": -5
  },
  "risks": [
    {
      "description": "Vendor delivery delay for component X",
      "severity": "high",
      "flagged_date": "2026-06-15"
    }
  ],
  "delays": [
    {
      "task_id": "T5",
      "task_name": "Integration testing",
      "days_behind": 3
    }
  ],
  "effort": {
    "total_estimated_hours": 240,
    "total_actual_hours": 98,
    "variance_percent": -59
  }
}
```
```

Note: the description starts with the HTML comment sentinel `<!-- pm-status-v1 -->` on its own line, immediately followed by a code fence containing the JSON. This sentinel lets Personal PM locate and parse the block reliably.

## Field extraction rules

**percent_complete:** Search `progress_clarification_log.md` for patterns like "XX% complete", "XX% done", "overall progress: XX". If not found, search `project/gantt_tasks.csv` — count rows where Status = "Done" or Progress = "100%" divided by total task rows (excluding milestones). If still not determinable, write `null` and note it.

**current_phase:** Look for the most recently passed milestone in `gantt_tasks.csv` (Milestone? = Yes, Milestone date <= today). Use its task name as the current phase label. If no milestones have passed, use the work package of the earliest in-progress task.

**rag_status:** Map the readiness decision from `progress_clarification_log.md`:
- `Ready for progress reporting` → `"green"`
- `Ready with unresolved items` → `"amber"`
- `Not ready - clarification required` → `"amber"`
- `Needs change-control workflow` → `"red"`
- Any blocked tasks or high-severity risks → `"red"` (overrides green/amber)
- If no progress_clarification_log.md exists: `"amber"`

**next_milestone:** From `gantt_tasks.csv`, find the earliest row where Milestone? = Yes and Milestone date > today. Calculate days_variance: if the milestone date is unchanged from the plan, days_variance = 0. If delayed tasks in the progress log affect this milestone's dependencies, estimate the variance from the delay data. If no milestone found, set `next_milestone` to `null`.

**risks:** Extract from `progress_clarification_log.md` — look for sections titled "Risks", "Change-control items", "Blockers". Each risk gets: description (text of the flag), severity (use "high" if the log says "high" or "critical"; "medium" for warnings; "low" otherwise), flagged_date (date of the progress_clarification_log.md file, formatted YYYY-MM-DD).

**delays:** Look in `progress_clarification_log.md` for tasks marked as delayed or blocked. For each: task_id (from gantt_tasks.csv match on task name), task_name, days_behind (extract number if stated, otherwise write 1 as a minimum).

**effort:** Read `project/effort_vs_actuals.md` summary table. Extract total_estimated_hours, total_actual_hours. Calculate variance_percent = round((actual - estimated) / estimated * 100, 1). If effort_vs_actuals.md is absent, write `{"total_estimated_hours": null, "total_actual_hours": null, "variance_percent": null}`.

## Workflow

1. Read `.pm-config.json` → get jira_project_key, jira_cloud_id, project_name.
2. Read `project/jira_sync.json` → get `pm_status_ticket.jira_key`. If jira_sync.json is missing or has no pm_status_ticket, stop and tell the user to run `/jira-project-sync` first.
3. Read `project/progress_clarification_log.md` → extract percent_complete, current_phase, rag_status, risks, delays using the rules above.
4. Read `project/gantt_tasks.csv` → find next_milestone and current_phase.
5. Read `project/effort_vs_actuals.md` if it exists → extract effort totals.
6. Build the JSON payload. Use ISO 8601 format for last_updated (today's date + current time in UTC as best estimate, note it is approximate if exact time is unavailable).
7. Construct the full description string: `<!-- pm-status-v1 -->\n\`\`\`json\n{json}\n\`\`\``
8. Call `editJiraIssue` with `cloudId`, `issueIdOrKey` = pm_status_ticket.jira_key, `fields` = `{"description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": "<full description string>"}]}]}}`. Use `contentFormat: "markdown"` if the API supports it; otherwise wrap in ADF paragraph node.
9. Report: pm-status ticket key updated, last_updated timestamp, RAG status broadcast.

## Rules

- Overwrite the description — never append to it. The ticket always shows current state only.
- Never invent data. If a field cannot be determined, write `null` and note it in the report.
- Do not transition the pm-status ticket status — leave it at whatever state it is in.
- If jira_sync.json is missing: stop with clear instructions to run /jira-project-sync first.
