# Project Plan Output Guide

Use this guide only when creating or reviewing `project_plan.md`.

A Gantt-ready project plan should give a scheduler enough information to create tasks, durations, dependencies, milestones, owners, progress, status, and resource requirements.

## Minimum useful planning fields

- Task ID
- Task name
- Task description
- Work package or deliverable supported
- Owner or role
- Resource requirement
- Inputs needed
- Estimated duration, or `TBD`
- Predecessor / dependency
- Start constraint or fixed date, if any
- Output or acceptance result
- Progress, defaulting to `0%` when not provided
- Status, defaulting to `Not started` when not provided
- Notes / uncertainty

## Basic Gantt planning elements

Always include a table that explains how the project plan supports these elements:

| Element | What it shows |
|---|---|
| Task list | The activities, deliverables, or work packages |
| Timeline | Days, weeks, months, or quarters across the top |
| Bars | Each task's start date, duration, and end date |
| Milestones | Key deadlines or decision points, often shown as diamonds |
| Dependencies | Which tasks must happen before others |
| Progress | How much of each task is complete |
| Owner | Person or team responsible for each task |
| Status | On track, at risk, delayed, complete |

## Task and resource requirements

Each task should have a practical resource requirement. Include internal roles, external vendors, tools, materials, software, permits, approvals, and owner time when applicable.

Use `TBD` or `Not provided` when the questionnaire does not provide the resource or person. Do not invent named people, budget authority, vendors, permits, or fixed dates.

## Dependency language

Prefer practical dependency notes:

- `Project approval complete`
- `Requirements confirmed`
- `Vendor selected`
- `Permit received`
- `Materials delivered`
- `Design approved`
- `Final review complete`

Avoid vague dependencies such as `after planning` when a more concrete predecessor is possible.

## Confidence rating

Use `High` only when scope, deliverables, dates, owners, resources, and approvals are mostly provided.
Use `Medium` when the project is understandable but some dates, roles, durations, or dependencies are missing.
Use `Low` when the questionnaire is incomplete, vague, or missing the main deliverables or dates.

## Missing information priority

Use `High` when missing information blocks Gantt charting, especially:

- start date
- fixed deadline
- key deliverables
- task owners / available resources
- external vendors or permits
- approval authority
- required task order
- budget or procurement constraints

Use `Medium` when missing information improves planning but does not block a draft.
Use `Low` for useful details that can be refined later.
