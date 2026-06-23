"""
供 API 和未来 UI 使用的 RAG 问答服务
RAG chat service used by API and future UI
"""

from __future__ import annotations

from typing import Any

from dnd5e_srd_rag import config
from dnd5e_srd_rag.ollama_answer import answer_with_ollama
from dnd5e_srd_rag.retrieval import retrieve_chunks, unique_sources

# 引用溯源
def build_source_items(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build structured source items from retrieved records."""
    sources = []

    for source in unique_sources(records):
        sources.append({"label": source})

    return sources

# 构建和ollama聊天内容。
def chat_with_srd(
    question: str,
    top_k: int = config.DEFAULT_TOP_K,
    section: str | None = None,
    model: str = config.DEFAULT_OLLAMA_MODEL,
    base_url: str = config.DEFAULT_OLLAMA_BASE_URL,
) -> dict[str, Any]:
    """Retrieve SRD chunks, ask Ollama, and return answer plus deterministic sources."""
    records = retrieve_chunks(
        question,
        top_k=top_k,
        section=section,
    )

    answer = answer_with_ollama(
        question=question,
        records=records,
        model=model,
        base_url=base_url,
    )

    return {
        "answer": answer,
        "sources": build_source_items(records),
    }