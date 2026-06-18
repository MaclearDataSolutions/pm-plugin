# Gantt output format reference

Use this reference when refining or debugging generated Gantt outputs.

## Mermaid Gantt basics

A Mermaid Gantt chart starts with `gantt`, then usually includes `title`, `dateFormat YYYY-MM-DD`, an optional `axisFormat`, and sections for work packages.

Example structure only:

```mermaid
gantt
    title Example Project
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    excludes weekends

    section Planning
    Kickoff [Owner: Owner] :crit, t1, 2026-06-01, 1d
    Requirements [Owner: PM] :t2, 2026-06-02, 3d
    Approval [Owner: Sponsor] :milestone, crit, t3, 2026-06-05, 0d
```

## Required schedule fields

| Field | Purpose |
|---|---|
| Task ID | Stable identifier for Mermaid, CSV, and Excel |
| Task | Short readable task label |
| Work package | Mermaid section and Excel grouping |
| Owner / role | Accountability and chart label |
| Resource requirements | People, tools, vendors, materials, approvals, or systems needed |
| Task description | Practical explanation of the task |
| Estimated start | Calculated or provided start date |
| Estimated end | Calculated or provided end date |
| Duration | Estimated business-day task length |
| Depends on | Predecessor task IDs |
| Progress | Percent complete or unknown |
| Status | Not started, on track, at risk, delayed, complete, or unknown |
| Estimate basis | Explains whether the value was provided, inferred, or assumed |
| Critical? | Flags approvals, deadlines, launch, permits, and final acceptance |
| Notes | Extra constraints, outputs, or missing information |

## Missing information policy

Do not hide uncertainty. Every weak value must be visible:

- missing start date: use a planning start date and mark it as an assumption
- missing duration: estimate from task type and mark estimate basis
- missing dependency: sequence from source order and mark it as provisional
- missing owner: use `Unknown`
- missing resources: use `Unknown`
- missing progress: use `Unknown` or `0%` only if the project clearly has not started
- unclear task description: derive from task name and output, then mark it as inferred

## Runtime Excel script guidance

The skill must not ship a ready-made Excel script. During the task, Claude Code should generate a repo-local Python script that matches the current `gantt_chart.md` table and environment.

The generated script should be easy to inspect, specific to the current repo, and safe to rerun.
