---
name: personal-pm-setup
description: use this skill to initialize a personal PM workspace for cross-project visibility. Creates .pm-config.json with role "personal", prompts the user for their name and the Jira project keys they want to monitor, verifies Jira access to each project, and writes the config. Run once per personal workspace, or when adding new projects to link.
allowed-tools: Read, Write, Edit, mcp__atlassian-rovo-mcp__atlassianUserInfo, mcp__atlassian-rovo-mcp__getVisibleJiraProjects, mcp__atlassian-rovo-mcp__getAccessibleAtlassianResources
---

# Personal PM Setup

Initialize a personal PM workspace. After setup, run `/personal-pm-dashboard` to generate your first cross-project view.

## Outputs

- `.pm-config.json` in the current working directory

## personal .pm-config.json schema

```json
{
  "role": "personal",
  "user_name": "Harris Yang",
  "user_email": "harris.yang@maclear.ca",
  "linked_projects": [
    {
      "jira_project_key": "COR",
      "jira_cloud_id": "macleardata.atlassian.net"
    },
    {
      "jira_project_key": "INF",
      "jira_cloud_id": "macleardata.atlassian.net"
    }
  ]
}
```

## Workflow

1. **Check for existing config.** If `.pm-config.json` already exists in the current directory, read it and show the current configuration. Ask: "A personal workspace is already configured here. Do you want to (A) add more projects or (B) reset the entire config?" Wait for the answer before proceeding. For option A, skip to step 5. For option B, continue from step 2.

2. **Get Jira identity.** Call `atlassianUserInfo` → extract `email` and `displayName`. Pre-populate user_email and user_name from these values.

3. **Confirm user details.** Tell the user: "I found your Atlassian account: {displayName} ({email}). Is this correct?" Wait for confirmation. If they say no, ask them to enter their name and email manually.

4. **Get accessible sites.** Call `getAccessibleAtlassianResources` → list available cloudIds and site hostnames. If only one site is available, use it as the default cloudId for all linked projects. If multiple sites, show the list and note which one will be used.

5. **Ask which projects to link.** Tell the user: "Which Jira projects do you want to monitor in your dashboard? Enter the project keys, one per line (e.g. COR, INF, BDS). Press Enter twice when done." Wait for the list.

6. **Verify each project.** For each project key entered:
   - Call `getVisibleJiraProjects` with `cloudId` and `searchString` = project key.
   - If found: confirm "✓ COR — {project name} — accessible".
   - If not found: warn "✗ {KEY} — not found or not accessible. This project will be skipped."

7. **Write `.pm-config.json`** with all verified projects. Skip any projects that failed the access check.

8. **Report setup complete.** Tell the user:
   - Config written to: `.pm-config.json`
   - Linked projects: {list of verified keys}
   - Skipped: {list of failed keys if any}
   - "Run /personal-pm-dashboard to generate your first cross-project dashboard."

## Adding more projects later

The user can either:
- Run `/personal-pm-setup` again and choose option A (add more projects)
- Manually edit `.pm-config.json` and add entries to the `linked_projects` array

## Rules

- Never overwrite `.pm-config.json` without explicit user confirmation (see step 1).
- Never add a project key that failed the access check.
- If `atlassianUserInfo` fails (Jira not authenticated), stop and tell the user to authenticate via Claude Code's built-in Atlassian auth flow first.
- If no projects pass the access check, do not write `.pm-config.json` — report the failures and ask the user to verify their Jira access.
