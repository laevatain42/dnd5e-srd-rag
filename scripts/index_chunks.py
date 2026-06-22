"""
把 SRD chunks 写入 Chroma 向量库。
Index SRD chunks into the Chroma vector store.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from dnd5e_srd_rag import config
from dnd5e_srd_rag.embeddings import embed_texts
from dnd5e_srd_rag.jsonl import read_jsonl
from dnd5e_srd_rag.vector_store import add_chunks, get_collection


# 把列表按固定大小切成多个 batch。
def batched(items: list[dict[str, Any]], batch_size: int):
    """按 batch_size 分批产出列表片段。"""
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


# 读取 chunks，生成 embeddings，并写入 Chroma。
def index_chunks(
    chunks_path: Path,
    batch_size: int,
    reset: bool,
) -> int:
    # 读取 chunks 数据。每条记录应该包含 chunk_id, text, metadata。
    chunks = list(read_jsonl(chunks_path))

    if not chunks:
        raise ValueError(f"No chunks found in {chunks_path}")
    
    # 获取collection
    collection = get_collection()

    if reset:
        # 删除已有 collection 里的数据最简单的方式，是删除 collection 后重建。
        from dnd5e_srd_rag.vector_store import get_chroma_client

        client = get_chroma_client()
        client.delete_collection(config.DEFAULT_CHROMA_COLLECTION)
        collection = get_collection()

    total = 0

    # 按 batch_size 分批处理 chunks，生成 embeddings，并写入 Chroma。
    for batch in batched(chunks, batch_size):
        texts = [chunk["text"] for chunk in batch]
        embeddings = embed_texts(texts)

        add_chunks(batch, embeddings, collection)

        total += len(batch)
        print(f"Indexed {total}/{len(chunks)} chunks")

    return total


# 命令行入口，解析参数并执行索引。
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index SRD chunks into Chroma."
    )
    parser.add_argument(
        "--chunks",
        type=Path,
        default=config.DEFAULT_CHUNKS_PATH,
        help="Path to chunk JSONL.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Embedding/indexing batch size.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and rebuild the Chroma collection before indexing.",
    )

    args = parser.parse_args()

    count = index_chunks(
        chunks_path=args.chunks,
        batch_size=args.batch_size,
        reset=args.reset,
    )

    print(f"Indexed {count} chunks into {config.DEFAULT_CHROMA_COLLECTION}")


if __name__ == "__main__":
    main()