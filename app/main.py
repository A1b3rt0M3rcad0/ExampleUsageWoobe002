from __future__ import annotations

import json
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import get_settings
from app.db import db, init_db
from app.documents import chunk_sections, extract_sections, sha256_bytes
from app.evidence import lexical_score
from app.woobe import WoobeRuntimeError, run_atlas_network


app = FastAPI(
    title="Atlas Vendor Risk",
    version="0.1.0",
    description="Example AI product powered by Woobe.",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_assessment(assessment_id: str):
    with db() as connection:
        row = connection.execute(
            "SELECT * FROM assessments WHERE id = ?",
            (assessment_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return row


def decode_assessment(row) -> dict:
    result = dict(row)
    result["data_handled"] = json.loads(result.pop("data_handled_json"))
    result["requirements"] = json.loads(result.pop("requirements_json"))
    raw_result = result.pop("result_json")
    result["result"] = json.loads(raw_result) if raw_result else None
    return result


def verify_woobe_tool_auth(authorization: str | None) -> None:
    settings = get_settings()
    expected = settings.atlas_woobe_tool_token
    if not expected:
        raise HTTPException(status_code=503, detail="Atlas Tool authentication is not configured.")
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="Invalid Atlas Tool credential.")


class AssessmentCreate(BaseModel):
    vendor_name: str = Field(min_length=2, max_length=200)
    category: str = Field(default="SaaS", min_length=2, max_length=120)
    criticality: str = Field(default="HIGH", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    region: str = Field(default="US / EU", min_length=2, max_length=120)
    data_handled: list[str] = Field(default_factory=lambda: ["PII"])
    requirements: list[str] = Field(
        default_factory=lambda: ["SECURITY", "LEGAL", "COMPLIANCE"]
    )


class EvidenceSearchInput(BaseModel):
    query: str = Field(min_length=2, max_length=1000)
    domain: str = Field(default="ALL", max_length=30)
    limit: int = Field(default=8, ge=1, le=20)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "product": "atlas"}


@app.get("/api/assessments")
def list_assessments():
    with db() as connection:
        rows = connection.execute(
            "SELECT * FROM assessments ORDER BY created_at DESC"
        ).fetchall()
    return {"items": [decode_assessment(row) for row in rows]}


@app.post("/api/assessments", status_code=201)
def create_assessment(payload: AssessmentCreate):
    assessment_id = f"ass_{uuid4().hex[:20]}"
    timestamp = now_iso()
    with db() as connection:
        connection.execute(
            """
            INSERT INTO assessments (
                id, tenant_id, vendor_name, category, criticality, region,
                data_handled_json, requirements_json, status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assessment_id,
                "atlas-demo",
                payload.vendor_name,
                payload.category,
                payload.criticality,
                payload.region,
                json.dumps(payload.data_handled),
                json.dumps(payload.requirements),
                "DRAFT",
                timestamp,
                timestamp,
            ),
        )
        row = connection.execute(
            "SELECT * FROM assessments WHERE id = ?",
            (assessment_id,),
        ).fetchone()
    return decode_assessment(row)


@app.get("/api/assessments/{assessment_id}")
def get_assessment(assessment_id: str):
    row = require_assessment(assessment_id)
    assessment = decode_assessment(row)
    with db() as connection:
        docs = connection.execute(
            """
            SELECT id, filename, media_type, sha256, byte_size, created_at
            FROM documents
            WHERE assessment_id = ?
            ORDER BY created_at
            """,
            (assessment_id,),
        ).fetchall()
    assessment["documents"] = [dict(doc) for doc in docs]
    return assessment


@app.post("/api/assessments/{assessment_id}/documents", status_code=201)
async def upload_document(assessment_id: str, file: UploadFile = File(...)):
    require_assessment(assessment_id)
    settings = get_settings()
    data = await file.read()
    if len(data) > settings.atlas_max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Document exceeds Atlas upload limit.")

    filename = Path(file.filename or "document").name
    digest = sha256_bytes(data)
    try:
        sections = extract_sections(filename, data)
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    document_id = f"doc_{uuid4().hex[:20]}"
    target_dir = settings.storage_path / assessment_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{document_id}{Path(filename).suffix.lower()}"
    media_type = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    timestamp = now_iso()
    chunks = chunk_sections(sections)

    try:
        with db() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id, assessment_id, filename, media_type, sha256,
                    byte_size, stored_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    assessment_id,
                    filename,
                    media_type,
                    digest,
                    len(data),
                    str(target_path),
                    timestamp,
                ),
            )
            for chunk_index, chunk in enumerate(chunks):
                connection.execute(
                    """
                    INSERT INTO evidence_chunks (
                        id, assessment_id, document_id, page_number,
                        chunk_index, content, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"ev_{uuid4().hex[:20]}",
                        assessment_id,
                        document_id,
                        chunk.page_number,
                        chunk_index,
                        chunk.text,
                        timestamp,
                    ),
                )
    except Exception as exc:
        if "UNIQUE constraint failed: documents.assessment_id, documents.sha256" in str(exc):
            raise HTTPException(
                status_code=409,
                detail="This document is already active in the assessment.",
            ) from exc
        raise

    target_path.write_bytes(data)
    return {
        "id": document_id,
        "assessment_id": assessment_id,
        "filename": filename,
        "sha256": digest,
        "byte_size": len(data),
        "chunks": len(chunks),
    }


@app.post("/api/assessments/{assessment_id}/analyze")
async def analyze_assessment(
    assessment_id: str,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    row = require_assessment(assessment_id)
    assessment = decode_assessment(row)
    with db() as connection:
        document_count = connection.execute(
            "SELECT COUNT(*) FROM documents WHERE assessment_id = ?",
            (assessment_id,),
        ).fetchone()[0]
    if document_count == 0:
        raise HTTPException(status_code=409, detail="Upload at least one evidence document.")

    runtime_idempotency_key = idempotency_key or f"atlas:{assessment_id}:{uuid4()}"
    with db() as connection:
        connection.execute(
            "UPDATE assessments SET status = ?, updated_at = ? WHERE id = ?",
            ("ANALYZING", now_iso(), assessment_id),
        )

    try:
        runtime = await run_atlas_network(
            assessment_id=assessment_id,
            required_domains=assessment["requirements"],
            idempotency_key=runtime_idempotency_key,
        )
    except WoobeRuntimeError as exc:
        with db() as connection:
            connection.execute(
                "UPDATE assessments SET status = ?, updated_at = ? WHERE id = ?",
                ("FAILED", now_iso(), assessment_id),
            )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    with db() as connection:
        connection.execute(
            """
            UPDATE assessments
            SET status = ?, result_json = ?, woobe_execution_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                "COMPLETED",
                json.dumps(runtime["result"]),
                runtime.get("execution_id"),
                now_iso(),
                assessment_id,
            ),
        )

    return runtime


# Woobe -> Atlas read-only Tool API.
@app.get("/api/integrations/woobe/assessments/{assessment_id}")
def tool_get_assessment(
    assessment_id: str,
    authorization: str | None = Header(default=None),
):
    verify_woobe_tool_auth(authorization)
    assessment = decode_assessment(require_assessment(assessment_id))
    return {
        "assessment_id": assessment["id"],
        "vendor": {
            "name": assessment["vendor_name"],
            "category": assessment["category"],
            "criticality": assessment["criticality"],
            "region": assessment["region"],
            "data_handled": assessment["data_handled"],
        },
        "required_domains": assessment["requirements"],
        "evidence_policy": (
            "Vendor-specific claims require evidence returned by Atlas evidence tools. "
            "Woobe Knowledge is policy, not vendor evidence."
        ),
    }


@app.get("/api/integrations/woobe/assessments/{assessment_id}/documents")
def tool_list_documents(
    assessment_id: str,
    authorization: str | None = Header(default=None),
):
    verify_woobe_tool_auth(authorization)
    require_assessment(assessment_id)
    with db() as connection:
        rows = connection.execute(
            """
            SELECT id, filename, media_type, sha256, byte_size, created_at
            FROM documents WHERE assessment_id = ? ORDER BY created_at
            """,
            (assessment_id,),
        ).fetchall()
    return {
        "assessment_id": assessment_id,
        "documents": [dict(row) for row in rows],
    }


@app.post("/api/integrations/woobe/assessments/{assessment_id}/evidence/search")
def tool_search_evidence(
    assessment_id: str,
    payload: EvidenceSearchInput,
    authorization: str | None = Header(default=None),
):
    verify_woobe_tool_auth(authorization)
    require_assessment(assessment_id)
    with db() as connection:
        rows = connection.execute(
            """
            SELECT
                c.id AS evidence_id,
                c.document_id,
                d.filename AS document_name,
                c.page_number,
                c.chunk_index,
                c.content
            FROM evidence_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.assessment_id = ?
            """,
            (assessment_id,),
        ).fetchall()

    ranked = []
    for row in rows:
        score = lexical_score(payload.query, row["content"])
        if score <= 0:
            continue
        item = dict(row)
        item["score"] = score
        item["content"] = item["content"][:2200]
        ranked.append(item)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return {
        "assessment_id": assessment_id,
        "query": payload.query,
        "domain": payload.domain,
        "results": ranked[: payload.limit],
    }


@app.get("/api/integrations/woobe/assessments/{assessment_id}/evidence/{evidence_id}")
def tool_get_evidence(
    assessment_id: str,
    evidence_id: str,
    authorization: str | None = Header(default=None),
):
    verify_woobe_tool_auth(authorization)
    require_assessment(assessment_id)
    with db() as connection:
        row = connection.execute(
            """
            SELECT
                c.id AS evidence_id,
                c.document_id,
                d.filename AS document_name,
                c.page_number,
                c.chunk_index,
                c.content
            FROM evidence_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.assessment_id = ? AND c.id = ?
            """,
            (assessment_id, evidence_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    return dict(row)


static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")
