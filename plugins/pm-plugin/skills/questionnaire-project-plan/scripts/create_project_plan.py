#!/usr/bin/env python3
"""Create a structured project_plan.md draft from a completed project questionnaire.

This helper is intentionally conservative: it extracts visible answers and marks
missing information rather than inventing project facts. Claude Code should read
and improve the generated draft after running the script.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path
from typing import Dict, List, Tuple

QUESTION_RE = re.compile(r"^\*\*(\d+)\.\s*(.*?)\*\*\s*$")
HEADING_RE = re.compile(r"^#{1,6}\s+")

QUESTION_KEYS = {
    1: "project_name",
    2: "decision_maker",
    3: "day_to_day_contact",
    4: "business_problem",
    5: "successful_result",
    6: "deliverables",
    7: "in_scope",
    8: "out_of_scope",
    9: "must_have",
    10: "nice_to_have",
    11: "start_date",
    12: "fixed_deadline",
    13: "important_dates",
    14: "specific_order",
    15: "parallel_tasks",
    16: "company_people",
    17: "external_parties",
    18: "prework_needs",
    19: "budget",
    20: "spending_limits",
    21: "risks",
    22: "open_decisions",
    23: "updates",
    24: "final_approver",
    25: "previous_materials",
    26: "priority_tradeoff",
    27: "scope_adjustment_allowed",
}

QUESTION_TEXT = {
    1: "What is the name of the project?",
    2: "Who is the final decision-maker for this project?",
    3: "Who should be contacted day-to-day for project questions?",
    4: "What problem is this project supposed to solve?",
    5: "What does a successful final result look like in practical terms?",
    6: "What are the main deliverables you expect?",
    7: "What is included in the project?",
    8: "What is definitely not included in the project?",
    9: "Are there any must-have requirements?",
    10: "Are there any nice-to-have items that should only be done if time or budget allows?",
    11: "What is the preferred project start date?",
    12: "Is there a fixed deadline? If yes, what date and why is it fixed?",
    13: "Are there any important dates we must plan around?",
    14: "Are there tasks that must happen in a specific order?",
    15: "Are there tasks that can happen at the same time?",
    16: "Who will be involved from your company? Please list names, roles, and availability.",
    17: "Will outside vendors, contractors, suppliers, consultants, or agencies be involved?",
    18: "Are any materials, equipment, software, permits, or approvals needed before work can begin?",
    19: "What is the approved budget or budget range?",
    20: "Are there spending approval limits?",
    21: "What are the biggest risks or concerns you already see?",
    22: "What decisions are still not made yet?",
    23: "How often do you want project updates?",
    24: "Who needs to approve the final deliverables before the project is considered complete?",
    25: "Are there any previous similar projects, documents, quotes, designs, contracts, or lessons learned we should review?",
    26: "What is most important if there is a conflict: time, cost, quality, or scope?",
    27: "Are we allowed to adjust the project scope if the deadline or budget is not realistic?",
}

MISSING = "Not provided"


def clean_answer(lines: List[str]) -> str:
    text = "\n".join(lines).strip()
    # Remove common prompt/example lines that follow questions.
    text = re.sub(r"(?im)^examples?:.*$", "", text).strip()
    text = re.sub(r"(?im)^answer:\s*", "", text).strip()
    if not text or text.lower() in {"answer:", "n/a", "na", "none", "tbd", "todo"}:
        return MISSING
    return text


def parse_questionnaire(text: str) -> Dict[int, str]:
    answers: Dict[int, List[str]] = {}
    current_q: int | None = None
    collecting = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        q_match = QUESTION_RE.match(line.strip())
        if q_match:
            current_q = int(q_match.group(1))
            answers.setdefault(current_q, [])
            collecting = False
            continue

        if current_q is None:
            continue

        if line.strip().lower().startswith("answer:"):
            collecting = True
            remainder = line.split(":", 1)[1].strip()
            if remainder:
                answers[current_q].append(remainder)
            continue

        if collecting:
            # Section headings are structure, not answers.
            if HEADING_RE.match(line):
                continue
            answers[current_q].append(line)

    return {q: clean_answer(v) for q, v in answers.items()}


def ans(parsed: Dict[int, str], number: int) -> str:
    return parsed.get(number, MISSING) or MISSING


def split_items(value: str) -> List[str]:
    if value == MISSING:
        return []
    # Preserve meaningful multi-line bullets; otherwise split on semicolons.
    lines = [re.sub(r"^[-*\d.)\s]+", "", ln.strip()) for ln in value.splitlines() if ln.strip()]
    if len(lines) > 1:
        return [ln for ln in lines if ln]
    parts = [p.strip() for p in re.split(r";|,\s*(?=[A-Z0-9])", value) if p.strip()]
    return parts if parts else [value]


def md_list(items: List[str], fallback: str = MISSING) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def planning_confidence(parsed: Dict[int, str]) -> Tuple[str, str]:
    critical = [1, 2, 4, 5, 6, 7, 11, 12, 14, 16, 19, 24]
    provided = sum(1 for q in critical if ans(parsed, q) != MISSING)
    if provided >= 10:
        return "High", "Most core planning inputs are provided."
    if provided >= 6:
        return "Medium", "The project is understandable, but some dates, resources, dependencies, or approvals need confirmation."
    return "Low", "Several core planning inputs are missing or unclear."


def make_wbs(deliverables: List[str]) -> List[Tuple[str, str, str, str]]:
    rows: List[Tuple[str, str, str, str]] = [
        ("1.0", "Project initiation and planning", "Confirm objectives, scope, owner expectations, and planning assumptions.", "Approved project plan"),
        ("2.0", "Requirements and scope confirmation", "Confirm must-have requirements, nice-to-have items, exclusions, and acceptance criteria.", "Confirmed requirements"),
    ]
    base = 3
    if deliverables:
        for i, deliverable in enumerate(deliverables, start=base):
            rows.append((f"{i}.0", f"Deliverable: {deliverable}", f"Plan, execute, review, and approve {deliverable}.", deliverable))
        next_id = base + len(deliverables)
    else:
        rows.append(("3.0", "Main project delivery work", "Detailed work packages cannot be finalized until deliverables are confirmed.", "Project deliverables"))
        next_id = 4
    rows.extend([
        (f"{next_id}.0", "Quality review and acceptance", "Check deliverables against success criteria and obtain approval.", "Accepted deliverables"),
        (f"{next_id + 1}.0", "Handover and closeout", "Complete handover, lessons learned, and final documentation.", "Project closeout"),
    ])
    return rows


def make_tasks(deliverables: List[str]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    def add(task_id: str, task: str, wp: str, owner: str, duration: str, dep: str, constraint: str, output: str, notes: str):
        status = "At risk" if ("TBD" in owner or duration == "TBD" or constraint == "TBD") else "Not started"
        progress = "0%"
        description = notes if notes and notes != "TBD" else output
        rows.append({
            "id": task_id, "task": task, "wp": wp, "owner": owner, "duration": duration,
            "dep": dep, "constraint": constraint, "output": output, "notes": notes,
            "description": description, "progress": progress, "status": status,
        })

    add("T1", "Confirm project owner, decision-maker, and approval process", "1.0", "Project manager / sponsor", "1 day", "None", "Project start", "Confirmed governance", "Planning estimate")
    add("T2", "Review completed questionnaire and identify planning gaps", "1.0", "Project manager", "1 day", "T1", "After questionnaire received", "Gap list", "Planning estimate")
    add("T3", "Confirm requirements, scope, exclusions, and success criteria", "2.0", "Project manager + owner", "2-3 days", "T2", "Owner availability", "Confirmed scope", "Planning estimate")
    add("T4", "Create baseline project plan and Gantt-ready task list", "1.0", "Project manager", "1-2 days", "T3", "After scope confirmation", "Draft project plan", "Planning estimate")

    prev = "T4"
    task_num = 5
    if deliverables:
        for idx, deliverable in enumerate(deliverables, start=1):
            add(f"T{task_num}", f"Plan work for {deliverable}", f"{idx + 2}.0", "Assigned owner / role TBD", "1-2 days", prev, "TBD", f"Work plan for {deliverable}", "Planning estimate; confirm owner and duration")
            prev = f"T{task_num}"
            task_num += 1
            add(f"T{task_num}", f"Execute work for {deliverable}", f"{idx + 2}.0", "Assigned owner / role TBD", "TBD", prev, "TBD", deliverable, "Duration must be confirmed from team/vendor estimates")
            prev = f"T{task_num}"
            task_num += 1
            add(f"T{task_num}", f"Review and approve {deliverable}", f"{idx + 2}.0", "Owner / final approver", "1-2 days", prev, "Approver availability", f"Approved {deliverable}", "Planning estimate")
            prev = f"T{task_num}"
            task_num += 1
    else:
        add("T5", "Define missing deliverables", "3.0", "Project owner", "TBD", "T4", "Owner input required", "Confirmed deliverable list", "Required before detailed Gantt chart")
        prev = "T5"
        task_num = 6

    add(f"T{task_num}", "Final quality check and acceptance review", "Quality review and acceptance", "Project manager + final approver", "1-3 days", prev, "After all deliverables complete", "Acceptance decision", "Planning estimate")
    prev = f"T{task_num}"
    task_num += 1
    add(f"T{task_num}", "Handover and closeout", "Handover and closeout", "Project manager", "1-2 days", prev, "After final approval", "Closeout notes and handover", "Planning estimate")
    return rows


def make_project_flow(tasks: List[Dict[str, str]]) -> List[Tuple[str, str, str, str]]:
    flow = []
    for idx, task in enumerate(tasks, start=1):
        flow.append((
            str(idx),
            task["task"],
            task["dep"],
            task["output"],
        ))
    return flow


def infer_task_resources(task: Dict[str, str], parsed: Dict[int, str]) -> str:
    name = task["task"].lower()
    resources = []
    if any(word in name for word in ["owner", "decision", "approval", "approve", "acceptance"]):
        resources.append(f"owner / approver: {ans(parsed, 2)}")
    if any(word in name for word in ["questionnaire", "requirements", "scope", "plan", "gantt"]):
        resources.append("project manager / planner")
    if "execute" in name or "work for" in name:
        resources.append(f"assigned internal team: {ans(parsed, 16)}")
        resources.append(f"external support if needed: {ans(parsed, 17)}")
    if any(word in name for word in ["purchase", "procurement", "materials", "permit", "software"]):
        resources.append(f"materials / permits / tools: {ans(parsed, 18)}")
    if not resources:
        resources.append(task["owner"] or "assigned owner / role TBD")
    return "; ".join(resources)


def make_resource_requirement_rows(tasks: List[Dict[str, str]], parsed: Dict[int, str]) -> List[List[str]]:
    rows = []
    for task in tasks:
        rows.append([
            task["id"],
            task["task"],
            task["description"],
            make_task_inputs(task, parsed),
            infer_task_resources(task, parsed),
            task["output"],
            task["owner"],
            task["dep"],
        ])
    return rows


def make_task_inputs(task: Dict[str, str], parsed: Dict[int, str]) -> str:
    name = task["task"].lower()
    if "questionnaire" in name:
        return "completed owner questionnaire"
    if "requirements" in name or "scope" in name:
        return f"scope answers: {ans(parsed, 7)}; requirements: {ans(parsed, 9)}"
    if "execute" in name or "work for" in name:
        return "approved scope, assigned owner, required materials/tools, predecessor task output"
    if "approve" in name or "acceptance" in name:
        return "completed deliverable and acceptance criteria"
    return "project questionnaire and previous task output"


def gantt_element_rows(parsed: Dict[int, str]) -> List[List[str]]:
    return [
        ["Task list", "Activities, deliverables, and work packages from the questionnaire and WBS.", "Use the Gantt-ready task list and task/resource table."],
        ["Timeline", "Preferred start date, fixed deadline, and important dates from the owner.", f"Start: {ans(parsed, 11)}; deadline: {ans(parsed, 12)}; important dates: {ans(parsed, 13)}"],
        ["Bars", "Each task bar should show estimated start date, duration, and end date.", "Use estimated duration and dependency order; calculate exact dates in the Gantt chart step."],
        ["Milestones", "Key deadlines, approvals, reviews, and decision points.", "Use the milestones section and owner-provided important dates."],
        ["Dependencies", "Which tasks must happen before others and which tasks can run in parallel.", f"Required order: {ans(parsed, 14)}; parallel work: {ans(parsed, 15)}"],
        ["Progress", "How much of each task is complete.", "Default to 0% / Not started unless the questionnaire says work has already begun."],
        ["Owner", "Person, team, vendor, or role responsible for each task.", f"Internal team: {ans(parsed, 16)}; external parties: {ans(parsed, 17)}"],
        ["Status", "Current task state: Not started, On track, At risk, Delayed, Complete.", "Default to Not started; mark At risk when an owner, date, resource, or approval is missing."],
    ]


def open_questions(parsed: Dict[int, str]) -> List[Tuple[str, str, str, str]]:
    mapping = [
        ("High", 6, "Confirm the full list of deliverables.", "Deliverables become WBS sections and Gantt summary bars.", "Project owner"),
        ("High", 11, "Confirm the project start date.", "The Gantt chart needs a baseline start point.", "Project owner"),
        ("High", 12, "Confirm whether the deadline is fixed and why.", "A fixed deadline changes schedule compression and prioritization.", "Project owner"),
        ("High", 14, "Confirm required task order and hard dependencies.", "Dependencies determine the Gantt sequence and critical path.", "Project manager / owner"),
        ("High", 16, "Confirm internal people, roles, and availability.", "Resource availability affects task duration and sequencing.", "Company owner"),
        ("Medium", 17, "Confirm external vendors or contractors.", "External dependencies may add lead time and approval gates.", "Project owner"),
        ("Medium", 18, "Confirm materials, permits, software, or approvals needed before work starts.", "Prework items may become early Gantt tasks.", "Project owner"),
        ("High", 24, "Confirm final approval authority.", "Final acceptance should be a milestone in the schedule.", "Project owner"),
    ]
    return [(pri, q, why, who) for pri, num, q, why, who in mapping if ans(parsed, num) == MISSING]


def table_row(values: List[str]) -> str:
    escaped = [v.replace("\n", "<br>").replace("|", "\\|") for v in values]
    return "| " + " | ".join(escaped) + " |"


def build_plan(parsed: Dict[int, str], input_name: str) -> str:
    project_name = ans(parsed, 1)
    if project_name == MISSING:
        project_name = "TBD Project"
    deliverables = split_items(ans(parsed, 6))
    confidence, confidence_reason = planning_confidence(parsed)
    today = dt.date.today().isoformat()
    wbs = make_wbs(deliverables)
    tasks = make_tasks(deliverables)
    gaps = open_questions(parsed)

    deliverable_rows = []
    if deliverables:
        for d in deliverables:
            deliverable_rows.append(table_row([d, d, ans(parsed, 5), ans(parsed, 24), "Acceptance criteria should be confirmed."]))
    else:
        deliverable_rows.append(table_row([MISSING, MISSING, MISSING, ans(parsed, 24), "Deliverables must be confirmed before final Gantt charting."]))

    milestone_rows = [
        table_row(["Project start", ans(parsed, 11), "Project approval / owner confirmation", ans(parsed, 2), "Confirm before baselining schedule"]),
        table_row(["Scope confirmed", "TBD", "Questionnaire reviewed and gaps answered", ans(parsed, 2), "Required before detailed scheduling"]),
        table_row(["Final approval", ans(parsed, 12), "All deliverables complete", ans(parsed, 24), "May be deadline-driven"]),
    ]
    if ans(parsed, 13) != MISSING:
        for item in split_items(ans(parsed, 13)):
            milestone_rows.append(table_row([item, "See owner-provided date", "TBD", ans(parsed, 2), "Owner identified as important date"]))

    risk_items = split_items(ans(parsed, 21)) or ["Missing or unclear project risks"]
    risk_rows = []
    for idx, risk in enumerate(risk_items, start=1):
        risk_rows.append(table_row([f"R{idx}", risk, "Owner-identified concern" if ans(parsed, 21) != MISSING else "Questionnaire incomplete", "Could affect schedule, cost, scope, or quality", "TBD", "TBD", "Confirm mitigation with project owner", "TBD"]))

    open_decisions_items = split_items(ans(parsed, 22))
    if open_decisions_items:
        for idx, item in enumerate(open_decisions_items, start=len(risk_rows) + 1):
            risk_rows.append(table_row([f"R{idx}", f"Open decision: {item}", "Decision not finalized", "May block planning or execution", "TBD", "Medium", "Assign owner and due date for decision", ans(parsed, 2)]))

    gap_rows = [table_row(list(g)) for g in gaps] or [table_row(["Low", "No major missing information detected by the script.", "Review manually before baselining the Gantt chart.", "Project manager"])]

    plan = f"""# Project Plan: {project_name}

## 1. Executive summary
This plan converts the owner questionnaire into a practical project-management plan for execution and Gantt chart preparation. The project purpose is: {ans(parsed, 4)}

Expected final result: {ans(parsed, 5)}

Main deliverables identified: {ans(parsed, 6)}

## 2. Source and confidence
- Source file reviewed: `{input_name}`
- Date prepared: {today}
- Planning confidence: {confidence}
- Reason for confidence rating: {confidence_reason}

## 3. Project identity and governance
| Item | Details |
|---|---|
| Project name | {project_name} |
| Project owner / sponsor | {ans(parsed, 2)} |
| Final decision-maker | {ans(parsed, 2)} |
| Day-to-day contact | {ans(parsed, 3)} |
| Final approver | {ans(parsed, 24)} |
| Change approver | {ans(parsed, 2)} |
| Budget approver | {ans(parsed, 20)} |

## 4. Business purpose and success criteria
### Business problem
{ans(parsed, 4)}

### Success criteria
| Success criterion | How it will be checked | Owner / approver |
|---|---|---|
| {ans(parsed, 5)} | Compare completed deliverables against owner expectations and acceptance criteria. | {ans(parsed, 24)} |

## 5. Scope
### In scope
{md_list(split_items(ans(parsed, 7)))}

### Out of scope
{md_list(split_items(ans(parsed, 8)))}

### Must-have requirements
{md_list(split_items(ans(parsed, 9)))}

### Nice-to-have items
{md_list(split_items(ans(parsed, 10)))}

## 6. Deliverables and acceptance criteria
| Deliverable | Description | Acceptance criteria | Approver | Notes |
|---|---|---|---|---|
{chr(10).join(deliverable_rows)}

## 7. Milestones
| Milestone | Target date | Dependency | Approval needed | Notes |
|---|---|---|---|---|
{chr(10).join(milestone_rows)}

## 8. Work breakdown structure
| WBS ID | Work package | Description | Deliverable supported |
|---|---|---|---|
{chr(10).join(table_row(list(row)) for row in wbs)}

## 9. Project flow and execution sequence
This flow shows the practical order of work based on the questionnaire, deliverables, approvals, and dependencies. It should be reviewed before final Gantt charting.

| Step | Task / phase | Must happen after | Output / handoff |
|---:|---|---|---|
{chr(10).join(table_row(list(row)) for row in make_project_flow(tasks))}

## 10. Basic Gantt planning elements
| Element | What it shows for this project | Source / planning note |
|---|---|---|
{chr(10).join(table_row(row) for row in gantt_element_rows(parsed))}

## 11. Task and resource requirements
| Task ID | Task | Task description | Inputs needed | Resource requirement | Output | Owner / role | Dependency |
|---|---|---|---|---|---|---|---|
{chr(10).join(table_row(row) for row in make_resource_requirement_rows(tasks, parsed))}

## 12. Gantt-ready task list
| Task ID | Task | Work package | Owner / role | Estimated duration | Depends on | Earliest start / constraint | Output | Progress | Status | Notes |
|---|---|---|---|---:|---|---|---|---:|---|---|
{chr(10).join(table_row([r['id'], r['task'], r['wp'], r['owner'], r['duration'], r['dep'], r['constraint'], r['output'], r['progress'], r['status'], r['notes']]) for r in tasks)}

## 13. Dependency notes
- Finish-to-start dependencies: {ans(parsed, 14)}
- Tasks that can run in parallel: {ans(parsed, 15)}
- External dependencies: {ans(parsed, 17)}
- Approval gates: {ans(parsed, 2)} for major decisions; {ans(parsed, 24)} for final approval.

## 14. Resource plan
| Resource / role | Person or vendor | Responsibilities | Availability / constraint | Planning risk |
|---|---|---|---|---|
| Internal project team | {ans(parsed, 16)} | Execute assigned project work and provide subject-matter input. | {ans(parsed, 16)} | Confirm exact availability before baselining schedule. |
| External vendors / contractors | {ans(parsed, 17)} | Provide external services, materials, or specialist work. | {ans(parsed, 17)} | Vendor lead times may affect the schedule. |
| Project owner / sponsor | {ans(parsed, 2)} | Approve scope, budget, major decisions, and changes. | TBD | Slow approvals can delay dependent work. |

## 15. Budget and procurement notes
| Item | Budget / cost information | Approval rule | Timing impact | Notes |
|---|---|---|---|---|
| Overall budget | {ans(parsed, 19)} | {ans(parsed, 20)} | Budget approval may be needed before purchasing or vendor work. | Confirm spending authority before procurement tasks. |
| Materials, equipment, software, permits, or approvals | {ans(parsed, 18)} | {ans(parsed, 20)} | Lead times may need early scheduling. | Add each confirmed item as a Gantt task. |

## 16. Risk register
| Risk ID | Risk | Cause | Impact | Probability | Severity | Response / mitigation | Owner |
|---|---|---|---|---|---|---|---|
{chr(10).join(risk_rows)}

## 17. Communication plan
| Audience | Information needed | Format / channel | Frequency | Sender / owner |
|---|---|---|---|---|
| Project owner / sponsor | Progress, decisions needed, risks, budget or schedule issues | {ans(parsed, 23)} | {ans(parsed, 23)} | Project manager |
| Project team | Task assignments, due dates, dependencies, blockers | Meeting or shared project tracker | Weekly or as agreed | Project manager |
| Vendors / contractors | Scope, schedule, purchase requirements, approvals | Email / contract documents / meetings | As needed by task | Project manager or assigned owner |

## 18. Change control
- Scope changes: Route to {ans(parsed, 2)} for approval before work is added.
- Schedule changes: Confirm impact on deadline: {ans(parsed, 12)}.
- Budget changes: Follow spending rule: {ans(parsed, 20)}.
- Approval process: Document request, reason, impact on time/cost/scope/quality, decision, and date approved.

## 19. Assumptions and constraints
### Confirmed constraints
- Preferred start date: {ans(parsed, 11)}
- Fixed deadline: {ans(parsed, 12)}
- Important dates: {ans(parsed, 13)}
- Priority tradeoff: {ans(parsed, 26)}
- Scope adjustment allowed: {ans(parsed, 27)}

### Planning assumptions
- Durations marked as planning estimates must be confirmed by the assigned owner or vendor.
- Any item marked `TBD` or `Not provided` must be resolved before the Gantt chart is baselined.
- If scope, deadline, and budget conflict, the owner priority is: {ans(parsed, 26)}.

## 20. Open questions before final Gantt chart
| Priority | Question | Why it matters for the Gantt chart | Who should answer |
|---|---|---|---|
{chr(10).join(gap_rows)}

## 21. Recommended next steps
1. Confirm missing dates, owners, deliverables, approvals, and dependencies.
2. Review the Gantt-ready task list with the owner and project team.
3. Replace planning estimates with owner/vendor-approved durations.
4. Convert the task list into the Gantt chart after dependencies and durations are approved.
"""
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Create project_plan.md from a completed project questionnaire.")
    parser.add_argument("--input", "-i", default="empty_questionnaire.md", help="Completed questionnaire markdown file")
    parser.add_argument("--output", "-o", default="project_plan.md", help="Output project plan markdown file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output file if it already exists")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")
    if output_path.exists() and not args.overwrite:
        raise SystemExit(f"Output file already exists: {output_path}. Use --overwrite to replace it.")

    text = input_path.read_text(encoding="utf-8")
    parsed = parse_questionnaire(text)
    plan = build_plan(parsed, input_path.name)
    output_path.write_text(plan, encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
