from __future__ import annotations

import hashlib
import io
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}


@dataclass(frozen=True)
class ExtractedSection:
    page_number: int | None
    text: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_sections(filename: str, data: bytes) -> list[ExtractedSection]:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError("Unsupported document type. Atlas MVP accepts PDF, TXT and MD.")

    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        sections: list[ExtractedSection] = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = normalize_text(page.extract_text() or "")
            if text:
                sections.append(ExtractedSection(page_number=page_number, text=text))
        if not sections:
            raise ValueError("PDF has no extractable text. OCR is outside the Atlas MVP.")
        return sections

    text = normalize_text(data.decode("utf-8"))
    if not text:
        raise ValueError("Document is empty.")
    return [ExtractedSection(page_number=None, text=text)]


def normalize_text(value: str) -> str:
    value = value.replace("\x00", " ")
    value = re.sub(r"\r\n?", "\n", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def chunk_sections(
    sections: list[ExtractedSection],
    *,
    target_chars: int = 1800,
    overlap_chars: int = 250,
) -> list[ExtractedSection]:
    chunks: list[ExtractedSection] = []
    for section in sections:
        text = section.text
        if len(text) <= target_chars:
            chunks.append(section)
            continue

        start = 0
        while start < len(text):
            end = min(len(text), start + target_chars)
            if end < len(text):
                boundary = max(
                    text.rfind("\n", start, end),
                    text.rfind(". ", start, end),
                )
                if boundary > start + target_chars // 2:
                    end = boundary + 1
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(ExtractedSection(section.page_number, chunk))
            if end >= len(text):
                break
            start = max(start + 1, end - overlap_chars)
    return chunks
