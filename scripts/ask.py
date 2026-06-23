"""
基于检索结果回答 SRD 问题。
Answer SRD questions from retrieved context.
"""

from __future__ import annotations

import argparse
from typing import Any

from dnd5e_srd_rag import config
from dnd5e_srd_rag.retrieval import (
    format_source,
    preview_text,
    retrieve_chunks,
    unique_sources,
)


# 打印不调用 LLM 的引用式回答。LLM部分后面再做。
def print_answer(
    question: str,
    records: list[dict[str, Any]],
    context_length: int,
) -> None:
    print("Question:")
    print(question)

    if not records:
        print()
        print("Answer:")
        print("No relevant SRD context was found.")
        return

    print()
    print("Relevant SRD Context:")

    for index, record in enumerate(records, start=1):
        source = format_source(record["metadata"])
        distance = record["distance"]

        print()
        print(f"{index}. {source}")
        print(f"   Chunk: {record['chunk_id']}")
        print(f"   Distance: {distance:.4f}")
        print(f"   {preview_text(record['text'], limit=context_length)}")

    print()
    print("Sources:")

    for source in unique_sources(records):
        print(f"- {source}")


# 命令行入口。
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Answer SRD questions from retrieved context."
    )
    parser.add_argument(
        "question",
        type=str,
        help="Rules question.",
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
        "--context-length",
        type=int,
        default=900,
        help="Maximum characters to print for each retrieved chunk.",
    )

    args = parser.parse_args()

    records = retrieve_chunks(
        args.question,
        top_k=args.top_k,
        section=args.section,
    )

    print_answer(
        args.question,
        records=records,
        context_length=args.context_length,
    )


if __name__ == "__main__":
    main()