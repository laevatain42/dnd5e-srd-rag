"""
从JSONL拆分Chunk
Chunk extracted SRD pages for retrieval.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from typing import Any

from dnd5e_srd_rag import config

# Chunk 大小
DEFAULT_CHUNK_SIZE = 3200
# Chunk 重叠部分大小，确保上下文连续性
DEFAULT_CHUNK_OVERLAP = 400

# 转换句子为chunk-id友好的slug
def slugify(value: str | None) -> str:
    """Convert metadata text to a chunk-id friendly slug."""
    if not value:
        return "unknown"

    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")

    return value or "unknown"

# 分割文本为重叠的chunk
def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping character chunks."""
    text = " ".join(text.split())

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - chunk_overlap

    return chunks

# 构建chunk id
def build_chunk_id(
    page: int,
    section: str | None,
    subsection: str | None,
    index: int,
) -> str:
    """Build a stable chunk id."""
    section_slug = slugify(section)
    subsection_slug = slugify(subsection)

    return (
        f"srd-{config.SRD_VERSION}-"
        f"{config.SRD_LANGUAGE}-"
        f"p{page}-"
        f"{section_slug}-"
        f"{subsection_slug}-"
        f"{index:03d}"
    )

# 整理chunk的metadata
def build_metadata(page_record: dict[str, Any]) -> dict[str, Any]:
    """Build retrieval metadata for a chunk."""
    return {
        "source": page_record.get("source", config.SRD_SOURCE),
        "source_url": page_record.get("source_url", config.SRD_SOURCE_URL),
        "document_title": page_record.get(
            "document_title",
            config.SRD_DOCUMENT_TITLE,
        ),
        "ruleset": page_record.get("ruleset", config.SRD_RULESET),
        "srd_version": page_record.get("srd_version", config.SRD_VERSION),
        "language": page_record.get("language", config.SRD_LANGUAGE),
        "license": page_record.get("license", config.SRD_LICENSE),
        "published_date": page_record.get(
            "published_date",
            config.SRD_PUBLISHED_DATE,
        ),
        "page": page_record["page"],
        "section": page_record.get("section"),
        "subsection": page_record.get("subsection"),
    }

# 主函数，并行，pages in chunks out
def chunk_pages(
    page_records: Iterable[dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> Iterator[dict[str, Any]]:
    """Yield chunk records from extracted page records."""
    for page_record in page_records:
        page = page_record["page"]
        section = page_record.get("section")
        subsection = page_record.get("subsection")
        text = page_record.get("text", "")

        page_chunks = split_text(text, chunk_size, chunk_overlap)

        for index, chunk_text in enumerate(page_chunks, start=1):
            yield {
                "chunk_id": build_chunk_id(page, section, subsection, index),
                "text": chunk_text,
                "metadata": build_metadata(page_record),
            }