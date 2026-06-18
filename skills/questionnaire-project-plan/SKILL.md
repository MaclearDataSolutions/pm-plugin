---
name: questionnaire-project-plan
description: use this skill in claude code when the user needs to turn an owner-completed project questionnaire into a detailed project_plan.md for project management, gantt chart preparation, work breakdown structure, milestone planning, dependencies, resource planning, risk planning, communication planning, budget notes, approvals, task flow, task-level resource requirements, and open planning questions. use when files such as empty_questionnaire.md, filled_questionnaire.md, or owner questionnaire answers are present and the user asks to create a project plan, planning document, gantt-ready plan, schedule basis, or wbs.
---

# Questionnaire Project Plan

Create a practical, detailed `project_plan.md` from an owner-completed questionnaire.

## Source file priority

1. Use the file the user names explicitly.
2. If the user does not name a file, prefer `project/filled_questionnaire.md` when it exists.
3. Otherwise use `project/empty_questionnaire.md` when it exists, assuming the owner filled answers into it.
4. If both files are missing, ask the user to provide or create a completed questionnaire first.

## Main workflow

1. Read the questionnaire completely.
2. Extract only information supported by the questionnaire text.
3. Identify missing, blank, vague, or contradictory answers.
4. Build a realistic project plan for execution and Gantt chart preparation.
5. Save the result as `project/project_plan.md` unless the user asks for another location.
6. Do not overwrite an existing `project/project_plan.md` without telling the user what will change, unless the user explicitly asked to regenerate it.

## Critical rules

- Do not invent owner decisions, budgets, dates, approvers, vendors, permits, or fixed deadlines.
- If information is missing, write `Not provided`, `TBD`, or `Planning assumption` clearly.
- You may create planning assumptions only when needed to make a useful first draft. Mark every assumption as `Planning assumption` and list it again in the assumptions section.
- Distinguish facts from estimates.
- For Gantt planning, translate owner answers into concrete tasks, milestones, dependencies, owners/roles, durations, constraints, progress defaults, status defaults, and task-level resource requirements.
- Prefer specific, practical language over abstract project-management language.
- Do not make the plan look more certain than the questionnaire supports.

## What `project_plan.md` must include

Use this structure unless the user asks for a different format:

```markdown
# Project Plan: [Project Name]

## 1. Executive summary
[Plain-language overview of the project, purpose, main deliverables, timeline pressure, and major planning risks.]

## 2. Source and confidence
- Source file reviewed: `[filename]`
- Date prepared: [today if known, otherwise omit]
- Planning confidence: High / Medium / Low
- Reason for confidence rating: [short explanation]

## 3. Project identity and governance
| Item | Details |
|---|---|
| Project name | ... |
| Project owner / sponsor | ... |
| Final decision-maker | ... |
| Day-to-day contact | ... |
| Final approver | ... |
| Change approver | ... |
| Budget approver | ... |

## 4. Business purpose and success criteria
### Business problem
...

### Success criteria
| Success criterion | How it will be checked | Owner / approver |
|---|---|---|
| ... | ... | ... |

## 5. Scope
### In scope
- ...

### Out of scope
- ...

### Must-have requirements
- ...

### Nice-to-have items
- ...

## 6. Deliverables and acceptance criteria
| Deliverable | Description | Acceptance criteria | Approver | Notes |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## 7. Milestones
| Milestone | Target date | Dependency | Approval needed | Notes |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## 8. Work breakdown structure
| WBS ID | Work package | Description | Deliverable supported |
|---|---|---|---|
| 1.0 | Project initiation and planning | ... | ... |

## 9. Project flow and execution sequence
| Step | Task / phase | Must happen after | Output / handoff |
|---:|---|---|---|
| 1 | ... | ... | ... |

## 10. Basic Gantt planning elements
| Element | What it shows for this project | Source / planning note |
|---|---|---|
| Task list | Activities, deliverables, or work packages | Use WBS and Gantt-ready task list |
| Timeline | Days, weeks, months, or quarters across the top | Use start date, deadline, and important dates |
| Bars | Each task’s start date, duration, and end date | Estimate during Gantt chart step |
| Milestones | Key deadlines or decision points | Use approvals, reviews, fixed dates, and handoffs |
| Dependencies | Which tasks must happen before others | Use predecessor task IDs and owner-provided order |
| Progress | How much of each task is complete | Default to 0% unless provided |
| Owner | Person or team responsible for each task | Use owner, team, vendor, or role |
| Status | On track, at risk, delayed, complete | Default to Not started; mark At risk when data is missing |

## 11. Task and resource requirements
| Task ID | Task | Task description | Inputs needed | Resource requirement | Output | Owner / role | Dependency |
|---|---|---|---|---|---|---|---|
| T1 | ... | ... | ... | ... | ... | ... | ... |

## 12. Gantt-ready task list
| Task ID | Task | Work package | Owner / role | Estimated duration | Depends on | Earliest start / constraint | Output | Progress | Status | Notes |
|---|---|---|---|---:|---|---|---|---:|---|---|
| T1 | ... | ... | ... | ... | ... | ... | ... | 0% | Not started | ... |

## 13. Dependency notes
- Finish-to-start dependencies: ...
- Tasks that can run in parallel: ...
- External dependencies: ...
- Approval gates: ...

## 14. Resource plan
| Resource / role | Person or vendor | Responsibilities | Availability / constraint | Planning risk |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## 15. Budget and procurement notes
| Item | Budget / cost information | Approval rule | Timing impact | Notes |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## 16. Risk register
| Risk ID | Risk | Cause | Impact | Probability | Severity | Response / mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R1 | ... | ... | ... | Low/Med/High | Low/Med/High | ... | ... |

## 17. Communication plan
| Audience | Information needed | Format / channel | Frequency | Sender / owner |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## 18. Change control
- Scope changes: ...
- Schedule changes: ...
- Budget changes: ...
- Approval process: ...

## 19. Assumptions and constraints
### Confirmed constraints
- ...

### Planning assumptions
- ...

## 20. Open questions before final Gantt chart
| Priority | Question | Why it matters for the Gantt chart | Who should answer |
|---|---|---|---|
| High | ... | ... | ... |

## 21. Recommended next steps
1. Confirm missing dates, owners, and approvals.
2. Review the Gantt-ready task list with the owner.
3. Convert tasks into the Gantt chart after dependencies and durations are approved.
```

## Planning logic

When building the work breakdown structure and task list:

1. Convert each deliverable into one or more work packages.
2. Add normal planning and control work packages when relevant:
   - project kickoff and planning
   - requirements confirmation
   - design or solution definition
   - procurement / vendor coordination
   - execution / build / implementation
   - review and quality check
   - owner approval
   - handover / closeout
3. Use owner-provided dates first.
4. If dates are not provided, leave dates as `TBD` and use relative sequencing through dependencies.
5. Estimate durations only as draft planning estimates when the questionnaire provides enough context. Mark them clearly as estimates.
6. Use `Depends on` values that can be copied into a Gantt tool. Include task owner, task description, resource requirement, progress, and status fields so the later Gantt skill can produce a clear schedule.
7. Add approval gates as separate milestone rows when approval affects timing.
8. Place missing information in `Open questions before final Gantt chart`, not hidden in prose.

## Optional script

A helper script is available at `scripts/create_project_plan.py`.

Use it when you need a fast first draft file from a questionnaire:

```bash
python .claude/skills/questionnaire-project-plan/scripts/create_project_plan.py --input project/empty_questionnaire.md --output project/project_plan.md
```

The script creates a structured draft and marks missing answers. After running it, improve the plan manually using the rules above.

## Quality checklist before finishing

Before presenting the result to the user, verify:

- `project/project_plan.md` exists.
- The plan is based on questionnaire answers.
- Missing information is clearly marked.
- The Gantt-ready task list includes task IDs, task descriptions, owners/roles, durations or TBD, dependencies, outputs, progress, and status.
- Risks include cause, impact, mitigation, and owner where available.
- Open questions are specific enough for the project owner to answer.
- Task and resource requirements are clear enough to support Gantt chart and Excel creation.
