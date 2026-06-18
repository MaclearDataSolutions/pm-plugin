---
name: repo-progress-capture
description: Capture project progress from the repo and a progress_inputs folder to produce a structured progress_update.md ready for progress-update-clarifier. Use at the start of Lane B when the user wants to record a progress snapshot from git commits, modified files, meeting notes, status notes, owner updates, or completed work evidence. This skill reads evidence only — it does not modify project_plan.md, Excel, Gantt, or any planning artifact.
argument-hint: [progress_inputs folder path] [reporting period start date YYYY-MM-DD]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Repo Progress Capture

Collect progress evidence from the repo and the `progress_inputs/` folder and produce a structured `project/progress_update.md` for `progress-update-clarifier`.

This is the Lane B entry point — the equivalent of `project-update-intake` for progress tracking.

## Hard boundary

Read and capture only. Do not:

- Modify `project_plan.md`
- Modify `gantt_tasks.csv`, Excel, or any deck
- Interpret evidence as a plan change — flag those as `Potential change-control items` instead
- Invent progress, completion dates, owners, or decisions not supported by visible evidence

## Inputs

### Primary evidence sources (read in this order)

1. **`progress_inputs/` folder** — owner-provided notes, meeting notes, status emails, completed-work evidence, screenshots, exported reports. If the user names a different folder, use that instead.
2. **Git log** — recent commits since the last progress update date. Use commit messages, changed file paths, and timestamps as progress signals.
3. **Repo files** — recently modified files that correspond to deliverables or tasks in the plan.

### Context files (read-only reference)

- `project/project_plan.md` — for task list, milestones, and the last `# Progress Update Log` entry date
- `project/gantt_tasks.csv` — for canonical task IDs, owners, statuses, progress percentages, and due dates
- `project/progress_sources_manifest.json` — if present, use the last update date to set the reporting period start

## Outputs

- `project/progress_update.md` — structured progress snapshot, ready for `progress-update-clarifier`
- `project/progress_sources_manifest.json` — inventory of all sources reviewed and what each contributed

## Reporting period

Determine the reporting period start date using this priority:

1. Date passed as an argument by the user.
2. Date of the most recent `## YYYY-MM-DD` entry in `project/project_plan.md` under `# Progress Update Log`.
3. Date of the last run recorded in `project/progress_sources_manifest.json`.
4. If none of the above exist, use the project start date from the plan, and note it as a planning assumption.

Reporting period end = today's date.

## Workflow

1. Determine the reporting period.
2. Scan `progress_inputs/` — list all files, read each one, extract progress facts.
3. Scan git log for commits since the reporting period start:
   ```bash
   git log --oneline --since="YYYY-MM-DD" --name-only
   ```
4. Cross-reference changed files with task deliverables in `gantt_tasks.csv`.
5. Read the last progress log entry in `project_plan.md` to avoid re-reporting already-confirmed items.
6. Consolidate all evidence into `progress_update.md` using the structure below.
7. Write `progress_sources_manifest.json`.

## progress_update.md structure

```markdown
# Progress Update

Update date: YYYY-MM-DD
Reporting period: YYYY-MM-DD to YYYY-MM-DD
Capture method: repo-progress-capture
Capture status: Draft — awaiting clarification

## Update summary
[2–4 sentence plain-language summary of overall progress this period]

## Completed since last update
| Task ID | Task | Completed date | Evidence | Notes |
|---|---|---|---|---|
| T1 | ... | YYYY-MM-DD | git commit abc1234 / progress_inputs/file.md | ... |

## In progress
| Task ID | Task | Owner | Reported progress | Evidence | Notes |
|---|---|---|---|---|---|
| T2 | ... | ... | 50% | ... | ... |

## Blocked or delayed
| Task ID | Task | Blocker description | Owner | First noticed | Notes |
|---|---|---|---|---|---|

## Risks and issues
- [Risk or issue observed this period — include source]

## Decisions made
- [Decision observed in meeting notes or owner messages — include source]

## Next actions observed
- [Action] — Owner: [name or Unknown] — Due: [date or Unknown] — Source: [file]

## Potential change-control items
- [Item that looks like a scope, schedule, or resource change rather than progress — flag for Lane A if confirmed]

## Source evidence log
| Source | Type | Date | What it contributed |
|---|---|---|---|
| progress_inputs/meeting_notes.md | Meeting notes | YYYY-MM-DD | Confirmed T4 complete; T7 delayed |
| git commit abc1234 | Commit | YYYY-MM-DD | Modified project/gantt_chart.md — T3 likely done |
| gantt_tasks.csv | Plan file | — | Baseline task status for comparison |

## Unreadable or skipped files
- [File and reason it was skipped]
```

## Evidence interpretation rules

- A git commit that modifies a deliverable file is **weak evidence** of task completion — mark as `Inferred from commit, confirm`.
- An owner note that explicitly says "done" or "complete" is **strong evidence** — mark as `Confirmed by owner note`.
- A commit message alone without a corresponding file change is **informational only**.
- If a task's reported progress in `gantt_tasks.csv` differs from evidence, note the discrepancy — do not resolve it here; let `progress-update-clarifier` handle it.
- If a change looks like a scope, date, or resource shift (not just progress), flag it as a `Potential change-control item` — do not treat it as progress.

## progress_sources_manifest.json structure

```json
{
  "capture_id": "YYYY-MM-DD_HHMM-progress-capture",
  "update_date": "YYYY-MM-DD",
  "reporting_period_start": "YYYY-MM-DD",
  "reporting_period_end": "YYYY-MM-DD",
  "progress_inputs_folder": "progress_inputs",
  "files_reviewed": [
    {
      "path": "progress_inputs/meeting_notes.md",
      "type": "meeting_notes",
      "modified": "YYYY-MM-DD",
      "contributed": "Confirmed T4 complete"
    }
  ],
  "git_commits_reviewed": [
    {
      "hash": "abc1234",
      "date": "YYYY-MM-DD",
      "message": "...",
      "files_changed": [],
      "contributed": "Evidence of T3 deliverable modified"
    }
  ],
  "files_skipped": [],
  "output_file": "project/progress_update.md"
}
```

## Final response

Report:
- reporting period covered
- number of `progress_inputs/` files reviewed
- number of git commits reviewed
- number of tasks with new progress evidence
- number of potential change-control items flagged
- whether `progress-update-clarifier` should run next
