"""
检查提取的SRD页面JSONL.
Inspect extracted SRD page JSONL.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dnd5e_srd_rag import config
from dnd5e_srd_rag.jsonl import read_jsonl


REQUIRED_FIELDS = {
    "source",
    "source_url",
    "document_title",
    "ruleset",
    "srd_version",
    "language",
    "license",
    "published_date",
    "page",
    "text",
}


def preview_text(text: str, limit: int = 160) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def inspect_pages(path: Path, preview_count: int) -> int:
    records = list(read_jsonl(path))

    if not records:
        raise ValueError(f"No records found in {path}")

    missing_required = []
    empty_text_pages = []
    page_numbers = []

    for index, record in enumerate(records, start=1):
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            missing_required.append((index, sorted(missing)))

        page = record.get("page")
        if not isinstance(page, int):
            raise ValueError(f"Record {index} has invalid page value: {page!r}")

        page_numbers.append(page)

        text = record.get("text")
        if not isinstance(text, str):
            raise ValueError(f"Record {index} has invalid text value.")

        if not text.strip():
            empty_text_pages.append(page)

    expected_pages = list(range(1, len(records) + 1))
    if page_numbers != expected_pages:
        raise ValueError(
            "Page numbers are not sequential from 1. "
            f"First mismatch: expected {expected_pages[:10]}, got {page_numbers[:10]}"
        )

    if missing_required:
        examples = missing_required[:5]
        raise ValueError(f"Records missing required fields: {examples}")

    print(f"File: {path}")
    print(f"Pages: {len(records)}")
    print(f"Empty text pages: {len(empty_text_pages)}")

    if empty_text_pages:
        print(f"Empty page numbers: {empty_text_pages[:20]}")

    print()
    print("Preview:")

    for record in records[:preview_count]:
        print(f"- Page {record['page']}: {preview_text(record['text'])}")

    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect extracted SRD page JSONL."
    )
    parser.add_argument(
        "--pages",
        type=Path,
        default=config.DEFAULT_EXTRACTED_PAGES_PATH,
        help="Path to extracted page JSONL.",
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=5,
        help="Number of initial pages to preview.",
    )

    args = parser.parse_args()

    inspect_pages(args.pages, args.preview_count)


if __name__ == "__main__":
    main()