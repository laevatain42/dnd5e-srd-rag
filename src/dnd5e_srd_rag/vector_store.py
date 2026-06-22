"""
Chroma 向量库工具。
Chroma vector store utilities.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from dnd5e_srd_rag import config


# 清洗 Chroma metadata。Chroma 不接受 None，只接受 str/int/float/bool。
def sanitize_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
    sanitized: dict[str, str | int | float | bool] = {}

    for key, value in metadata.items():
        if value is None:
            sanitized[key] = ""
        elif isinstance(value, str | int | float | bool):
            sanitized[key] = value
        else:
            sanitized[key] = str(value)

    return sanitized


# 创建一个持久化 Chroma client，数据会写入本地目录。默认目录在config.DEFAULT_CHROMA_PATH。
def get_chroma_client(path: Path = config.DEFAULT_CHROMA_PATH):
    """创建 Chroma persistent client。"""
    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(path))


# 获取或创建 SRD collection。默认名：DEFAULT_CHROMA_COLLECTION
def get_collection(
    collection_name: str = config.DEFAULT_CHROMA_COLLECTION,
    path: Path = config.DEFAULT_CHROMA_PATH,
) -> Collection:

    client = get_chroma_client(path)
    return client.get_or_create_collection(name=collection_name)


# 把 chunk records 和 embeddings 写入 Chroma。
def add_chunks(
    chunks: list[dict[str, Any]],
    embeddings: list[list[float]],
    collection: Collection,
) -> None:
    """写入 chunks 和对应 embeddings。"""
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"chunks and embeddings length mismatch: {len(chunks)} != {len(embeddings)}"
        )

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [sanitize_metadata(chunk["metadata"]) for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


# 根据embedding向量，查询 Chroma，返回最相似的 chunks。
def query_chunks(
    query_embedding: list[float],
    collection: Collection,
    top_k: int = config.DEFAULT_TOP_K,
    where: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """根据 query embedding 检索相似 chunks。"""
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
