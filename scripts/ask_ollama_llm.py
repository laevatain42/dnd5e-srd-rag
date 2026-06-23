"""
使用本地 Ollama LLM 回答 SRD 问题。
Answer SRD questions with a local Ollama LLM.
"""

from __future__ import annotations

import argparse

from dnd5e_srd_rag import config
from dnd5e_srd_rag.ollama_answer import OllamaAnswerError, answer_with_ollama
from dnd5e_srd_rag.retrieval import (
    format_source,
    preview_text,
    retrieve_chunks,
    unique_sources,
)


# 打印由程序生成的确定性 sources，不让模型自由生成来源。
def print_sources(records: list[dict]) -> None:
    sources = unique_sources(records)

    print()
    print("Sources:")

    if not sources:
        print("- None")
        return

    for source in sources:
        print(f"- {source}")

# 打印实际传给 LLM 的检索上下文，方便调试 RAG 质量。
def print_context(records: list[dict], context_length: int) -> None:
    print()
    print("Retrieved Context:")

    if not records:
        print("- None")
        return

    for index, record in enumerate(records, start=1):
        source = format_source(record["metadata"])
        distance = record["distance"]

        print()
        print(f"[{index}] {source}")
        print(f"Distance: {distance:.4f}")
        print(preview_text(record["text"], limit=context_length))

# 命令行入口，检索 SRD context，并调用本地 Ollama 生成回答。
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Answer SRD questions with local Ollama."
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
        "--model",
        type=str,
        default=config.DEFAULT_OLLAMA_MODEL,
        help="Ollama model name, for example: llama3.1:8b.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=config.DEFAULT_OLLAMA_BASE_URL,
        help="Ollama base URL.",
    )
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Print retrieved context used for the LLM prompt.",
    )
    parser.add_argument(
        "--context-length",
        type=int,
        default=900,
        help="Maximum characters to print for each retrieved context chunk.",
    )

    args = parser.parse_args()

    records = retrieve_chunks(
        args.question,
        top_k=args.top_k,
        section=args.section,
    )

    if args.show_context:
        print_context(records, context_length=args.context_length)

    try:
        answer = answer_with_ollama(
            question=args.question,
            records=records,
            model=args.model,
            base_url=args.base_url,
        )
    except OllamaAnswerError as error:
        print("Ollama error:")
        print(error)
        print()
        print("Hints:")
        print(f"- Check Ollama is running: {args.base_url}")
        print(f"- Pull the model: ollama pull {args.model}")
        return

    print("Question:")
    print(args.question)
    print()
    print("Answer:")
    print(answer)

    print_sources(records)


if __name__ == "__main__":
    main()
