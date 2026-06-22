"""
SRD 目录范围，大章节标题。
SRD page-level section map.
"""

from __future__ import annotations

from typing import Any

# 目录范围，大章节标题。
SECTION_MAP: list[dict[str, Any]] = [
    {
        "page_start": 1,
        "page_end": 4,
        "section": "Front Matter",
        "include_in_rag": False,
    },
    {
        "page_start": 5,
        "page_end": 18,
        "section": "Playing the Game",
        "include_in_rag": True,
    },
    {
        "page_start": 19,
        "page_end": 27,
        "section": "Character Creation",
        "include_in_rag": True,
    },
    {
        "page_start": 28,
        "page_end": 82,
        "section": "Classes",
        "include_in_rag": True,
    },
    {
        "page_start": 83,
        "page_end": 86,
        "section": "Character Origins",
        "include_in_rag": True,
    },
    {
        "page_start": 87,
        "page_end": 88,
        "section": "Feats",
        "include_in_rag": True,
    },
    {
        "page_start": 89,
        "page_end": 103,
        "section": "Equipment",
        "include_in_rag": True,
    },
    {
        "page_start": 104,
        "page_end": 175,
        "section": "Spells",
        "include_in_rag": True,
    },
    {
        "page_start": 176,
        "page_end": 191,
        "section": "Rules Glossary",
        "include_in_rag": True,
    },
    {
        "page_start": 192,
        "page_end": 203,
        "section": "Gameplay Toolbox",
        "include_in_rag": True,
    },
    {
        "page_start": 204,
        "page_end": 253,
        "section": "Magic Items",
        "include_in_rag": True,
    },
    {
        "page_start": 254,
        "page_end": 343,
        "section": "Monsters",
        "include_in_rag": True,
    },
    {
        "page_start": 344,
        "page_end": 364,
        "section": "Animals",
        "include_in_rag": True,
    },
]
