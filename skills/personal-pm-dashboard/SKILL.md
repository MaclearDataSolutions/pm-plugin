---
name: personal-pm-dashboard
description: use this skill in a personal PM workspace to generate a cross-project status dashboard. Reads pm-status tickets from all Jira projects linked in .pm-config.json, surfaces per-project status (RAG, % complete, next milestone), cross-project risks, delays, effort vs actuals, and all Jira tasks currently assigned to the user. Writes dashboard/YYYY-MM-DD_dashboard.md. Requires .pm-config.json with role "personal" — run /personal-pm-setup first if not configured.
allowed-tools: Read, Write, Bash, mcp__atlassian-rovo-mcp__atlassianUserInfo, mcp__atlassian-rovo-mcp__searchJiraIssuesUsingJql, mcp__atlassian-rovo-mcp__getJiraIssue
---

# Personal PM Dashboard

Generate a cross-project dashboard from Jira pm-status tickets. Creates `dashboard/YYYY-MM-DD_dashboard.md` — regenerated on every run.

## Inputs

- `.pm-config.json` — required: `role` = "personal", `linked_projects` array

## Outputs

- `dashboard/YYYY-MM-DD_dashboard.md` — regenerated on every run (previous dashboards are kept)

## dashboard/YYYY-MM-DD_dashboard.md format

```markdown
# Personal PM Dashboard — YYYY-MM-DD

Generated: YYYY-MM-DD
User: {user_name}
Projects monitored: {N}

---

## Portfolio Overview

| Project | Phase | % Complete | RAG | Next Milestone | Days to Milestone |
|---------|-------|-----------|-----|----------------|------------------|
| Client Onboarding Revamp (COR) | Implementation | 45% | Amber | Phase 1 Complete | 28 |
| Infrastructure Upgrade (INF) | Discovery | 20% | Green | Requirements Sign-off | 45 |

---

## Projects Needing Attention

### Red — {project name} ({KEY})
**Status:** {rag reason from pm-status}
**Risks:** {risk descriptions, one per line}
**Delays:** {delayed task names with days_behind}

### Amber — {project name} ({KEY})
**Status:** {rag reason}
**Watch items:** {any risks or unresolved items}

(Omit this section entirely if all projects are Green.)

---

## My Tasks (across all projects)

| Project | Issue | Summary | Status | Due |
|---------|-------|---------|--------|-----|
| COR | COR-15 | Finalize requirements document | In Progress | 2026-07-01 |
| INF | INF-8 | Review infrastructure proposal | To Do | 2026-07-10 |

(Write "No open tasks assigned to you." if the query returns nothing.)

---

## Cross-project Effort vs Actuals

| Project | Estimated (h) | Actual (h) | Variance |
|---------|--------------|------------|----------|
| COR | 240 | 98 | -59% |
| INF | 120 | 0 | No time logged |

(Write "No effort data available — run /jira-progress-pull in each project workspace." if all projects have null effort fields.)

---

## Risks & Delays Across Portfolio

| Project | Item | Severity | Flagged |
|---------|------|----------|---------|
| COR | Vendor delivery delay for component X | High | 2026-06-15 |

(Write "No risks or delays flagged." if the risks and delays arrays are empty across all projects.)

---

## Data Freshness

| Project | Last Updated | Status |
|---------|-------------|--------|
| COR | 2026-06-17 10:00 UTC | Current |
| INF | No pm-status data | Run /pm-status-broadcast in INF workspace |
```

## Workflow

1. Read `.pm-config.json` → verify `role` = "personal". If role is "project", stop: "This skill is for personal workspaces only. Use /pm-status-broadcast for project workspaces."
2. Get current user: call `atlassianUserInfo` → extract `accountId` (for "my tasks" JQL query) and `displayName`.
3. **For each entry in `linked_projects`:**
   a. Call `searchJiraIssuesUsingJql` with `cloudId` = jira_cloud_id, `jql` = `project = "{jira_project_key}" AND labels = "pm-status"`, `fields` = ["summary", "description"], `maxResults` = 1.
   b. If no result: record this project as "No pm-status data — run /pm-status-broadcast in the project workspace."
   c. If found: call `getJiraIssue` with `cloudId`, `issueIdOrKey` = returned key, `fields` = ["description"].
   d. In the description, find the line `<!-- pm-status-v1 -->`. Extract the JSON block that follows (the content between the ` ```json ` and ` ``` ` fences immediately after the sentinel).
   e. Parse the JSON. Store: project_name, percent_complete, current_phase, rag_status, next_milestone, risks, delays, effort, last_updated.
   f. If parsing fails (malformed JSON or missing sentinel): record "pm-status data unreadable — run /pm-status-broadcast again in the project workspace."
4. **Get my tasks:** call `searchJiraIssuesUsingJql` with `cloudId` (use the cloudId of the first linked project — or iterate per cloudId if linked_projects span multiple sites), `jql` = `assignee = "{accountId}" AND project in ({comma-separated project keys}) AND status not in (Done, Resolved, Closed) ORDER BY duedate ASC`, `fields` = ["summary", "status", "duedate", "project"], `maxResults` = 50.
5. Create the `dashboard/` directory if it does not exist.
6. Write `dashboard/YYYY-MM-DD_dashboard.md` using the format above. Use today's date for YYYY-MM-DD.
7. Report: number of projects with pm-status data, number of projects with no data, number of my open tasks, path of dashboard file written.

## RAG label mapping

In the dashboard, render RAG status as text labels (not emoji, for portability):
- `"green"` → `Green`
- `"amber"` → `Amber`
- `"red"` → `Red`
- unknown/null → `Unknown`

## Rules

- Regenerate the full dashboard on every run — do not append to existing dashboards.
- Previous dashboard files (`dashboard/YYYY-MM-DD_dashboard.md` for earlier dates) are kept untouched.
- Never write data that could not be sourced from Jira or .pm-config.json. Write "Not available" for missing fields.
- If all projects return "No pm-status data", write the dashboard anyway with a clear call to action for each project.
- This skill is read-only with respect to Jira — never create, edit, or transition issues.
