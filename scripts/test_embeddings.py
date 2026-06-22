"""
测试 embedding 模型是否能正常加载和生成向量。
"""

from __future__ import annotations

from dnd5e_srd_rag import config
from dnd5e_srd_rag.embeddings import embed_texts


# 命令行入口。加载默认 embedding 模型，并生成几条测试向量。
def main() -> None:
    texts = [
        "A creature can take one action on its turn.",
        "The Cleric prepares spells after finishing a Long Rest.",
        "Fireball deals fire damage in an area.",
    ]

    embeddings = embed_texts(texts)

    print(f"Model: {config.DEFAULT_EMBEDDING_MODEL}")
    print(f"Texts: {len(texts)}")
    print(f"Embeddings: {len(embeddings)}")

    if embeddings:
        print(f"Embedding dimension: {len(embeddings[0])}")
        print(f"First vector preview: {embeddings[0][:5]}")


if __name__ == "__main__":
    print("Testing embedding model loading and vector generation...")
    main()