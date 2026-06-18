# CLAUDE.md — PM Plugin

## Plugin purpose

This plugin provides a 3-lane project management workflow that turns owner input into planning documents, a Gantt chart, an Excel task workbook, and an introductory slide deck. It integrates with Jira for task tracking, status broadcasts, and cross-project visibility.

## Configuration

Each workspace has a `.pm-config.json` at its root. Read it at the start of every session:
- `"role": "project"` — Full 3-lane PM workflow (Baseline, Lane A, Lane B)
- `"role": "personal"` — Cross-project dashboard and effort vs actuals view

## Active project workspace (project role only)

All project artifacts live in the `project/` subfolder of the workspace. When reading or writing questionnaires, plans, Gantt files, or decks, use `project/<filename>` paths.

## Baseline setup (run once at project start)

1. `/project-owner-questionnaire` → `project/empty_questionnaire.md` + `project/filled_questionnaire.md`
2. `/questionnaire-project-plan` → `project/project_plan.md`
3. `/gantt-chart-creator` → `project/gantt_chart.md`, `project/gantt_chart.xlsx`, `project/gantt_tasks.csv`
4. `/project-intro-slide-deck` → `project/project_intro_deck.pptx`
5. `/jira-project-sync` → `project/jira_sync.json` (creates Epics, Tasks, milestone Tasks in Jira)

## Lane A — Change / Replan

Always creates new timestamped snapshots. Never overwrites the active plan.

1. Place update files (emails, notes) in `updates/`
2. `/project-update-intake` → `project/update.md`
3. `/project-update-clarifier` → `project/update_clarification_log.md`
4. `/project-replan-snapshot-builder` → `replans/<ts>_project_plan.md` + manifest
5. `/project-replan-artifact-snapshot-builder` → timestamped Excel, Gantt, deck in `replans/`
6. `/project-update-archiver` → moves source files to `archive/`
7. `/jira-project-sync` → updates Jira issues to match the new plan

## Lane B — Progress Tracking

Always appends or creates new files. Never overwrites active artifacts.

1. Place meeting notes, status notes in `progress_inputs/`
2. `/repo-progress-capture` → `project/progress_update.md`
3. `/progress-update-clarifier` → `project/progress_clarification_log.md`
4. `/jira-progress-pull` → `project/effort_vs_actuals.md`
5. Any or all of:
   - `/progress-plan-log-appender` → appends `## YYYY-MM-DD` entry to `project/project_plan.md`
   - `/progress-excel-snapshot` → adds `YYYY-MM-DD` worksheet to `project/gantt_chart.xlsx`
   - `/progress-slide-deck-creator` → `progress_reports/YYYY-MM-DD_progress_deck.pptx`
6. `/pm-status-broadcast` → overwrites the Jira pm-status ticket description for this project

## Lane B → Lane A (manual trigger — explicit double confirmation required)

The owner must explicitly request a replan. The exact phrase `YES CREATE REPLAN FILE` is required to confirm.

## Personal PM workspace (personal role only)

1. `/personal-pm-setup` → creates `.pm-config.json` with `role: personal`, links Jira projects
2. `/personal-pm-dashboard` → `dashboard/YYYY-MM-DD_dashboard.md` (regenerated on every run)

## Available skills

### Baseline lane
- `project-owner-questionnaire` — Create or fill the owner questionnaire
- `questionnaire-project-plan` — Convert questionnaire → `project/project_plan.md`
- `gantt-chart-creator` — Convert plan → `project/gantt_chart.md` + `project/gantt_chart.xlsx`
- `project-intro-slide-deck` — Create intro slide deck from plan + tasks

### Lane A — Change / Replan
- `project-update-intake` — Consolidate update files from `updates/` into `project/update.md`
- `project-update-clarifier` — Clarify change scope before replanning
- `project-replan-snapshot-builder` — Build timestamped plan snapshot
- `project-replan-artifact-snapshot-builder` — Build timestamped Excel, Gantt, deck
- `project-update-archiver` — Move processed source files to `archive/`

### Lane B — Progress Tracking
- `repo-progress-capture` — Capture progress from git + `progress_inputs/`
- `progress-update-clarifier` — Clarify progress details and flag change-control items
- `progress-plan-log-appender` — Append dated progress note to `project/project_plan.md`
- `progress-excel-snapshot` — Add dated worksheet to `project/gantt_chart.xlsx`
- `progress-slide-deck-creator` — Create dated progress deck in `progress_reports/`

### Jira integration
- `jira-project-sync` — Push plan tasks to Jira (run after baseline + after replan)
- `jira-progress-pull` — Pull Jira worklogs → `project/effort_vs_actuals.md`
- `pm-status-broadcast` — Write structured status to Jira pm-status ticket

### Personal PM
- `personal-pm-setup` — Initialize personal workspace, link Jira projects
- `personal-pm-dashboard` — Generate cross-project dashboard from Jira

## Rules

- Never overwrite active artifacts. Lane A creates timestamped snapshots. Lane B appends or creates new files.
- Never invent data. Mark missing info as `Not provided`, `TBD`, or `Planning assumption`.
- `project/project_plan.md` is the source of truth. All Gantt, Excel, and deck outputs derive from it.
- Lane B does not suggest replanning. The owner must explicitly request it with `YES CREATE REPLAN FILE`.
- All workspace folder names use `lower_snake_case`.
- Use `project/gantt_tasks.xlsx` as the structured task source — not the CSV.
- `project/jira_sync.json` tracks all Jira issue IDs to prevent duplicates on re-runs.
