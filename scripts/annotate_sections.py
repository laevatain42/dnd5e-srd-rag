"""
给 SRD page JSONL 添加章节信息。
Annotate SRD page JSONL records with section metadata.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dnd5e_srd_rag import config
from dnd5e_srd_rag.jsonl import read_jsonl, write_jsonl
from dnd5e_srd_rag.sections import annotate_page_records


# 命令行入口。读取原始 pages JSONL，添加 section/include_in_rag，
# 然后写入 annotated pages JSONL。
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Annotate extracted SRD pages with section metadata."
    )
    parser.add_argument(
        "--pages",
        type=Path,
        default=config.DEFAULT_EXTRACTED_PAGES_PATH,
        help="Path to extracted page JSONL.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=config.DEFAULT_ANNOTATED_PAGES_PATH,
        help="Path to write annotated page JSONL.",
    )

    args = parser.parse_args()

    annotated_pages = annotate_page_records(read_jsonl(args.pages))
    count = write_jsonl(annotated_pages, args.out)

    print(f"Annotated {count} pages to {args.out}")


if __name__ == "__main__":
    main()