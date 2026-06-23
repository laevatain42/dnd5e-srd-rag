"""
Ollama 本地 LLM 回答工具。
Ollama local LLM answer utilities.
"""

from __future__ import annotations

from typing import Any

import httpx

from dnd5e_srd_rag import config
from dnd5e_srd_rag.retrieval import format_source, preview_text

# 命名异常类
class OllamaAnswerError(RuntimeError):
    """Raised when Ollama cannot generate an answer."""
    pass

# 把检索到的 records 组装成给 LLM 使用的上下文。
def build_context(
    records: list[dict[str, Any]],
    max_chars_per_chunk: int = 1200,
) -> str:
    context_parts = []

    for index, record in enumerate(records, start=1):
        source = format_source(record["metadata"])
        text = preview_text(record["text"], limit=max_chars_per_chunk)

        context_parts.append(
            f"[{index}] Source: {source}\n"
            f"{text}"
        )

    return "\n\n".join(context_parts)


# 构建 Ollama /api/chat 需要的 messages。
def build_messages(
    question: str,
    records: list[dict[str, Any]],
) -> list[dict[str, str]]:
    context = build_context(records)

    system_message = (
        "You are a careful Dungeons & Dragons SRD rules assistant. "
        "Answer only from the provided SRD context. "
        "Do not use outside rules, house rules, or unsupported assumptions. "
        "If the context does not contain enough information, say that the current SRD context does not answer the question. "
        "Cite sources using the source labels provided in the context."
    )

    user_message = (
        "SRD context:\n"
        f"{context}\n\n"
        "Question:\n"
        f"{question}\n\n"
        "Answer with a concise rules explanation, then include a Sources section."
    )

    return [
        {
            "role": "system",
            "content": system_message,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]


# 调用本地 Ollama /api/chat，让 LLM 基于检索上下文生成回答。
def answer_with_ollama(
    question: str,
    records: list[dict[str, Any]],
    model: str = config.DEFAULT_OLLAMA_MODEL,
    base_url: str = config.DEFAULT_OLLAMA_BASE_URL,
    timeout: float = 180,
) -> str:
    if not records:
        return (
            "I could not find relevant SRD context for this question.\n\n"
            "Sources:\n"
            "- None"
        )

    messages = build_messages(question, records)

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    url = f"{base_url.rstrip('/')}/api/chat"

    try:
        response = httpx.post(
            url,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
    except httpx.ConnectError as error:
        raise OllamaAnswerError(
            f"Could not connect to Ollama at {base_url}. "
            "Make sure Ollama is installed and running. "
            "You can test it with: ollama --version"
        ) from error
    except httpx.TimeoutException as error:
        raise OllamaAnswerError(
            f"Ollama request timed out after {timeout} seconds. "
            f"The model '{model}' may still be loading or may be too slow for this machine."
        ) from error
    except httpx.HTTPStatusError as error:
        response_text = error.response.text
        raise OllamaAnswerError(
            f"Ollama returned HTTP {error.response.status_code} from {url}. "
            f"Model: {model}. Response: {response_text}"
        ) from error
    except httpx.HTTPError as error:
        raise OllamaAnswerError(
            f"Ollama request failed: {error}"
        ) from error

    try:
        data = response.json()
    except ValueError as error:
        raise OllamaAnswerError(
            f"Ollama returned a non-JSON response from {url}: {response.text}"
        ) from error

    answer = data.get("message", {}).get("content")
    if not answer:
        raise OllamaAnswerError(
            f"Ollama response did not contain message.content: {data}"
        )

    return answer.strip()
