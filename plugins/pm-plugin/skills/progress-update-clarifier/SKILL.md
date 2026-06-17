---
name: progress-update-clarifier
description: Clarify progress-only status updates before reporting artifacts are created. Use after repo-progress-capture has produced project/progress_update.md, or when the user asks to review progress_update.md for missing dates, completion status, blockers, owners, evidence, risks, issues, decisions, or reporting details. This skill must not replan the project and must not update baseline plan, Excel, Gantt, or slide deck artifacts.
argument-hint: [progress_update.md path]
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash
---

# Progress Update Clarifier

Clarify progress-only updates. This skill is for status reporting, not change control or replanning.

## Inputs

Default input:

- `project/progress_update.md`

If the user passes an argument, use that file instead.

Helpful context, read only when present:

- `project/project_plan.md`
- `project/gantt_tasks.csv`
- `project/progress_sources_manifest.json`
- `project/progress_conflicts.md`
- `progress_inputs/`

## Outputs

Create or update:

- `project/progress_update.md`
- `project/progress_clarification_questions.md`
- `project/progress_clarification_log.md`
## Hard boundary

Progress tracking is append-only and snapshot-based. Do not revise, restructure, overwrite, or regenerate the current approved project plan, existing Excel sheets, original slide deck, previous progress decks, current Gantt baseline, or planning baseline.

If an update implies a plan change, mark it as `Potential change-control item` and tell the user it should go through the change/replan workflow instead of treating it as progress.

## Workflow

1. Read the progress update file.
2. Identify missing or vague information that affects progress reporting only.
3. Produce `progress_clarification_questions.md` with focused questions.
4. Ask the user for answers in the chat.
5. After answers are provided, update `progress_update.md` in place, preserving the original sections and wording where possible.
6. Create `progress_clarification_log.md` summarizing what was clarified, what remains unknown, and whether the update is ready for reporting.

## What to clarify

Ask only practical, answerable questions. Prioritize:

- Update date: what date should this progress snapshot use?
- Completed work: which task or deliverable is completed, and on what date?
- In-progress work: what is actively being worked on now?
- Blockers: what is blocked, who owns the blocker, and what is needed to unblock it?
- Delay vs replan: is the delay only a status note, or does it require replanning?
- Evidence: which file, commit, meeting note, email, or artifact supports the progress claim?
- Owner: who owns each open action?
- Next actions: what must happen next, by whom, and by when?
- Risks/issues: is this a risk, issue, decision, or information-only note?
- Reporting sensitivity: should anything be hidden, softened, or escalated in the progress deck?

## Question format

Use this structure in `progress_clarification_questions.md`:

```markdown
# Progress Clarification Questions

Source file: project/progress_update.md
Clarification status: Waiting for answers

## High-priority questions

1. [Question]
   - Why this matters: [short reason]
   - Affects: progress note / Excel sheet / progress deck

## Medium-priority questions

...

## Items that may require change control

- [Potential plan change]
```

Do not ask broad questions like "Anything else?" unless all required reporting fields are already clear.

## Updating progress_update.md after answers

Before editing, create a backup:

- `project/progress_update_backup_YYYY-MM-DD_HHMMSS.md`
Then update `progress_update.md` with confirmed answers. Keep unresolved items clearly marked as:

- `Not confirmed`
- `TBD`
- `Potential change-control item`

Do not invent missing dates, completion percentages, owners, blockers, or decisions.

## Readiness decision

At the end of `progress_clarification_log.md`, set one of:

- `Ready for progress reporting`
- `Ready with unresolved items`
- `Not ready - clarification required`
- `Needs change-control workflow`

If status is `Needs change-control workflow`, do not continue to Excel or deck update skills.

## Lane A handoff (manual trigger — double confirmation required)

When change-control items are flagged, **do not suggest, offer, or initiate Lane A**. Only list the flagged items clearly in `progress_clarification_log.md` and stop.

Do not:
- Ask the owner if they want a replan
- Offer to create an `updates/` file
- Mention Lane A unless the owner explicitly asks

The owner must come back and explicitly request the handoff themselves. This is intentional — a replan is a significant decision and must not happen by accident.

### When the owner explicitly asks to trigger Lane A

Only proceed if the owner's message clearly and unambiguously requests a replan. Examples of sufficient requests:

- "I want to start a replan based on the flagged items"
- "Create the Lane A update file for these change-control items"
- "Trigger Lane A for [specific item]"

Vague messages such as "what should I do?" or "sounds like things changed" are **not sufficient** — respond with a plain list of flagged items and wait.

### Step 1 — Show a preview, do not act yet

When a sufficient request is received:

1. List exactly which flagged items from `progress_clarification_log.md` will be included.
2. Show a preview of the `updates/` file content that would be created — full text, nothing hidden.
3. State the file path: `updates/replan_from_progress_YYYY-MM-DD.md`
4. End with this exact prompt and nothing else:

   > **To create this file and begin Lane A, reply: YES CREATE REPLAN FILE**
   > Any other reply will cancel.

### Step 2 — Create only on exact confirmation

- If the owner replies with the exact phrase `YES CREATE REPLAN FILE` (case-insensitive), create the file.
- If the owner replies with anything else — including "yes", "ok", "do it", "confirm", "go ahead" — do not create the file. Treat it as a cancel and say: "Replan file not created. Reply 'YES CREATE REPLAN FILE' to proceed."

After creating the file, instruct the owner to run Lane A:
```
project-update-intake → project-update-clarifier → project-replan-snapshot-builder → project-replan-artifact-snapshot-builder
```

### Progress reporting is unaffected

Progress artifacts (plan log, Excel sheet, progress deck) can still be created for items that are not flagged as change-control, even when the overall status is `Needs change-control workflow`.
