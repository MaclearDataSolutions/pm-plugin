---
name: project-owner-questionnaire
description: use this skill in claude code when the user needs to collect practical project-start information from a company owner, project owner, sponsor, client, or stakeholder before project planning, gantt charting, work breakdown, schedule estimation, resource planning, or risk planning. this skill creates or provides an owner-facing empty questionnaire, collects or reads the owner's answers, and saves a structured filled_questionnaire.md without inventing missing information.
---

# Project Owner Questionnaire

Use this workflow to collect concrete project information from an owner and save it for later Gantt chart planning.

## Core files

- `assets/empty_questionnaire.md`: owner-facing blank questionnaire.
- `scripts/create_empty_questionnaire.sh`: copies the blank questionnaire into the current project as `project/empty_questionnaire.md`.
- `project/filled_questionnaire.md`: final structured answer file to create after answers are available.

## Workflow

1. Determine the working directory.
   - If the user gives a folder path, use it.
   - Otherwise use the current repository or current working directory.

2. Create or provide the empty questionnaire.
   - If the user asks to start, prepare, send, or create the questionnaire, create `project/empty_questionnaire.md` from `assets/empty_questionnaire.md`.
   - Prefer running:
     ```bash
     bash "${CLAUDE_SKILL_DIR}/scripts/create_empty_questionnaire.sh" project
     ```
   - Do not overwrite an existing `project/empty_questionnaire.md` unless the user clearly asks for a fresh copy.

3. Collect answers.
   - Accept answers pasted in chat, written directly into `empty_questionnaire.md`, or provided in another markdown/text file.
   - If answers are in a file, read the file before writing `filled_questionnaire.md`.
   - Do not ask abstract questions. Ask for dates, names, deliverables, constraints, dependencies, resources, approvals, and risks.

4. Save `project/filled_questionnaire.md`.
   - Create or update `project/filled_questionnaire.md` only after answers are available.
   - Preserve the owner's wording where useful, but organize it into the output structure below.
   - Mark missing answers as `not provided`.
   - Do not invent dates, budgets, dependencies, resources, or risks.
   - Add a short `planning gaps` section listing missing information needed before building a Gantt chart.
   - Do not build a Gantt chart unless the user asks for one after `project/filled_questionnaire.md` is saved.

## filled_questionnaire.md structure

Use this structure exactly:

```markdown
# Filled Project Owner Questionnaire

## 1. Project identity
- Project name:
- Company / department:
- Project owner / sponsor:
- Day-to-day contact:
- Final decision-maker:

## 2. Project purpose and success
- Problem or opportunity:
- Practical definition of success:
- Main business value:

## 3. Scope and deliverables
- Main deliverables:
- Included in scope:
- Excluded from scope:
- Must-have requirements:
- Nice-to-have items:

## 4. Dates and milestones
- Preferred start date:
- Fixed deadline:
- Reason for deadline:
- Important dates or events:
- Expected approval dates:

## 5. Work sequence and dependencies
- Tasks that must happen first:
- Tasks that must happen in a specific order:
- Tasks that can happen in parallel:
- External dependencies:

## 6. People and resources
- Internal team members and roles:
- Internal availability constraints:
- External vendors / contractors / suppliers:
- Materials, equipment, software, permits, or access needed:

## 7. Budget and approvals
- Approved budget or range:
- Spending approval rules:
- Budget concerns:
- Who approves budget changes:

## 8. Risks and constraints
- Known risks:
- Assumptions:
- Constraints:
- Decisions not yet made:

## 9. Communication and reporting
- Preferred update frequency:
- Preferred update format:
- People who need updates:
- Escalation contact:

## 10. Completion and acceptance
- Final approver:
- Acceptance criteria:
- Handover / training / closeout needs:

## 11. Planning gaps before Gantt charting
- Gap 1:
- Gap 2:
- Gap 3:
```

## Quality rules

- Keep the questionnaire realistic and owner-friendly.
- Prefer concrete wording over project-management jargon.
- Keep `empty_questionnaire.md` short enough that an owner can complete it in one sitting.
- If an answer is unclear, record it and add a specific follow-up question in `planning gaps`.
- For Gantt readiness, prioritize: deliverables, dates, task order, dependencies, resource names, availability, approvals, vendor lead times, and fixed constraints.
