"""项目配置 和 SRD 元数据."""

"""Project configuration and SRD metadata."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
EXTRACTED_DATA_DIR = DATA_DIR / "extracted"
CHUNKS_DATA_DIR = DATA_DIR / "chunks"
VECTORSTORES_DIR = DATA_DIR / "vectorstores"
INDEXES_DIR = DATA_DIR / "indexes"

SRD_VERSION = "5.2.1"
SRD_LANGUAGE = "en"

DEFAULT_PDF_PATH = RAW_DATA_DIR / "SRD_CC_v5.2.1.pdf"
DEFAULT_EXTRACTED_PAGES_PATH = EXTRACTED_DATA_DIR / "srd-5.2.1-pages.jsonl"
DEFAULT_CHUNKS_PATH = CHUNKS_DATA_DIR / "srd-5.2.1-chunks.jsonl"
DEFAULT_CHROMA_PATH = VECTORSTORES_DIR / "chroma"
DEFAULT_CHROMA_COLLECTION = "srd_5_2_1_en"

DEFAULT_EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "Qwen/Qwen3-Embedding-0.6B",
)

DEFAULT_TOP_K = int(os.getenv("TOP_K", "5"))