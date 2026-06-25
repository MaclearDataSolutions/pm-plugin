# Personal PM vs Project PM — Discussion Notes

## What they are

**Project PM** (`role: "project"` in `.pm-config.json`)
- One workspace per project, in any directory
- Runs all three lanes: baseline setup → Lane A (replan) → Lane B (progress tracking)
- Manages local artifacts: `project_plan.md`, Gantt chart, Excel, slide decks
- Syncs tasks into Jira via `/jira-project-sync`

**Personal PM** (`role: "personal"` in `.pm-config.json`)
- One standalone directory (e.g. `~/personal-pm`)
- No local project files — reads only from Jira
- Cross-project view: aggregates pm-status tickets from every project in `linked_projects`
- Shows RAG per project, your assigned tasks across all projects, effort vs actuals, risks/delays

## Where they live

Both are **user-created directories** on your machine — not inside the plugin source repo. The plugin provides the skills; you create the workspaces wherever you want.

```
~/my-project/          ← project workspace (one per project)
├── .pm-config.json    role: "project"
└── project/

~/personal-pm/         ← personal workspace (one total)
├── .pm-config.json    role: "personal", linked_projects: [...]
└── dashboard/
```

## How they communicate

Jira is the only communication channel — no direct file sharing between workspaces.

```
Project workspace (Lane B)
    /pm-status-broadcast  →  writes JSON blob to Jira pm-status ticket

Personal workspace
    /personal-pm-dashboard  →  reads those tickets → unified dashboard
```

The personal dashboard is always one progress-run stale — it reflects whatever the last `/pm-status-broadcast` wrote.

## Known gap: role enforcement is one-directional

`/personal-pm-dashboard` checks `role` and stops if it is `"project"`. Project skills do **not** check `role` — they run based on whether the expected files exist. Running a project skill in a personal workspace succeeds if the files are there.

Fix (not yet implemented): add a role guard to the top of every project skill's Workflow section.

## Considered: blurring the line

Options discussed but deferred — keeping personal/project distinction as-is for now:

- **A — One directory does both:** Project workspace also runs `/personal-pm-dashboard` with a `linked_projects` entry in the config.
- **B — Drop the config role entirely:** Skills run based on files present, no declared mode.
- **C — One config, all features:** Config has both `jira_project_key` (this project) and `linked_projects` (dashboard). Full project workflow plus cross-project view from one place.

The core tension: personal dashboard is read-only from Jira across many projects; project skills write local files for one project. They don't conflict — they serve different needs from different contexts.
