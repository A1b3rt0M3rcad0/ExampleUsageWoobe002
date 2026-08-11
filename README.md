# Atlas — AI Vendor Risk powered by Woobe

Atlas is a proof-of-value B2B SaaS whose core product is an AI vendor-risk assessment. The end user uses Atlas; Woobe operates the AI product behind it.

The architectural boundary is deliberate:

- **Atlas owns case data:** users/tenants, assessments, uploaded vendor documents, extraction, evidence retrieval and the final business record.
- **Woobe owns the AI product:** Agents, Agent Network, controlled Knowledge, Tools, versions/releases, Runtime, Runs, Traces and Evaluations.
- Customer documents are **not** uploaded into Woobe Knowledge. Woobe Knowledge contains stable assessment methodology and policies. Agents obtain assessment-specific evidence through read-only Atlas HTTP Tools.

## MVP flow

```text
Atlas UI
  -> create assessment
  -> upload PDF/TXT/MD to Atlas
  -> Atlas extracts/chunks evidence
  -> Atlas backend calls Woobe POST /v1/run
  -> Atlas Vendor Risk Network
       -> Security Analyst
       -> Legal Analyst
       -> Compliance Analyst
       -> Risk Coordinator
  -> structured VendorAssessment
  -> Atlas stores and renders the result
```

## Run locally

Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8080
```

Open `http://localhost:8080`.

Before running an AI assessment, configure the Woobe project using [`woobe/SETUP.md`](woobe/SETUP.md).

## Woobe Runtime contract used by Atlas

The current Woobe `development-mvp` public runtime binds the target/environment to the Runtime Key and exposes:

```http
POST /v1/run
Authorization: Bearer <WOOBE_RUNTIME_KEY>
Content-Type: application/json
```

Atlas sends `message`, `tenant_id`, `user_id`, `metadata` and `idempotency_key`. The Network Release must have strict structured output enabled because Atlas persists `data.parsed_output`.

## Atlas Tool API

Woobe Agents call Atlas through read-only HTTP Tools:

- `GET /api/integrations/woobe/assessments/{assessment_id}`
- `GET /api/integrations/woobe/assessments/{assessment_id}/documents`
- `POST /api/integrations/woobe/assessments/{assessment_id}/evidence/search`
- `GET /api/integrations/woobe/assessments/{assessment_id}/evidence/{evidence_id}`

All require:

```http
Authorization: Bearer <ATLAS_WOOBE_TOOL_TOKEN>
```

The Woobe-side secret configuration is documented in `woobe/tools/`.

## Scope

This repository is an example product, not a full vendor-governance suite. The MVP intentionally excludes OCR, DOCX/XLSX parsing, production identity/RBAC, external compliance data providers and write-capable AI Tools.
