---
name: project-update-archiver
description: use this skill in claude code when the user wants to move project update source files out of an updates folder after the update workflow has been processed. use after project-update-intake, project-plan-updater, and optionally plan-artifact-updater when files such as update_sources_manifest.json, update.md, plan_change_manifest.json, update_conflict_log.md, an Updates folder, or an Archive folder are present. this skill safely archives only the original update files that were reviewed earlier, creates an archive log, avoids moving generated workflow outputs unless explicitly requested, and preserves restore information.
---

# Project Update Archiver

Archive update source files after the project update workflow has been completed.

## Purpose

Move the update files from the selected Updates folder into an Archive folder so the active Updates folder is ready for the next update cycle.

This skill should normally run after:

1. `project-update-intake` created `project/update.md` and `project/update_sources_manifest.json`.
2. `project-plan-updater` updated `project/project_plan.md` and created `project/plan_change_manifest.json`.
3. `plan-artifact-updater` updated Gantt/Excel/slide artifacts, when applicable.

## Source of truth for what to archive

Use this priority order:

1. If the user names specific files or a specific update folder, use that explicit instruction.
2. If `project/update_sources_manifest.json` exists, use it to identify the selected Updates folder and reviewed source files.
3. If no manifest exists, look for the first existing folder from this list:
   - `updates/`
   - `Updates/`
   - `Project_Updates/`
   - `project_updates/`
   - `Change_Requests/`
   - `change_requests/`
4. If no update folder is found, stop and explain what is missing.

## Files to archive

Archive only original update source files from the selected update folder.

Do not archive these generated workflow files unless the user explicitly asks:

- `project/update.md`
- `project/update_conflict_log.md`
- `project/update_sources_manifest.json`
- `project/plan_update_request.md`
- `project/plan_change_impact.md`
- `project/plan_change_manifest.json`
- `project/project_plan.md`
- `project/gantt_tasks.csv`
- `project/gantt_chart.md`
- slide decks, Excel workbooks, or reports created by later workflow steps

If `project/update_sources_manifest.json` lists reviewed source files, archive exactly those files when possible. If a listed file no longer exists, record it as missing in the archive log and continue.

## Archive destination

Default destination:

`archive/updates/YYYY-MM-DD_HHMMSS/`

If the user names a different archive folder, use the requested folder.

Preserve relative paths inside the selected Updates folder. Example:

`updates/client/email_update.md` becomes `archive/updates/2026-05-12_153000/client/email_update.md`.

If a destination file already exists, do not overwrite it. Add a numeric suffix such as `_2`, `_3`, etc.

## Required workflow

1. Identify the selected Updates folder.
2. Identify files to archive.
3. Show a short summary before moving files unless the user already said to archive now.
4. Create the archive destination folder.
5. Move the files, not copy them, unless the user requests copy-only mode.
6. Leave empty source subfolders alone unless the user asks to remove them.
7. Create or update `project/update_archive_log.md` with:
   - run timestamp
   - source folder
   - archive destination
   - files moved
   - files skipped
   - files missing
   - restore instructions
8. Report the final archive location and any skipped/missing files.

## Safety rules

- Never move the entire project folder.
- Never move `.claude/`, `.git/`, `archive/`, or generated project artifacts unless explicitly requested.
- Never delete files permanently.
- Do not overwrite existing archive files.
- If the source folder contains unrelated working files and no manifest exists, ask before archiving everything.
- If the user asks for a dry run, list the files that would be moved but make no changes.

## Helper script

A safe helper script is available at:

`scripts/archive_updates.py`

Use it when the user wants the archival step executed. Example:

```bash
python .claude/skills/project-update-archiver/scripts/archive_updates.py \
  --manifest project/update_sources_manifest.json \
  --archive-root archive \
  --log project/update_archive_log.md
```

Dry run:

```bash
python .claude/skills/project-update-archiver/scripts/archive_updates.py \
  --manifest project/update_sources_manifest.json \
  --archive-root archive \
  --log project/update_archive_log.md \
  --dry-run
```

Fallback without a manifest:

```bash
python .claude/skills/project-update-archiver/scripts/archive_updates.py \
  --updates-folder updates \
  --archive-root archive \
  --log project/update_archive_log.md
```

## Expected user prompts

- "Archive the update files."
- "Move the processed update files from Updates to Archive."
- "Use the update manifest and archive the source update files."
- "Clean up the Updates folder after the plan and artifacts are updated."
