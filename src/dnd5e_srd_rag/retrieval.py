"""
检索与引用格式化工具。
Retrieval and citation formatting utilities.
"""

from __future__ import annotations

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


# 从 Chroma 查询结果中提取扁平化 result records。
def flatten_results(results: dict[str, Any]) -> list[dict[str, Any]]:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    flattened = []

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        flattened.append(
            {
                "chunk_id": chunk_id,
                "text": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return flattened


# 去重来源引用，返回唯一的来源列表。
def unique_sources(records: list[dict[str, Any]]) -> list[str]:
    seen = set()
    sources = []

    for record in records:
        source = format_source(record["metadata"])
        if source in seen:
            continue

        seen.add(source)
        sources.append(source)

    return sources


# 检索问题相关 chunks，可选按 section 过滤。
def retrieve_chunks(
    query: str,
    top_k: int = config.DEFAULT_TOP_K,
    section: str | None = None,
) -> list[dict[str, Any]]:
    query_embedding = embed_query(query)
    collection = get_collection()

    where = None
    if section:
        where = {"section": section}

    results = query_chunks(
        query_embedding,
        collection,
        top_k=top_k,
        where=where,
    )

    return flatten_results(results)