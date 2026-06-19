"""
JSONL to chunks
Chunk extracted SRD pages into JSONL."""

from __future__ import annotations

import argparse
from pathlib import Path

from dnd5e_srd_rag import config
from dnd5e_srd_rag.chunking import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    chunk_pages,
)
from dnd5e_srd_rag.jsonl import read_jsonl, write_jsonl


# 读取pages JSONL，切成chunks，写入新的JSONL
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chunk extracted SRD pages into retrieval records."
    )
    parser.add_argument(
        "--pages",
        type=Path,
        default=config.DEFAULT_EXTRACTED_PAGES_PATH,
        help="Path to extracted page JSONL.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=config.DEFAULT_CHUNKS_PATH,
        help="Path to write chunk JSONL.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Chunk size in characters.",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=DEFAULT_CHUNK_OVERLAP,
        help="Chunk overlap in characters.",
    )

    args = parser.parse_args()

    chunks = chunk_pages(
        read_jsonl(args.pages),
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    count = write_jsonl(chunks, args.out)

    print(f"Wrote {count} chunks to {args.out}")


if __name__ == "__main__":
    main()