"""
根据词 检索 SRD chunks。
Search indexed SRD chunks.
"""

from __future__ import annotations

import argparse
from typing import Any

from dnd5e_srd_rag import config
from dnd5e_srd_rag.embeddings import embed_query
from dnd5e_srd_rag.vector_store import get_collection, query_chunks


# 压缩空白并截断文本，方便命令行显示。
def preview_text(text: str, limit: int = 500) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."

# 格式化来源引用，包含 SRD 版本、页码、section 和可选 subsection。
def format_source(metadata: dict[str, Any]) -> str:
    page = metadata.get("page", "unknown")
    section = metadata.get("section") or "unknown"
    subsection = metadata.get("subsection")

    parts = [
        f"SRD v{metadata.get('srd_version', config.SRD_VERSION)}",
        f"p. {page}",
        section,
    ]

    if subsection:
        parts.append(str(subsection))

    return ", ".join(parts)


# 把 Chroma query 结果打印成人类可读格式。
def print_results(
    results: dict[str, Any],
    top_k: int,
    preview_length: int,
) -> None:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    if not documents:
        print("No results found.")
        return

    for index, (chunk_id, document, metadata, distance) in enumerate(
        zip(ids, documents, metadatas, distances),
        start=1,
    ):
        print(f"\n[{index}/{top_k}] {chunk_id}")
        print(f"Source: {format_source(metadata)}")
        print(f"Distance: {distance:.4f}")
        print()
        print(preview_text(document, limit=preview_length))


# 执行一次语义检索。
def search(
    query: str,
    top_k: int,
    section: str | None,
) -> dict[str, Any]:
    query_embedding = embed_query(query)
    collection = get_collection()

    where = None
    if section:
        where = {"section": section}

    return query_chunks(
        query_embedding,
        collection,
        top_k=top_k,
        where=where,
    )


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

    results = search(
        args.query,
        top_k=args.top_k,
        section=args.section,
    )
    print_results(
        results,
        top_k=args.top_k,
        preview_length=args.preview_length,
    )


if __name__ == "__main__":
    main()
