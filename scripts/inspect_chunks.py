"""
检查生成的 SRD chunks JSONL.
Inspect generated SRD chunk JSONL.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

from dnd5e_srd_rag import config
from dnd5e_srd_rag.jsonl import read_jsonl


REQUIRED_FIELDS = {
    "chunk_id",
    "text",
    "metadata",
}

REQUIRED_METADATA_FIELDS = {
    "source",
    "source_url",
    "document_title",
    "ruleset",
    "srd_version",
    "language",
    "license",
    "published_date",
    "page",
    "section",
    "subsection",
}


# 安全打印文本，避免 Windows 控制台编码导致检查脚本失败。
def safe_print(value: object = "") -> None:
    text = str(value)
    encoding = "utf-8"

    try:
        import sys

        encoding = sys.stdout.encoding or encoding
    except Exception:
        pass

    print(text.encode(encoding, errors="replace").decode(encoding))


# 压缩空白并截断文本，方便命令行预览。
def preview_text(text: str, limit: int = 220) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


# 判断 chunk 开头是否像半截词或不自然的残片。
def looks_like_fragment_start(text: str) -> bool:
    stripped = text.strip()

    if not stripped:
        return False

    first_word = stripped.split(maxsplit=1)[0]

    if re.match(r"^[a-z]{1,3}\.$", first_word):
        return True

    if re.match(r"^[a-z]{1,3}$", first_word):
        return True

    return False


# 确认单条 chunk 记录具备必要字段和合法 metadata。
def validate_chunk_record(index: int, record: dict[str, Any]) -> None:
    missing = REQUIRED_FIELDS - set(record)
    if missing:
        raise ValueError(f"Record {index} missing required fields: {sorted(missing)}")

    chunk_id = record.get("chunk_id")
    text = record.get("text")
    metadata = record.get("metadata")

    if not isinstance(chunk_id, str) or not chunk_id:
        raise ValueError(f"Record {index} has invalid chunk_id: {chunk_id!r}")

    if not isinstance(text, str):
        raise ValueError(f"Record {index} has invalid text value.")

    if not isinstance(metadata, dict):
        raise ValueError(f"Record {index} has invalid metadata value.")

    metadata_missing = REQUIRED_METADATA_FIELDS - set(metadata)
    if metadata_missing:
        raise ValueError(
            f"Record {index} missing metadata fields: {sorted(metadata_missing)}"
        )

    page = metadata.get("page")
    if not isinstance(page, int):
        raise ValueError(f"Record {index} has invalid metadata.page: {page!r}")


# 读取 chunks JSONL，检查字段、长度、章节分布和明显异常。
def inspect_chunks(
    path: Path,
    preview_count: int,
    page: int | None,
    max_length: int,
) -> int:
    records = list(read_jsonl(path))

    if not records:
        raise ValueError(f"No records found in {path}")

    for index, record in enumerate(records, start=1):
        validate_chunk_record(index, record)

    filtered_records = [
        record
        for record in records
        if page is None or record["metadata"]["page"] == page
    ]

    if page is not None and not filtered_records:
        raise ValueError(f"No chunks found for page {page}")

    lengths = [len(record["text"]) for record in filtered_records]
    sections = Counter(record["metadata"].get("section") for record in records)

    empty_text_chunks = [
        record for record in filtered_records if not record["text"].strip()
    ]
    over_max_chunks = [
        record for record in filtered_records if len(record["text"]) > max_length
    ]
    front_matter_chunks = [
        record for record in records if record["metadata"]["page"] <= 4
    ]
    unknown_section_chunks = [
        record for record in records if not record["metadata"].get("section")
    ]
    unknown_subsection_chunks = [
        record for record in records if not record["metadata"].get("subsection")
    ]
    header_chunks = [
        record
        for record in filtered_records
        if f"System Reference Document {config.SRD_VERSION}" in record["text"]
    ]
    fragment_starts = [
        record for record in filtered_records if looks_like_fragment_start(record["text"])
    ]

    safe_print(f"File: {path}")
    safe_print(f"Chunks checked: {len(filtered_records)}")
    safe_print(f"Total chunks in file: {len(records)}")

    if lengths:
        safe_print(f"Min length: {min(lengths)}")
        safe_print(f"Max length: {max(lengths)}")
        safe_print(f"Avg length: {sum(lengths) / len(lengths):.1f}")

    safe_print(f"Empty text chunks: {len(empty_text_chunks)}")
    safe_print(f"Chunks over max length ({max_length}): {len(over_max_chunks)}")
    safe_print(f"Front matter chunks, pages 1-4: {len(front_matter_chunks)}")
    safe_print(f"Chunks missing section: {len(unknown_section_chunks)}")
    safe_print(f"Chunks missing subsection: {len(unknown_subsection_chunks)}")
    safe_print(f"Chunks containing SRD page header: {len(header_chunks)}")
    safe_print(f"Chunks with suspicious fragment starts: {len(fragment_starts)}")

    safe_print()
    safe_print("Section distribution:")
    for section, count in sections.items():
        safe_print(f"- {section}: {count}")

    if fragment_starts:
        safe_print()
        safe_print("Suspicious fragment examples:")
        for record in fragment_starts[:preview_count]:
            safe_print(f"- {record['chunk_id']}: {preview_text(record['text'], 80)}")

    safe_print()
    safe_print("Preview:")
    for record in filtered_records[:preview_count]:
        metadata = record["metadata"]
        section = metadata.get("section") or "unknown"
        subsection = metadata.get("subsection") or "unknown"

        safe_print(
            f"- {record['chunk_id']} "
            f"(page {metadata['page']}, {section} > {subsection}, "
            f"len {len(record['text'])})"
        )
        safe_print(f"  {preview_text(record['text'])}")

    return len(filtered_records)


# 命令行入口，解析检查参数并运行 chunks 检查。
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect generated SRD chunk JSONL."
    )
    parser.add_argument(
        "--chunks",
        type=Path,
        default=config.DEFAULT_CHUNKS_PATH,
        help="Path to chunk JSONL.",
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=5,
        help="Number of chunks to preview.",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=None,
        help="Only inspect chunks from this page.",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=1800,
        help="Expected maximum chunk text length.",
    )

    args = parser.parse_args()

    inspect_chunks(
        args.chunks,
        preview_count=args.preview_count,
        page=args.page,
        max_length=args.max_length,
    )


if __name__ == "__main__":
    main()
