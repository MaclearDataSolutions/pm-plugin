# Merge pm-plugin into product_manager vs. Keep Standalone

**Question:** Should `pm-plugin` be folded into `product_manager` (with individual projects as branches), or kept as a separate repo?

---

## Current layout

| Repo | Role |
|---|---|
| `pm-plugin` | Reusable Claude Code plugin — 21 skills, config templates, tools |
| `alcopro` | Active project workspace — `.pm-config.json`, `project/` artifacts, Jira sync |
| `product_manager` | Original reference/template workspace — minimal artifacts, possibly a starter template |

---

## Option A — Merge: pm-plugin lives inside product_manager, projects are branches

### Pros
- **Single repo to install and configure.** One `git clone`, one place to read the manual.
- **Skills and project history co-located.** A reviewer can see skill changes and the plan evolution together.
- **Simpler onboarding story** for the first project: clone, pick a branch, start working.

### Cons
- **Skills are code; project data is data. They don't belong in the same repo.**  
  When you update a skill, you'd need to merge that change into every project branch. Rebasing `alcopro` onto a skills fix means touching Excel files, Gantt charts, and Jira sync JSON — all unrelated to the skill change.
- **Git history becomes incoherent.** Commits like "fix gantt date formula" and "update jira_sync.json with sprint 4 data" end up on the same branch log. Neither helps the other.
- **Binary artifacts pollute the timeline.** Excel (`.xlsx`), PowerPoint (`.pptx`), and CSV files change frequently. They bloat the repo and produce meaningless diffs. Mixing them with skill `.md` files is bad hygiene.
- **Security / data isolation risk.** Project workspaces contain client Jira keys, email addresses, and internal planning data. If `pm-plugin` is ever shared or open-sourced, you'd need to surgically remove all project branches first.
- **Branch proliferation.** Every new project (`alcopro`, `alcopro-v2`, `clientB-onboarding`, …) adds a long-lived branch. The repo becomes unwieldy fast.
- **Plugin versioning is blocked.** If `alcopro` is pinned to branch `main` of a merged repo, any skill update immediately affects all projects with no version gate.

---

## Option B — Standalone (current approach): pm-plugin is infrastructure, each project is its own repo

### Pros
- **Clean separation of concerns.** Skills are versioned infrastructure. Project workspaces are scoped data. Neither bleeds into the other.
- **Plugin can be versioned and shared.** Today it's installed via `.superpowers/`. Tomorrow it could be a Claude Code plugin in a registry — multiple teams, multiple orgs, zero coupling to any one project's data.
- **Each project controls its own upgrade cycle.** `alcopro` can stay on a stable plugin version while you iterate on skills for a new engagement.
- **No data leakage risk.** Jira cloud IDs, personal emails, client plan details never touch the plugin repo.
- **Git history is meaningful on both sides.** `pm-plugin` log = skill evolution. `alcopro` log = project decisions and artifact history.
- **Matches how Claude Code plugins actually work.** The `.claude-plugin/` manifest and `.superpowers/` installation pattern are designed for standalone plugin repos.

### Cons
- **Two repos to maintain.** A skill bug requires a change in `pm-plugin` and a pull in each project.
- **Synchronization discipline required.** If you forget to update the plugin in a project, it silently runs an old skill version.
- **Slightly more setup for a new project.** Clone plugin, install it, create project repo, drop `.pm-config.json`.

---

## Recommendation: Keep standalone

The separation is architecturally correct and operationally safer. The main cost — two repos — is real but small. The main risk of merging — binary artifact pollution, data leakage, no version gates, branch sprawl — is structural and grows with every new project.

The right model:

```
pm-plugin/          ← install once, update deliberately
  skills/
  tools/

alcopro/            ← project workspace, references pm-plugin
  .pm-config.json
  project/          ← all generated artifacts live here

clientB-onboarding/ ← another project, same plugin
  .pm-config.json
  project/
```

`product_manager` in its current form looks like an early prototype. Consider either retiring it or repurposing it as a **template starter repo** — a clean scaffold that new project repos can be copied from, with an empty `project/`, a sample `.pm-config.json`, and a pointer to `pm-plugin`.
