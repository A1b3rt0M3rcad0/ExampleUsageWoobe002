# Atlas Vendor Risk Network

## Network

- Name: `Atlas Vendor Risk Network`
- Root Agent: `Atlas Risk Coordinator`
- Purpose: execute a complete evidence-based Atlas assessment.
- Assessment engine session behavior: stateless.
- Recommended max depth: 2.
- Recommended max Agent invocations: 4.
- Recommended timeout: 120 seconds.

## Nodes

1. `Atlas Risk Coordinator` — root
2. `Atlas Security Analyst`
3. `Atlas Legal Analyst`
4. `Atlas Compliance Analyst`

## Edges / delegations

- Atlas Risk Coordinator -> Atlas Security Analyst
- Atlas Risk Coordinator -> Atlas Legal Analyst
- Atlas Risk Coordinator -> Atlas Compliance Analyst

No specialist-to-specialist edge.
No specialist can recursively call the coordinator.
The graph remains a shallow star.

## Runtime behavior

The coordinator reads the assessment context, then delegates only the domains listed by Atlas in `required_domains`.

For the default PoV assessment all three domains are required, therefore a successful full Network Run normally produces:
- 1 Agent Run for the coordinator;
- 1 Security Agent Run;
- 1 Legal Agent Run;
- 1 Compliance Agent Run.

The Network Run aggregates those four Agent Runs. Tool Calls remain inside each Agent Run and are not additional Agent Runs.

## Version rules

Draft is editable.
Staging is used for validation.
Production must bind only immutable Agent Releases.
A Network Release must preserve the exact specialist releases it uses.

Do not point production at mutable Draft agents.
