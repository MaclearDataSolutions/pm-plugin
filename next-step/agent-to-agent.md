
for the agent-to-agent process.MCP servers need hosting infrastructure. Jira handles v1 with zero new infra. Plugin is designed so MCP slots in          
alongside Jira — both can run simultaneously, Jira stays as fallback and audit trail. could you elaborate on that?  

---
Why it needs hosting

For Personal PM to reach Project PM's server, the server must be reachable over a network and running. Three realistic options:

┌───────────────────────────────────────┬───────────┬──────────────────────────┬────────────────────────┐
│                Option                 │   Cost    │        Always on?        │     Works remote?      │
├───────────────────────────────────────┼───────────┼──────────────────────────┼────────────────────────┤
│ Laptop-local (e.g. localhost:8000)    │ Free      │ Only when laptop is open │ No — same network only │
├───────────────────────────────────────┼───────────┼──────────────────────────┼────────────────────────┤
│ Small VPS (DigitalOcean, $5/mo)       │ ~$5/mo    │ Yes                      │ Yes                    │
├───────────────────────────────────────┼───────────┼──────────────────────────┼────────────────────────┤
│ Serverless (AWS Lambda + API Gateway) │ Near-zero │ Yes (cold start)         │ Yes                    │
└───────────────────────────────────────┴───────────┴──────────────────────────┴────────────────────────┘

3. Non-plugin users. Stakeholders and managers who don't run Claude Code can still open Jira and read project status. MCP only works inside Claude Code.

---
How "both run simultaneously" works in practice

Personal PM runs /personal-pm-dashboard
        │
        ├── Try MCP server for Project A
        │     ├── Server responds → use live data  ✓
        │     └── Server unreachable → fall back to pm-status Jira ticket
        │
        └── Try MCP server for Project B
            ├── Server responds → use live data  ✓
            └── Server unreachable → fall back to pm-status Jira ticket

Project PM writes to Jira on every Lane B run regardless — so the Jira fallback is always at most one progress cycle stale. MCP gives you real-time richness when
available; Jira gives you guaranteed availability when not.
