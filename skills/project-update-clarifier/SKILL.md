---
name: project-update-clarifier
description: Clarify Lane A change requests before a replan snapshot is created. Use after project-update-intake has produced project/update.md, or when the user asks to review update.md for missing scope details, affected task IDs, date rationale, owner confirmations, approval status, budget impact, or dependency effects. This skill must not replan the project, must not modify project_plan.md, and must not create or modify any Excel, Gantt, or deck artifacts.
argument-hint: [update.md path]
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash
---

# Project Update Clarifier

Clarify Lane A change requests before replanning. This skill is for change control, not progress tracking.

## Inputs

Default input:

- `project/update.md`

If the user passes an argument, use that file instead.

Helpful context, read only when present:

- `project/project_plan.md`
- `project/gantt_tasks.csv`
- `project/update_sources_manifest.json`
- `project/update_conflict_log.md`

## Outputs

Create or update:

- `project/update.md` (after answers are received — update in place)
- `project/update_clarification_questions.md`
- `project/update_clarification_log.md`

## Hard boundary

This skill clarifies change intent only. Do not:

- Modify `project_plan.md`
- Create replan snapshots
- Update `gantt_tasks.csv`, Excel workbooks, or slide decks
- Begin replanning or impact analysis

If a change item is already clear and confirmed, record it and move on. Do not ask unnecessary questions.

## Workflow

1. Read `update.md` completely.
2. Read `project_plan.md` and `gantt_tasks.csv` for context on current task IDs, dates, owners, and dependencies.
3. Identify missing, vague, or conflicting information that would block a clean replan.
4. Produce `update_clarification_questions.md` with focused questions grouped by priority.
5. Ask the user for answers in the chat.
6. After answers are provided, update `update.md` in place — preserve the original structure and wording where possible.
7. Create `update_clarification_log.md` summarising what was clarified, what remains open, and whether the update is ready for the replan snapshot builder.

## What to clarify

Ask only practical, answerable questions about the change itself. Prioritise:

- **Change scope**: Is this a scope change, schedule change, resource change, budget change, dependency change, or a combination? Be specific about which type applies.
- **Affected task IDs**: Which tasks from the current plan are directly affected? Reference task IDs from `gantt_tasks.csv` where possible.
- **New dates**: Are the new dates hard deadlines or estimates? What caused the date to change?
- **Owner or resource changes**: Is the new owner confirmed and available? Has their time been committed?
- **Dependency effects**: Does this change shift any downstream tasks or milestones beyond the directly affected ones?
- **Approval status**: Has this change been approved by the owner or decision-maker? Who approved it and when?
- **Budget or cost impact**: Does this change affect cost or time budget? Has that been acknowledged?
- **Rationale**: Why is this change happening? This is needed for the change impact document.
- **Scope boundary**: Is this a scope expansion, a scope correction, or a scope reduction?
- **Conflicts with current plan**: Does this change conflict with a constraint, assumption, or risk already documented in the plan?

## Question format

Use this structure in `update_clarification_questions.md`:

```markdown
# Update Clarification Questions

Source file: project/update.md
Clarification status: Waiting for answers

## High-priority questions

1. [Question]
   - Why this matters: [short reason]
   - Affects: replan plan snapshot / Excel snapshot / replan deck

## Medium-priority questions

...

## Items that need owner approval before replan

- [Change item requiring sign-off]
```

Do not ask broad questions like "Anything else to add?" unless all required change fields are already clear.

## Updating update.md after answers

Before editing, create a backup:

- `project/update_backup_YYYY-MM-DD_HHMMSS.md`

Then update `update.md` with confirmed answers. Keep unresolved items clearly marked as:

- `Not confirmed`
- `TBD`
- `Pending owner approval`

Do not invent dates, owners, task IDs, budgets, approvals, or scope decisions.

## Readiness decision

At the end of `update_clarification_log.md`, set one of:

- `Ready for replan` — all required fields confirmed; proceed to `project-replan-snapshot-builder`
- `Ready with open items` — minor gaps remain but replan can proceed; open items noted in plan snapshot
- `Not ready — clarification required` — key fields missing; do not proceed until resolved
- `Needs owner approval` — change is clear but requires explicit sign-off before a replan snapshot is created

If status is `Needs owner approval`, do not continue to the replan snapshot builder until approval is confirmed and recorded in `update.md`.
