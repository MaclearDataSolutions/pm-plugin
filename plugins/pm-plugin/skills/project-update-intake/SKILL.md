---
name: project-update-intake
description: use this skill in claude code when the user stores project update notes, emails, meeting notes, owner comments, revised assumptions, vendor updates, schedule changes, scope changes, budget changes, or resource changes in a folder and wants claude to review the folder before updating a project plan. this skill inventories all files in the update folder, consolidates the updates, resolves conflicts by using the most recently modified source as authoritative, and creates update.md as the input for the project-plan-updater skill.
---

# Project Update Intake

Review a folder of project update files and create one consolidated `update.md` file for the project plan update workflow.

This skill runs before `project-plan-updater`.

## Expected input

Use the folder named by the user. If no folder is named, look for these folders in this order:

1. `updates/`
2. `Updates/`
3. `Project_Updates/`
4. `project_updates/`
5. `Change_Requests/`
6. `change_requests/`

If none exists, ask the user for the update folder path.

## Required outputs

Create these files in the `project/` folder unless the user asks for another location:

- `project/update.md` - consolidated, conflict-resolved update file for `project-plan-updater`
- `project/update_conflict_log.md` - record of conflicts, overridden older information, and unresolved items
- `project/update_sources_manifest.json` - machine-readable source inventory and resolution notes

## Core rule for conflicts

When multiple update files conflict, use the newest source as the accurate one.

Newest source means:

1. Prefer filesystem modified time from `stat` or equivalent.
2. If modified time is unavailable, use explicit dates inside the file content.
3. If both are unavailable or tied, do not choose silently. Mark the item as `Needs confirmation`.

Always document which older source was overridden and why.

## Workflow

### 1. Inventory the update folder

List all files recursively. Exclude:

- hidden system files such as `.DS_Store`
- temporary files such as `~$file.docx`
- build/cache folders such as `.git`, `node_modules`, `.venv`, `__pycache__`
- generated output from previous runs unless the user explicitly asks to include it

For each included file, capture:

- relative path
- file type/extension
- modified timestamp
- size
- whether it was read successfully
- notes if unreadable or skipped

### 2. Read the update content

Read every supported file as far as practical.

Handle common formats:

- `.md`, `.txt`, `.csv`, `.json`, `.yaml`, `.yml` directly
- `.docx`, `.xlsx`, `.pdf`, `.pptx` using available project tools or by generating a temporary extraction script when needed
- images only if the user specifically says the image contains update information; otherwise list as attachment/reference

Do not silently ignore a file that appears relevant. If it cannot be read, list it in `update_conflict_log.md` and `update.md` under unreadable files.

### 3. Extract atomic update facts

Break the folder contents into specific update facts. Classify each fact as one or more of:

- scope change
- deliverable change
- schedule change
- milestone change
- dependency change
- resource or owner change
- budget or procurement change
- risk or constraint change
- approval or governance change
- communication/reporting change
- clarification only
- cancellation/removal
- open question

Each extracted fact should include:

- what changed
- old value if stated
- new value if stated
- affected task, milestone, deliverable, section, person, vendor, budget item, risk, or dependency if identifiable
- source file
- source timestamp
- confidence level: high / medium / low

### 4. Resolve conflicts

A conflict exists when two or more files say different things about the same planning item, for example:

- different dates for the same milestone
- different owners for the same task
- different budget amounts for the same work
- one file adds scope while another removes it
- dependencies contradict each other
- an older file says a risk is closed but a newer file says it is active

Resolve each conflict using the newest source rule. Record the selected value and overridden values.

### 5. Create `update.md`

Use the exact structure from `references/update_template.md`.

The `project/update.md` file must be suitable as direct input for `project-plan-updater`. It should not contain every raw note. It should contain the consolidated, conflict-resolved project update plus clear source references.

### 6. Create `update_conflict_log.md`

Include:

- all conflicts found
- selected newest source
- older overridden sources
- unreadable/skipped files
- facts that need owner confirmation
- assumptions made during extraction

### 7. Create `update_sources_manifest.json`

Include source inventory and consolidated update records using this shape:

```json
{
  "update_id": "YYYYMMDD-HHMM-update-intake",
  "source_folder": "updates",
  "conflict_policy": "newest_source_wins_by_modified_time",
  "files_reviewed": [],
  "files_skipped": [],
  "consolidated_updates": [],
  "conflicts_resolved": [],
  "needs_confirmation": [],
  "output_file": "project/update.md"
}
```

Use empty arrays when no items apply. Do not omit keys.

## Do not do

- Do not update `project_plan.md` in this skill.
- Do not update Gantt CSV, Excel, or slide decks in this skill.
- Do not invent project facts not supported by the update folder.
- Do not hide conflicts; resolve them by newest source and document the decision.
- Do not treat file name order as freshness unless file timestamps and content dates are unavailable.

## Final response

Report:

- number of files reviewed
- number of updates extracted
- number of conflicts resolved
- location of `project/update.md`
- whether `project-plan-updater` should run next
