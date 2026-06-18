"""
分割PDF页面为JSONL格式的记录。
Extract SRD PDF pages into JSONL.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dnd5e_srd_rag import config
from dnd5e_srd_rag.pdf_extract import extract_pages


def write_jsonl(records: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract text and page metadata from the SRD PDF."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=config.DEFAULT_PDF_PATH,
        help="Path to the source SRD PDF.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=config.DEFAULT_EXTRACTED_PAGES_PATH,
        help="Path to write extracted page JSONL.",
    )

    args = parser.parse_args()

    records = list(extract_pages(args.pdf))
    write_jsonl(records, args.out)

    print(f"Extracted {len(records)} pages to {args.out}")


if __name__ == "__main__":
    main()