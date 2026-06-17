---
name: project-intro-slide-deck
description: use this skill in claude code when the user needs to create a project introduction slide deck, kickoff deck, stakeholder presentation, owner presentation, project overview deck, or pptx from project_plan.md and gantt_tasks.csv, especially when a company_style pdf should guide company name, branding, colors, visual style, tone, logo usage, or slide design. use when the user asks to summarize a project plan into slides, present timeline and milestones, introduce scope and deliverables, explain risks and next steps, or create project_intro_deck.pptx from project planning files.
---

# Project Intro Slide Deck

Create a concise, professional PowerPoint deck that introduces a project using `project/project_plan.md`, `project/gantt_tasks.csv`, and the company style PDF found in `company_style/`.

This skill intentionally does **not** bundle a ready-made Python slide-generation script. Instead, generate a project-local Python script during the task so the deck logic is tailored to the current `project/project_plan.md`, `project/gantt_tasks.csv`, and `company_style` reference material.

## Deck types

Two deck types are available, each with its own template:

| Type | Template JSON | Template PPTX | Output | When to use |
|---|---|---|---|---|
| `intro` | `tools/templates/slide_template_intro.json` | `tools/templates/slide_template_intro.pptx` | `project/project_intro_deck.pptx` | Project kickoff, first presentation to stakeholders |
| `update` | `tools/templates/slide_template_update.json` | `tools/templates/slide_template_update.pptx` | `project/project_update_deck.pptx` | Recurring status update meetings |

Use `--type intro` or `--type update` when calling `tools/scripts/create_project_intro_deck.py`.

## Generation command

Do not generate a new Python script. Use the existing template-driven script:

```bash
python tools/scripts/create_project_intro_deck.py --project <folder> --type intro
python tools/scripts/create_project_intro_deck.py --project <folder> --type update
```

## Source file priority

1. Use files named explicitly by the user.
2. If no files are named, use `project/project_plan.md` and `project/gantt_tasks.csv`.
3. For update deck: also read `project/update.md` if present for the Executive Summary slide.
4. Check for `tools/templates/excel_template.json`. If found and `meta.template_enabled` is `true`, read `source_table.columns` to get the canonical column names before parsing `project/gantt_tasks.csv`.
5. If `project/gantt_tasks.csv` is missing, still create the deck from `project/project_plan.md`, but mark timeline details as incomplete.
6. If `project/project_plan.md` is missing, ask the user to create it first using the questionnaire-project-plan workflow.

## Main workflow

1. Determine deck type — `intro` or `update` — from the user's request.
2. Read `project/project_plan.md` fully.
3. Read `project/gantt_tasks.csv` if present.
4. For update deck: read `project/update.md` if present.
5. Run the generation command:
   ```bash
   python tools/scripts/create_project_intro_deck.py --project <folder> --type intro
   # or
   python tools/scripts/create_project_intro_deck.py --project <folder> --type update
   ```
6. Verify the output `.pptx` exists and has the expected slide count (11 for intro, 5 for update).
7. Do not invent budget, deadlines, owners, vendors, approvals, or final decisions.
9. If information is missing, write `TBD`, `Not provided`, or `Planning assumption` clearly.
10. Keep slides practical and stakeholder-friendly, not textbook-like.

## Required generated files

Create these files by default:

- `project/deck_outline.md`
- `project/project_intro_deck.pptx`
- a generated project-local Python script used to build the deck, such as `project/generated_scripts/create_project_intro_deck.py`

Optional but useful files:

- `deck_style_notes.md` if the company_style PDF contains enough branding details
- extracted logo/image files only when useful and legally/project-appropriate

## Python script generation requirements

When generating the Python script:

- Use `python-pptx` for `.pptx` creation unless the user asks for another method.
- Make the script deterministic and rerunnable.
- Include clear input constants or CLI arguments for:
  - `project/project_plan.md`
  - `project/gantt_tasks.csv`
  - `company_style/`
  - `project/project_intro_deck.pptx`
  - `project/deck_outline.md`
- Parse the project plan for project purpose, scope, deliverables, milestones, risks, roles, open decisions, and next steps.
- Parse `project/gantt_tasks.csv` for task name, work package, owner/role, duration, dependencies, dates/constraints, outputs, and notes. When `tools/templates/excel_template.json` exists and `meta.template_enabled` is `true`, use `source_table.columns[].name` values as the canonical column names in the CSV parser rather than hardcoding them — this keeps the parser in sync if the template column names change.
- Build a timeline visual from `gantt_tasks.csv` when enough schedule data exists.
- If dates are incomplete, show a phase/milestone timeline rather than a precise dated chart.
- Use the company name, colors, logo, and tone from the `company_style` PDF when confidently identified.
- If branding cannot be extracted reliably, use a conservative business theme and note the limitation in `deck_outline.md`.
- Keep slide text short. Put extra detail in speaker notes or the outline.

## company_style PDF handling

Use the PDF as a style reference, not as project content unless it clearly includes relevant company boilerplate.

Recommended approach:

1. Locate PDFs under `company_style/`.
2. Extract text with available tools, such as `pdftotext`, Python PDF libraries, or another project-approved method.
3. If useful, extract or screenshot visual pages to inspect colors, logos, and layout patterns.
4. Derive a style summary:
   - company name
   - color palette with hex values when possible
   - likely font family or font style description
   - logo/image placement guidance
   - layout guidance
   - tone guidance
5. Use these style choices consistently in the deck.
6. Do not overfit the deck to the PDF if the PDF is a report or contract rather than a brand guide.

## Default deck structure

Use this structure unless the user asks for a different audience or length:

1. Title / project introduction
2. Why this project matters
3. Project scope and expected deliverables
4. Success criteria and acceptance focus
5. Timeline overview
6. Key milestones
7. Workstreams and task summary
8. Roles and responsibilities
9. Risks and mitigation plan
10. Open decisions and information needed
11. Recommended next steps

## Slide quality rules

- Use clear slide titles, short bullets, and specific project facts.
- Prefer 3-5 bullets per slide.
- Use a timeline/Gantt visual when `gantt_tasks.csv` has enough task information.
- Keep technical planning tables in the appendix or outline unless the user asks for detailed slides.
- Make weak planning data visible. Do not make the schedule look certain if dates, owners, or durations are missing.
- Include `TBD` items on the open-decisions slide.
- Avoid overloading slides with raw text from `project_plan.md`.
- Apply the company name and visual style from the `company_style` PDF when available.
- Keep deck design polished but simple enough to maintain in PowerPoint.

## Output requirements

After creating the deck, verify:

- `project/project_intro_deck.pptx` exists.
- `project/deck_outline.md` exists.
- A project-local Python generation script exists.
- The deck uses facts from `project/project_plan.md` and `project/gantt_tasks.csv`.
- The deck uses company name/style cues from the `company_style` PDF when available.
- The timeline slide is consistent with available task data.
- Missing information is clearly marked.
- The final slide contains concrete next steps.

## Dependency note

The generated script will usually need `python-pptx`. Install dependencies in the project environment if needed:

```bash
python -m pip install python-pptx
```

For PDF text or image extraction, use available project tools or install a suitable library only if appropriate for the environment, such as `pymupdf` or `pypdf`.
