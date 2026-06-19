"""
PDF 文字提取工具.
PDF text extraction utilities.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import re
import fitz

from dnd5e_srd_rag import config

# 从PDF中提取页面文本和元数据，clean_page_text去除页眉和页码等干扰信息
def extract_pages(pdf_path: Path) -> Iterator[dict[str, Any]]:
    """Extract text from a PDF one page at a time."""
    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            # text = page.get_text("text").strip()
            raw_text = page.get_text("text")
            text = clean_page_text(raw_text, page_index + 1)
            yield {
                "source": config.SRD_SOURCE,
                "source_url": config.SRD_SOURCE_URL,
                "document_title": config.SRD_DOCUMENT_TITLE,
                "ruleset": config.SRD_RULESET,
                "srd_version": config.SRD_VERSION,
                "language": config.SRD_LANGUAGE,
                "license": config.SRD_LICENSE,
                "published_date": config.SRD_PUBLISHED_DATE,
                "page": page_index + 1,
                "text": text,
            }

# 判断两行文本是否看起来像是一个被换行分开的句子
def should_join_lines(previous: str, current: str) -> bool:
    """Return whether two PDF text lines look like one wrapped sentence."""
    if not previous or not current:
        return False

    if previous.endswith((".", "!", "?", ":", ";")):
        return False

    if current[0].isupper() and len(current.split()) <= 6:
        return False

    if looks_like_heading(previous) or looks_like_heading(current):
        return False

    return True

# 判断一行是否像规则标题或小标题。
def looks_like_heading(line: str) -> bool:
    if re.match(r"^Level \d+:", line):
        return True

    if len(line) <= 80 and line.endswith(".") and len(line.split()) <= 6:
        return True

    if len(line) <= 80 and ":" in line and len(line.split()) <= 8:
        return True

    return False

# 清理页面文本，去除页眉和页码等干扰信息
def clean_page_text(text: str, page_number: int) -> str:
    """Remove simple SRD headers/page numbers and merge soft-wrapped lines."""
    cleaned_lines = []

    for line in text.splitlines():
        normalized = " ".join(line.split())

        if not normalized:
            continue

        if normalized == f"System Reference Document {config.SRD_VERSION}":
            continue

        if normalized == str(page_number):
            continue

        cleaned_lines.append(normalized)

    merged_lines = []

    for line in cleaned_lines:
        if merged_lines and merged_lines[-1].endswith("-"):
            merged_lines[-1] = f"{merged_lines[-1][:-1]}{line}"
        elif merged_lines and should_join_lines(merged_lines[-1], line):
            merged_lines[-1] = f"{merged_lines[-1]} {line}"
        else:
            merged_lines.append(line)

    return "\n".join(merged_lines).strip()