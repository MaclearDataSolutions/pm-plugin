# PM Plugin — User Manual

Complete reference for using pm-plugin. For installation see [README.md](README.md).

---

## Table of contents

1. [Concepts](#1-concepts)
2. [Workspace setup](#2-workspace-setup)
3. [Baseline lane — starting a project](#3-baseline-lane--starting-a-project)
4. [Lane A — making changes and replanning](#4-lane-a--making-changes-and-replanning)
5. [Lane B — progress tracking](#5-lane-b--progress-tracking)
6. [Jira integration](#6-jira-integration)
7. [Personal PM dashboard](#7-personal-pm-dashboard)
8. [File reference](#8-file-reference)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Concepts

### Two modes, one plugin

The plugin reads `.pm-config.json` at the start of every session and loads the correct behaviour automatically — no manual mode switching.

- `"role": "project"` — Activates the full 3-lane PM workflow. Use this in any project directory.
- `"role": "personal"` — Activates the cross-project dashboard. Use this in a dedicated personal workspace directory.

You open a folder, Claude Code reads the config, and the right skills activate. Exactly like Git knowing it's in a repo when you open a directory.

### Three lanes

```
Baseline ──────── run once at project start
    │
    └── Lane A ── run when the plan needs to change (replan)
    └── Lane B ── run weekly or daily (progress tracking)
```

**Baseline** builds all the initial artifacts from a filled questionnaire.

**Lane A** handles changes — scope changes, delays, owner decisions that require a new plan. It always creates timestamped snapshots; it never overwrites the active plan.

**Lane B** captures progress — git commits, meeting notes, status updates — and appends dated entries to the plan, the Excel workbook, and the slide deck. It also pulls Jira effort data and broadcasts status to the pm-status Jira ticket.

### Lane B → Lane A escalation

Lane B does not suggest replanning. If the progress review surfaces something that requires a plan change, the owner must explicitly request a replan by saying:

> "I want to start a replan based on the flagged items"

Claude will show a preview of the changes file and ask for the exact phrase `YES CREATE REPLAN FILE` before proceeding. Any other response cancels.

### Jira as the communication bus

Project PMs write structured status to a dedicated Jira ticket (`[project name] PM Status`) on every Lane B run. Personal PM reads these tickets across all linked projects to build the cross-project dashboard.

---

## 2. Workspace setup

### Project workspace

A project workspace is any directory with a `.pm-config.json` file containing `"role": "project"`.

```
my-project/
├── .pm-config.json          ← role: project
├── project/                 ← all generated artifacts live here
│   ├── project_plan.md
│   ├── gantt_chart.md
│   ├── gantt_chart.xlsx
│   ├── gantt_tasks.csv
│   ├── jira_sync.json
│   └── ...
├── updates/                 ← drop change requests here (Lane A)
├── progress_inputs/         ← drop meeting notes and status here (Lane B)
├── replans/                 ← timestamped plan snapshots (Lane A output)
├── progress_reports/        ← dated progress decks (Lane B output)
└── archive/                 ← processed update files (Lane A output)
```

**To set up a project workspace:**

```bash
mkdir my-project && cd my-project
cp "$(claude plugin path pm-plugin)/config-templates/project.pm-config.json" .pm-config.json
```

Edit `.pm-config.json`:

```json
{
  "role": "project",
  "project_name": "Client Onboarding Revamp",
  "jira_project_key": "COR",
  "jira_cloud_id": "your-org.atlassian.net",
  "owner": "harris.yang@maclear.ca"
}
```

### Personal workspace

A personal workspace is any directory with a `.pm-config.json` containing `"role": "personal"`. Run `/personal-pm-setup` to create it interactively — it finds your Atlassian identity, asks which projects to link, verifies access, and writes the config.

```
~/personal-pm/
├── .pm-config.json          ← role: personal, linked_projects: [...]
└── dashboard/
    ├── 2026-06-17_dashboard.md
    ├── 2026-06-24_dashboard.md
    └── ...
```

---

## 3. Baseline lane — starting a project

Run once when starting a new project. Each step builds on the previous one.

### Step 1: Questionnaire

```
/project-owner-questionnaire
```

Generates `project/empty_questionnaire.md` with questions about scope, stakeholders, budget, timeline, and constraints. Fill it in and save as `project/filled_questionnaire.md` (or run the skill interactively — it will guide you).

**Output:** `project/filled_questionnaire.md`

### Step 2: Project plan

```
/questionnaire-project-plan
```

Reads `project/filled_questionnaire.md` and produces a detailed project plan with work packages, tasks, milestones, owners, and estimated durations.

**Output:** `project/project_plan.md`

### Step 3: Gantt chart and Excel workbook

```
/gantt-chart-creator
```

Reads `project/project_plan.md` and produces:
- `project/gantt_chart.md` — visual Gantt in Markdown
- `project/gantt_chart.xlsx` — Excel workbook with full task table
- `project/gantt_tasks.csv` — CSV used by Jira sync

**Output:** `project/gantt_chart.md`, `project/gantt_chart.xlsx`, `project/gantt_tasks.csv`

### Step 4: Intro slide deck

```
/project-intro-slide-deck
```

Reads `project/project_plan.md` and `project/gantt_chart.xlsx` and generates an intro presentation.

**Output:** `project/project_intro_deck.pptx`

### Step 5: Jira sync

```
/jira-project-sync
```

Reads `project/gantt_tasks.csv` and `.pm-config.json`. Creates Jira issues for every task:
- One Epic per work package
- One Story per regular task (with `originalEstimate` set from plan duration)
- One Task per milestone (labelled `milestone`, due date set)
- One Task labelled `pm-status` for status broadcasts

All issue keys are stored in `project/jira_sync.json` — re-running the skill updates existing issues rather than creating duplicates.

**Output:** `project/jira_sync.json`

---

## 4. Lane A — making changes and replanning

Use Lane A when the project plan needs to change — scope changes, budget revisions, timeline shifts, owner decisions. Lane A always creates new timestamped files. It never modifies the active `project/project_plan.md` or any existing artifacts.

### Trigger

Place the change source (email, meeting notes, owner decision) into `updates/`:

```
updates/
└── 2026-07-01_scope_change_email.md
```

### Step 1: Intake

```
/project-update-intake
```

Reads all files in `updates/` and consolidates them into a single structured summary.

**Output:** `project/update.md`

### Step 2: Clarifier

```
/project-update-clarifier
```

Reviews `project/update.md` and asks clarifying questions: what tasks are affected, who approved the change, what is the rationale, what is the impact. Produces a clarification log once all items are confirmed.

**Output:** `project/update_clarification_log.md`

### Step 3: Replan snapshot

```
/project-replan-snapshot-builder
```

Builds a new timestamped plan incorporating the approved changes.

**Output:**
- `replans/YYYY-MM-DDTHHMMSS_project_plan.md` — new plan snapshot
- `replans/YYYY-MM-DDTHHMMSS_manifest.md` — what changed and why

### Step 4: Artifact snapshots

```
/project-replan-artifact-snapshot-builder
```

Builds timestamped Excel workbook, Gantt chart, and replan deck from the snapshot plan.

**Output:**
- `replans/YYYY-MM-DDTHHMMSS_gantt_chart.md`
- `replans/YYYY-MM-DDTHHMMSS_gantt_tasks.xlsx`
- `replans/YYYY-MM-DDTHHMMSS_replan_deck.pptx`

### Step 5: Archive source files

```
/project-update-archiver
```

Moves the processed source files from `updates/` to `archive/` to keep the folder clean.

**Output:** Files moved to `archive/`

### Step 6: Sync Jira

```
/jira-project-sync
```

Re-run after every replan. Updates existing Jira issues to match the new plan. Tasks removed from the plan get an audit comment — they are never deleted.

---

## 5. Lane B — progress tracking

Run weekly (or daily during active phases). Lane B appends and creates — it never overwrites existing artifacts.

### Input preparation

Place evidence in `progress_inputs/` before running:
- Meeting notes
- Status update emails
- Completed work descriptions
- Any blocker notes

```
progress_inputs/
├── 2026-06-17_standup_notes.md
└── 2026-06-17_completed_tasks.md
```

### Step 1: Progress capture

```
/repo-progress-capture
```

Reads `progress_inputs/` files and recent git commits to produce a consolidated progress summary.

**Output:** `project/progress_update.md`

### Step 2: Clarifier

```
/progress-update-clarifier
```

Reviews `project/progress_update.md` and asks for confirmation on:
- Completion dates and owners
- Any blocked tasks
- Items that may require a plan change (flagged for Lane A consideration)

Produces a clarification log. Items that cross into change-control territory are flagged but do not automatically trigger a replan — the owner must explicitly request that.

**Output:** `project/progress_clarification_log.md`

### Step 3: Effort vs actuals (optional but recommended)

```
/jira-progress-pull
```

Reads `project/jira_sync.json` for all task Jira keys, calls Jira for each task's `originalEstimate` and worklog totals, and produces a comparison table.

**Output:** `project/effort_vs_actuals.md`

### Step 4: Update artifacts (run any or all)

```
/progress-plan-log-appender
```
Appends a new `## YYYY-MM-DD` dated entry to `project/project_plan.md`. All existing content is preserved.

```
/progress-excel-snapshot
```
Adds a new `YYYY-MM-DD` worksheet to `project/gantt_chart.xlsx`. All existing worksheets are preserved.

```
/progress-slide-deck-creator
```
Creates a new dated progress presentation. Previous progress decks are untouched.

**Output:** `progress_reports/YYYY-MM-DD_progress_deck.pptx`

### Step 5: Status broadcast

```
/pm-status-broadcast
```

Reads `project/progress_clarification_log.md` and `project/effort_vs_actuals.md`, builds a structured JSON status block, and overwrites the description of the Jira pm-status ticket for this project.

The status block contains: % complete, current phase, RAG status (green/amber/red), next milestone, open risks, delays, and effort variance. Personal PM reads this ticket to build the cross-project dashboard.

**Output:** Jira pm-status ticket description updated

---

## 6. Jira integration

### Issue hierarchy

```
gantt_tasks.csv                   Jira
────────────────────────────────  ──────────────────────────────────
Work Package (e.g. Discovery)  →  Epic
  Task (e.g. Interviews)       →    Story  (linked to Epic, estimate set)
Milestone (e.g. Phase 1 done)  →  Task   (label: milestone, due date set)
[auto-created]                 →  Task   (label: pm-status, for status broadcasts)
```

### Estimation

Duration in `gantt_tasks.csv` (business days) is converted to Jira `originalEstimate` in seconds:

```
1 business day = 8 hours = 28800 seconds
```

### jira_sync.json

Every Jira issue key created by the plugin is stored in `project/jira_sync.json`. This is the deduplication registry — re-running `/jira-project-sync` updates existing issues rather than creating new ones. Never delete this file unless you want to re-create all issues from scratch.

### Replan behaviour

When `/jira-project-sync` runs after a replan:
- Tasks still in the plan → Jira issue updated (summary, estimate, due date)
- Tasks removed from the plan → Jira issue receives an audit comment; the issue is kept (never deleted)
- New tasks → new Jira issues created

### pm-status sentinel format

The pm-status ticket description follows a machine-readable format so Personal PM can parse it reliably:

```
<!-- pm-status-v1 -->
```json
{ "schema_version": "1.0", "rag_status": "amber", ... }
```
```

If you ever edit the pm-status ticket description manually, preserve the `<!-- pm-status-v1 -->` sentinel line and the JSON block that follows it.

---

## 7. Personal PM dashboard

### Setup

```bash
mkdir ~/personal-pm && cd ~/personal-pm
/personal-pm-setup
```

The skill finds your Atlassian identity automatically, shows you which Jira sites you have access to, and asks which project keys to link. It verifies access to each project before writing the config.

To add more projects later: run `/personal-pm-setup` again (choose option A — add more projects), or edit `.pm-config.json` directly.

### Generating the dashboard

```
/personal-pm-dashboard
```

Reads pm-status tickets from all linked projects, queries Jira for your open tasks across all projects, and generates `dashboard/YYYY-MM-DD_dashboard.md`.

### Dashboard sections

| Section | What it shows |
|---------|--------------|
| Portfolio overview | % complete, current phase, RAG status, next milestone per project |
| Projects needing attention | All Red and Amber projects with risk/delay details |
| My tasks | All open Jira issues assigned to you, sorted by due date |
| Cross-project effort vs actuals | Estimated vs logged hours, variance per project |
| Risks & delays | Consolidated risk and delay list across all projects |
| Data freshness | When each project's pm-status was last updated |

### RAG status

| Status | Meaning |
|--------|---------|
| Green | On track, no blockers |
| Amber | Unresolved items or minor risks — watch closely |
| Red | Blocked, significant delay, or change-control item — needs attention |

---

## 8. File reference

### Workspace files (generated)

| File | Created by | Description |
|------|-----------|-------------|
| `project/empty_questionnaire.md` | `/project-owner-questionnaire` | Blank questionnaire template |
| `project/filled_questionnaire.md` | Owner | Completed questionnaire answers |
| `project/project_plan.md` | `/questionnaire-project-plan` | Master project plan (appended by Lane B) |
| `project/gantt_chart.md` | `/gantt-chart-creator` | Gantt chart in Markdown |
| `project/gantt_chart.xlsx` | `/gantt-chart-creator` | Excel workbook (new sheets added by Lane B) |
| `project/gantt_tasks.csv` | `/gantt-chart-creator` | Task CSV used by Jira sync |
| `project/project_intro_deck.pptx` | `/project-intro-slide-deck` | Intro presentation |
| `project/jira_sync.json` | `/jira-project-sync` | Jira issue ID registry |
| `project/update.md` | `/project-update-intake` | Consolidated change summary |
| `project/update_clarification_log.md` | `/project-update-clarifier` | Clarified change record |
| `project/progress_update.md` | `/repo-progress-capture` | Progress summary |
| `project/progress_clarification_log.md` | `/progress-update-clarifier` | Confirmed progress record |
| `project/effort_vs_actuals.md` | `/jira-progress-pull` | Jira estimate vs logged hours |
| `replans/<ts>_project_plan.md` | `/project-replan-snapshot-builder` | Timestamped plan snapshot |
| `replans/<ts>_manifest.md` | `/project-replan-snapshot-builder` | What changed and why |
| `progress_reports/YYYY-MM-DD_progress_deck.pptx` | `/progress-slide-deck-creator` | Dated progress presentation |
| `dashboard/YYYY-MM-DD_dashboard.md` | `/personal-pm-dashboard` | Cross-project dashboard |

### Config files (you create)

| File | Location | Description |
|------|---------|-------------|
| `.pm-config.json` (project) | Project workspace root | `role: project`, Jira key, cloud ID, owner |
| `.pm-config.json` (personal) | Personal workspace root | `role: personal`, linked_projects list |

---

## 9. Troubleshooting

### "Run /jira-project-sync first"

Any Jira skill that reads `project/jira_sync.json` will stop if the file is missing. Run `/jira-project-sync` to create it, then retry.

### Jira skill says "not authenticated"

Run the Atlassian auth flow in Claude Code. You only need to do this once per machine.

### Progress deck or plan entry is missing data

Make sure `project/progress_clarification_log.md` exists. It is required by `/pm-status-broadcast`, `/progress-plan-log-appender`, and `/progress-slide-deck-creator`. If it is missing, run `/progress-update-clarifier` first.

### Personal dashboard shows "No pm-status data" for a project

The project workspace hasn't run `/pm-status-broadcast` yet, or it hasn't completed a full Lane B cycle. Open that project workspace and run:

```
/progress-update-clarifier   (if progress_clarification_log.md is missing)
/pm-status-broadcast
```

### jira_sync.json is out of date after a replan

After every `/project-replan-snapshot-builder` + `/project-replan-artifact-snapshot-builder` run, always follow up with `/jira-project-sync`. The skill reads the latest `gantt_tasks.csv` and reconciles Jira — updating changed tasks and commenting on removed ones.

### "Issue not found in Jira" in effort_vs_actuals.md

The Jira issue was deleted manually outside of the plugin. The plugin never deletes issues itself. Note the affected task and continue — the row will show `0h` actual and the note. You can re-create the issue by running `/jira-project-sync` (it will create a new issue for any task ID not found in jira_sync.json).

### Partial worklog warning

Jira returns a maximum of 20 worklogs per request. If a task has more than 20 time entries, `effort_vs_actuals.md` will note "Partial worklog — Jira returned first 20 entries only." The actual hours shown are an undercount. For accuracy, consolidate worklogs in Jira or treat the number as a minimum.

### Lane A replan file accidentally created from Lane B

This requires the exact phrase `YES CREATE REPLAN FILE` from the owner. If this was entered by mistake, delete the file created in `updates/replan_from_progress_YYYY-MM-DD.md` before running `/project-update-intake`.
