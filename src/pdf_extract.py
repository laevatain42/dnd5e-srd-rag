"""PDF 文字提取工具."""

"""PDF text extraction utilities."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import fitz

from dnd5e_srd_rag import config


def extract_pages(pdf_path: Path) -> Iterator[dict[str, Any]]:
    """Extract text from a PDF one page at a time."""
    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            text = page.get_text("text").strip()

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