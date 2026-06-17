# update.md Template

Use this structure exactly when writing `update.md`.

```markdown
# Consolidated Project Update

## Source folder
- Folder reviewed: [path]
- Review timestamp: [timestamp]
- Conflict policy: newest source wins by modified timestamp; unresolved ties require confirmation

## Files reviewed
| File | Modified time | Status | Notes |
|---|---|---|---|

## Consolidated updates for project plan
| Update ID | Category | Affected item | Current / old value | New value | Source file | Source modified time | Confidence |
|---|---|---|---|---|---|---|---|

## Conflict decisions
| Conflict ID | Affected item | Selected value | Selected source | Overridden value(s) | Overridden source(s) | Reason |
|---|---|---|---|---|---|---|

## Likely project plan sections affected
- [section]: [reason]

## Likely downstream artifacts affected
- `gantt_tasks.csv`: [yes/no/unknown and reason]
- Excel workbook: [yes/no/unknown and reason]
- Slide deck: [yes/no/unknown and reason]

## Items needing owner confirmation
| Item | Question | Why it matters |
|---|---|---|

## Unreadable or skipped files
| File | Reason | Action needed |
|---|---|---|
```
