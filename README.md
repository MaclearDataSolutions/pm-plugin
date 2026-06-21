# pm-plugin

Private Claude Code plugin for Maclear Data Solutions. Turns a project brief into a full planning suite — questionnaire, project plan, Gantt chart, Excel workbook, slide decks — and keeps it in sync with Jira throughout the project lifecycle.

Two modes, one plugin: **Project PM** manages a single project end-to-end; **Personal PM** gives you a cross-project dashboard across every project you're involved in.

**What syncs to Jira:** Epics, Stories (with start date, due date, time estimate, story points), Subtasks, milestone Tasks, issue links (blocks / is blocked by), and status transitions.

---

## Architecture

```
Personal PM workspace (.pm-config.json → role: personal)
└── Cross-project dashboard, effort vs actuals, my tasks across all projects

Project A workspace  (.pm-config.json → role: project, jira_key: PROJ-A)
└── Full 3-lane PM: plan → Gantt → Excel → deck → Jira sync → progress tracking

Project B workspace  (.pm-config.json → role: project, jira_key: PROJ-B)
└── Same, independent
```

**Communication:** Project PMs write structured status to Jira on every progress run. Personal PM reads across all linked projects and generates a unified dashboard. No direct agent links needed.

---

## Install (team members)

**Prerequisites:** Claude Code installed, member of the `MaclearDataSolutions` GitHub org, Jira/Atlassian account.

### Step 1 — Authenticate with GitHub

```bash
gh auth login
```

Or configure an SSH key or PAT in your git credential store.

### Step 2 — Install the plugin (run once per machine)

```bash

claude plugin marketplace add https://github.com/MaclearDataSolutions/pm-plugin

claude plugin install pm-plugin  

```

### Step 3 — Authenticate Jira

Claude Code's built-in Atlassian auth flow runs automatically on first use of any Jira skill. No tokens to manage manually.

### Step 4 — Set up your personal workspace

Create a new directory for your personal dashboard and run:

```bash
mkdir ~/personal-pm && cd ~/personal-pm
/personal-pm-setup
```

This creates `.pm-config.json`, verifies your Jira project access, and links all your projects.

---

## Jira project setup

Before running `/jira-project-sync` for the first time, check these Jira settings.

### Story Points field

`/gantt-chart-creator` auto-estimates story points (Fibonacci 1–21) for every task. `/jira-project-sync` pushes them to Jira automatically — but the field must exist in your project first.

**Team-managed (next-gen) projects** — Story Points is a native field. Nothing to configure; it works out of the box.

**Company-managed (classic) projects** — Story Points (`customfield_10016`) is created automatically when a Scrum or Kanban board is added to the project. If your project has neither:

1. Go to your Jira project → **Project settings → Issue types → Story**
2. Click the screen name under **Edit fields**
3. Find **Story Points** in the field list and drag it onto the screen
4. Save — then re-run `/jira-project-sync`

> `/jira-project-sync` checks for the Story Points field before syncing. If the field is not found in the project, story points are skipped silently and noted in the sync report. Everything else (epics, tasks, dates, links) still syncs normally.

### Issue link types

`/jira-project-sync` creates **Blocks / Is blocked by** links from the `Depends on` column in the Gantt CSV. These link types exist by default in all Jira projects. If your project uses a custom workflow with renamed link types, the sync report will list what it found so you can investigate.

---

## Quick start — new project

```bash
# 1. Create a project directory
mkdir my-project && cd my-project

# 2. Copy the config template and fill it in
cp "$(claude plugin path pm-plugin)/config-templates/project.pm-config.json" .pm-config.json
# Edit .pm-config.json — set: project_name, jira_project_key, jira_cloud_id, owner

# 3. Run the baseline lane
/project-owner-questionnaire    # collect project details from the owner
/questionnaire-project-plan     # generate project_plan.md
/gantt-chart-creator            # generate Gantt chart, Excel workbook, and CSV
/project-intro-slide-deck       # generate the intro deck

# 4. Push tasks to Jira
/jira-project-sync              # create Epics, Stories, milestone Tasks; writes jira_sync.json
```

---

## Quick start — personal dashboard

```bash
cd ~/personal-pm
/personal-pm-dashboard          # generates dashboard/YYYY-MM-DD_dashboard.md
```

---

## Skill reference

### Baseline lane (project mode)

| Skill | When to run | Output |
|-------|------------|--------|
| `/project-owner-questionnaire` | Once, at project start | `project/empty_questionnaire.md` → `project/filled_questionnaire.md` |
| `/questionnaire-project-plan` | After questionnaire | `project/project_plan.md` |
| `/gantt-chart-creator` | After plan | `project/gantt_chart.md`, `project/gantt_chart.xlsx`, `project/gantt_tasks.csv` (includes auto-estimated story points) |
| `/project-intro-slide-deck` | After Gantt | `project/project_intro_deck.pptx` |
| `/jira-project-sync` | After baseline, and after every replan | `project/jira_sync.json`; creates/updates Jira Epics, Stories (with start date, due date, story points), Subtasks, milestone Tasks, and issue links |

### Lane A — Change / Replan

| Skill | When to run | Output |
|-------|------------|--------|
| `/project-update-intake` | After placing update files in `updates/` | `project/update.md` |
| `/project-update-clarifier` | After intake | `project/update_clarification_log.md` |
| `/project-replan-snapshot-builder` | After clarifier approved | `replans/<ts>_project_plan.md` + manifest |
| `/project-replan-artifact-snapshot-builder` | After snapshot | Timestamped Excel, Gantt, replan deck in `replans/` |
| `/project-update-archiver` | After artifacts built | Moves `updates/` files to `archive/` |

Then run `/jira-project-sync` to push the replanned tasks to Jira.

### Lane B — Progress tracking

| Skill | When to run | Output |
|-------|------------|--------|
| `/repo-progress-capture` | Daily/weekly, after placing notes in `progress_inputs/` | `project/progress_update.md` |
| `/progress-update-clarifier` | After capture | `project/progress_clarification_log.md` |
| `/jira-progress-pull` | After clarifier | `project/effort_vs_actuals.md` |
| `/jira-board-refresh` | After `/progress-update-clarifier` (optional: after `/jira-progress-pull`) | `project/jira_board_refresh.md`; transitions statuses and updates start/due dates |
| `/progress-plan-log-appender` | After clarifier | Appends `## YYYY-MM-DD` entry to `project/project_plan.md` |
| `/progress-excel-snapshot` | After clarifier | Adds `YYYY-MM-DD` worksheet to `project/gantt_chart.xlsx` |
| `/progress-slide-deck-creator` | After clarifier | `progress_reports/YYYY-MM-DD_progress_deck.pptx` |
| `/pm-status-broadcast` | End of Lane B run | Overwrites Jira pm-status ticket description |

### Personal PM

| Skill | When to run | Output |
|-------|------------|--------|
| `/personal-pm-setup` | Once, per personal workspace | `.pm-config.json` |
| `/personal-pm-dashboard` | Any time | `dashboard/YYYY-MM-DD_dashboard.md` |

---

## Config files

**Project workspace — `.pm-config.json`:**

```json
{
  "role": "project",
  "project_name": "Client Onboarding Revamp",
  "jira_project_key": "COR",
  "jira_cloud_id": "your-org.atlassian.net",
  "owner": "harris.yang@maclear.ca"
}
```

**Personal workspace — `.pm-config.json`:**

```json
{
  "role": "personal",
  "user_name": "Harris Yang",
  "user_email": "harris.yang@maclear.ca",
  "linked_projects": [
    { "jira_project_key": "COR", "jira_cloud_id": "your-org.atlassian.net" },
    { "jira_project_key": "INF", "jira_cloud_id": "your-org.atlassian.net" }
  ]
}
```

Starter templates are in `config-templates/` inside the plugin. Copy the right one and fill in your values.

---

## Updating the plugin

```bash
claude plugin update  pm-plugin@maclear-pm-plugin
```

Skills, scripts, and templates update. All `project/` data and `.pm-config.json` files in your workspaces are untouched.

---

## Access control

Access is gated by GitHub org membership. To grant: add the person to `MaclearDataSolutions` org. To revoke: remove them. Their existing local install continues working until their next `plugin update` (when the auth check runs).

---

## Potential next steps

The v1 architecture was designed to make these additions clean — no breaking changes to existing workspaces or skills.

### v2a — Confluence publishing

Project PM already writes to Jira on every Lane B run. Adding Confluence publishing means stakeholders can read project status and dashboards without running Claude Code. The Atlassian MCP already includes `updateConfluencePage` — no new infrastructure required.

```
/pm-status-broadcast  (enhanced)
    ├── v1: writes to Jira pm-status ticket   ← already live
    └── v2: also publishes to Confluence page

/personal-pm-dashboard  (enhanced)
    └── v2: pushes dashboard to personal Confluence page
```

### v2b — Agent-to-agent via MCP server

Personal PM currently reads Jira (one progress cycle stale). A lightweight MCP server per Project PM would give Personal PM real-time live data — current task status, in-progress blockers, live effort numbers — with Jira as the automatic fallback when the server is unreachable.

```
Personal PM → try MCP server for Project A → server responds → live data
                                            → server unreachable → Jira fallback (always fresh)
```

Hosting options: laptop-local for a small team ($0), small VPS at ~$5/month, or serverless (AWS Lambda/Azure Functions) for production use. The plugin already uses the Atlassian MCP pattern — adding a project MCP server follows the same model.

### v2c — Claude Agent SDK orchestration

Anthropic's Agent SDK is designed for multi-agent workflows. Defining Project PM and Personal PM as first-class agents enables structured handoffs — Personal PM delegates a risk clarification to the relevant Project PM, gets a structured response, and incorporates it into the dashboard. This is the cleanest long-term architecture and aligns with where Claude is heading. Complexity is higher today but the SDK is maturing fast.

### v3 — Commercial distribution

The plugin is structured for this: single installable package, GitHub-gated access, config-driven mode switching, no hardcoded org names. To sell externally:
- Move the repo to a public or customer-licensed private repo
- Replace GitHub org gating with a license key check (a small MCP server or webhook)
- Publish to the Claude Code plugin marketplace for discovery
- Version with git tags (`v1.0.0`, `v1.1.0`) for controlled rollout

---

## Full workflow reference

See [MANUAL.md](MANUAL.md) for detailed step-by-step instructions, lane diagrams, and troubleshooting.

See [CLAUDE.md](CLAUDE.md) for the plugin's internal instruction set (read by Claude Code automatically).
