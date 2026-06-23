"""
根据词 检索 SRD chunks。
Search indexed SRD chunks.
"""

from __future__ import annotations

import argparse
from typing import Any

from dnd5e_srd_rag import config

from dnd5e_srd_rag.retrieval import format_source, preview_text, retrieve_chunks


# 把检索 records 打印成人类可读的开发者调试格式。
def print_results(
    records: list[dict[str, Any]],
    preview_length: int,
) -> None:
    if not records:
        print("No results found.")
        return

    result_count = len(records)

    for index, record in enumerate(records, start=1):
        chunk_id = record["chunk_id"]
        document = record["text"]
        metadata = record["metadata"]
        distance = record["distance"]

        print(f"\n[{index}/{result_count}] {chunk_id}")
        print(f"Source: {format_source(metadata)}")
        print(f"Distance: {distance:.4f}")
        print()
        print(preview_text(document, limit=preview_length))


# 命令行入口，解析用户问题并输出检索结果。
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search indexed SRD chunks."
    )
    parser.add_argument(
        "query",
        type=str,
        help="Rules question or search query.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=config.DEFAULT_TOP_K,
        help="Number of chunks to retrieve.",
    )
    parser.add_argument(
        "--section",
        type=str,
        default=None,
        help="Optional section filter, for example: Classes, Spells, Monsters.",
    )
    parser.add_argument(
        "--preview-length",
        type=int,
        default=500,
        help="Maximum number of characters to show for each result.",
    )

    args = parser.parse_args()

    records = retrieve_chunks(
        args.query,
        top_k=args.top_k,
        section=args.section,
    )
    print_results(
        records,
        preview_length=args.preview_length,
    )


if __name__ == "__main__":
    main()
