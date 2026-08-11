# Atlas — exact Woobe setup

Use one Woobe Project named `Atlas Vendor Risk`.

## 1. Create the Project

- **Project name:** `Atlas Vendor Risk`
- **Description:** `AI control plane for the Atlas vendor-risk assessment product.`

## 2. Create a Tool authentication Secret

Create a Project Secret:

- **Name:** `ATLAS_HTTP_AUTHORIZATION`
- **Type:** `CUSTOM`
- **Value:** `Bearer <ATLAS_WOOBE_TOOL_TOKEN>`

The value includes the literal `Bearer ` prefix. The HTTP Tool headers use the Woobe secret reference:

`{{secret:ATLAS_HTTP_AUTHORIZATION}}`

The raw token after `Bearer ` must match `ATLAS_WOOBE_TOOL_TOKEN` in Atlas `.env`.

## 3. Create the HTTP Tools

Create exactly two project HTTP Tools.

### Tool A — Atlas Assessment Context

- **Name:** `Atlas Assessment Context`
- **Type:** HTTP
- **Risk:** LOW
- **Timeout:** 10000 ms
- Configure it from `tools/atlas-assessment-context.json`.

### Tool B — Atlas Evidence API

- **Name:** `Atlas Evidence API`
- **Type:** HTTP
- **Risk:** LOW
- **Timeout:** 15000 ms
- Configure it from `tools/atlas-evidence-api.json`.

Replace `https://atlas.example.com` with the URL at which the Woobe runtime can reach Atlas. For local Docker Woobe + host Atlas this may be `http://host.docker.internal:8080`; use the address valid in your deployment.

All routes are read-only from the business perspective. There is no Agent tool that writes/deletes Atlas data.

## 4. Create the Knowledge Collections

Create four Collections:

1. `Atlas Shared Policy`
   - `knowledge/shared/risk-scoring-methodology.md`
   - `knowledge/shared/evidence-handling-policy.md`

2. `Atlas Security Policy`
   - `knowledge/security/security-requirements.md`
   - `knowledge/security/security-assessment-methodology.md`

3. `Atlas Legal Policy`
   - `knowledge/legal/legal-requirements.md`
   - `knowledge/legal/legal-assessment-methodology.md`

4. `Atlas Compliance Policy`
   - `knowledge/compliance/compliance-requirements.md`
   - `knowledge/compliance/compliance-assessment-methodology.md`

These documents are controlled product knowledge. Do not upload Atlas customer/vendor evidence into these Collections.

## 5. Create the Agents

Create these four Agents, using the exact prompts/configuration sheets in `agents/`:

1. `Atlas Risk Coordinator`
2. `Atlas Security Analyst`
3. `Atlas Legal Analyst`
4. `Atlas Compliance Analyst`

Model choice is deployment-specific because it depends on Provider Models/Credentials configured in your Woobe instance. Use the same tool-capable model for the first PoV, with low creativity/temperature if the provider exposes it. Do not invent a model binding that does not exist in your catalog.

Attach structured output using the JSON schemas in `output-contracts/`.

## 6. Create the single Agent Network

Configure the Project's Network from `network/atlas-vendor-risk-network.md`.

Root:
`Atlas Risk Coordinator`

Delegation edges:
- Coordinator -> Security Analyst
- Coordinator -> Legal Analyst
- Coordinator -> Compliance Analyst

Recommended MVP limits:
- max depth: `2`
- max Agent invocations: `4`
- timeout: `120 seconds`
- session behavior for the assessment engine: `stateless`

The coordinator is one Agent Run; each delegated specialist is another Agent Run.

## 7. Stage and release

1. Validate each Agent in Draft.
2. Create Staging versions/releases according to the current Woobe flow.
3. Bind the Network Staging version only to valid Staging/Release Agents.
4. Execute representative assessments.
5. Publish immutable Agent Releases.
6. Publish a Network Release using only Agent Releases.
7. Create a Runtime Key bound to this Network and the desired `staging` or `production` environment.
8. Put the Runtime Key only in Atlas backend `.env` as `WOOBE_RUNTIME_KEY`.

Runtime Keys cannot execute a Network Draft.

## 8. Atlas Runtime integration

Atlas calls:

`POST <WOOBE_BASE_URL>/v1/run`

The Runtime Key determines the Project, Network and environment. Atlas does not send a mutable Network ID or Release ID.

The message contains the `assessment_id`. Specialists use Atlas Tools to resolve assessment-specific data.

## 9. Validation checklist

Before calling the PoV ready:

- Tool tests can reach Atlas.
- Wrong Atlas Tool token returns 401.
- Duplicate document inside one assessment returns 409.
- Customer documents do not appear in Woobe Knowledge.
- Every vendor-specific finding contains Atlas evidence references.
- No Agent treats policy Knowledge as evidence about the vendor.
- Specialist Agents produce valid structured JSON.
- Network root produces valid `VendorAssessment`.
- Atlas persists `parsed_output`.
- Production Network uses immutable Agent Releases.
- A completed Atlas assessment can be traced to a Woobe Network Run and its Agent Runs.
