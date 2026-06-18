# pm-plugin

Private Claude Code plugin for Maclear Data Solutions — project planning, Gantt charts, Jira sync, and cross-project dashboards.

## Install (team members)

**Prerequisites:** Claude Code installed, member of the `MaclearDataSolutions` GitHub org.

### Step 1 — Authenticate with GitHub

```bash
gh auth login
```

Or configure an SSH key or PAT in your git credential store.

### Step 2 — Install the plugin (run once per machine)

```bash
claude plugin install github:MaclearDataSolutions/pm-plugin
```

### Step 3 — Authenticate Jira

Claude Code's built-in Atlassian auth flow runs automatically on first use of any Jira skill.

### Step 4 — Set up your personal workspace

Run `/personal-pm-setup` in any directory to create your personal dashboard workspace and link your projects.

---

## Starting a new project

```bash
# 1. Create a project directory
mkdir my-project && cd my-project

# 2. Copy the project config template and fill it in
cp "$(claude plugin path pm-plugin)/config-templates/project.pm-config.json" .pm-config.json
# Edit .pm-config.json: set project_name, jira_project_key, jira_cloud_id, owner

# 3. Run the baseline lane
/project-owner-questionnaire
/questionnaire-project-plan
/gantt-chart-creator
/project-intro-slide-deck

# 4. Sync tasks to Jira
/jira-project-sync
```

---

## Updating the plugin

```bash
claude plugin update github:MaclearDataSolutions/pm-plugin
```

Skills, scripts, and templates update. All `project/` data and `.pm-config.json` files in your workspaces are untouched.

---

## Access control

Access is gated by GitHub org membership. To grant access: add the person to the `MaclearDataSolutions` org. To revoke: remove them.

---

## Full skill reference

See [CLAUDE.md](CLAUDE.md) for the complete skill list and workflow.
