"""
文本向量化工具。
Text embedding utilities.
"""

from __future__ import annotations

from collections.abc import Sequence

from sentence_transformers import SentenceTransformer

from dnd5e_srd_rag import config


# 缓存已加载的 embedding 模型，避免重复加载。
_MODEL: SentenceTransformer | None = None


# sentence-transformers 模型，初步选用config.DEFAULT_EMBEDDING_MODEL，即 Qwen/Qwen3-Embedding-0.6B，后续可根据需要调整。
def get_embedding_model(
    model_name: str = config.DEFAULT_EMBEDDING_MODEL,
) -> SentenceTransformer:
    """加载并缓存 embedding 模型。"""
    global _MODEL

    if _MODEL is None:
        try:
            _MODEL = SentenceTransformer(model_name)
        except Exception:
            _MODEL = SentenceTransformer(model_name, local_files_only=True)

    return _MODEL


# 把文本列表转换为 embedding 向量列表，即把我的jsonl中的text字段转换为向量，后续存储到 ChromaDB 中。
def embed_texts(
    texts: Sequence[str],
    model_name: str = config.DEFAULT_EMBEDDING_MODEL,
) -> list[list[float]]:
    """生成文本 embeddings。"""
    model = get_embedding_model(model_name)

    embeddings = model.encode(
        list(texts),
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return embeddings.tolist()


# 把单个查询文本转换为 embedding 向量，就是我的问题。
def embed_query(
    query: str,
    model_name: str = config.DEFAULT_EMBEDDING_MODEL,
) -> list[float]:
    """生成查询 embedding。"""
    return embed_texts([query], model_name=model_name)[0]
