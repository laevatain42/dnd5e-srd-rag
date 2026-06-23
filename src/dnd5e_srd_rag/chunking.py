"""
从PAGE的JSONL拆分Chunk
Chunk extracted SRD pages for retrieval.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from typing import Any

from dnd5e_srd_rag import config

# Chunk 大小
DEFAULT_CHUNK_SIZE = 1200
# Chunk 重叠部分大小，确保上下文连续性
DEFAULT_CHUNK_OVERLAP = 200

# 从文本尾部截取指定长度，并尽量从完整单词开始。
def take_text_tail(text: str, max_length: int) -> str:
    if max_length <= 0:
        return ""

    text = " ".join(text.split())

    if len(text) <= max_length:
        return text

    tail = text[-max_length:].strip()
    first_space = tail.find(" ")

    if first_space == -1:
        return tail

    return tail[first_space + 1 :].strip()

# 从上一个 chunk 中取完整句子作为 overlap，避免从单词中间截断。
def build_overlap_text(text: str, chunk_overlap: int) -> str:
    if chunk_overlap <= 0:
        return ""

    units = split_sentences(text)
    selected: list[str] = []
    total_length = 0

    for unit in reversed(units):
        unit_length = len(unit) + (1 if selected else 0)

        if unit_length > chunk_overlap and not selected:
            return take_text_tail(unit, chunk_overlap)

        if selected and total_length + unit_length > chunk_overlap:
            break

        selected.append(unit)
        total_length += unit_length

        if total_length >= chunk_overlap:
            break

    selected.reverse()
    return " ".join(selected).strip()

# 转换句子为chunk-id友好的slug
def slugify(value: str | None) -> str:
    """Convert metadata text to a chunk-id friendly slug."""
    if not value:
        return "unknown"

    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")

    return value or "unknown"

# 把一段文本拆成句子，尽量避免 chunk 在句子中间断开。
def split_sentences(text: str) -> list[str]:
    text = " ".join(text.split())

    if not text:
        return []

    return re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'])", text)

# 把文本拆成适合组装 chunk 的单位：标题行或句子。
def split_units(text: str) -> list[str]:
    units = []

    for line in text.splitlines():
        line = " ".join(line.split())

        if not line:
            continue

        if re.match(r"^Level \d+:", line):
            units.append(line)
            continue

        units.extend(split_sentences(line))

    return [unit for unit in units if unit]

# 把单个超长文本片段按字符切开，作为兜底方案。
def split_long_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """把单个超长文本片段按字符切开，作为兜底方案。"""
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())

        if end == len(text):
            break

        start = end - chunk_overlap

    return [chunk for chunk in chunks if chunk]

# 分割文本为重叠的chunks，按句子累积生成 chunks，尽量不在句子中间切断。
def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    units = split_units(text)

    chunks = []
    current = ""

    for unit in units:
        if len(unit) > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""

            chunks.extend(split_long_text(unit, chunk_size, chunk_overlap))
            continue

        candidate = f"{current} {unit}".strip()

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current.strip())

        overlap_text = build_overlap_text(chunks[-1], chunk_overlap) if chunks else ""
        current = f"{overlap_text} {unit}".strip() if overlap_text else unit


    if current:
        chunks.append(current.strip())

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
        # 如果 include_in_rag 是 False，跳过这个页面，不生成 chunk。
        if page_record.get("include_in_rag") is False:
            continue
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
