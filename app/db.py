from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from app.config import get_settings


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS assessments (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    vendor_name TEXT NOT NULL,
    category TEXT NOT NULL,
    criticality TEXT NOT NULL,
    region TEXT NOT NULL,
    data_handled_json TEXT NOT NULL,
    requirements_json TEXT NOT NULL,
    status TEXT NOT NULL,
    result_json TEXT,
    woobe_execution_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    media_type TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    byte_size INTEGER NOT NULL,
    stored_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    UNIQUE (assessment_id, sha256)
);

CREATE TABLE IF NOT EXISTS evidence_chunks (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    page_number INTEGER,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_assessment
    ON evidence_chunks(assessment_id);

CREATE INDEX IF NOT EXISTS idx_chunks_document
    ON evidence_chunks(document_id);
"""


def init_db() -> None:
    settings = get_settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.database_path) as connection:
        connection.executescript(SCHEMA)


@contextmanager
def db():
    settings = get_settings()
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
