
"""
章节标注工具。
Section annotation utilities.
"""

from __future__ import annotations

from typing import Any

from dnd5e_srd_rag.section_map import SECTION_MAP


# 根据页码在 SECTION_MAP 中查找对应的章节
def find_section_for_page(page: int) -> dict[str, Any]:
    for entry in SECTION_MAP:
        if entry["page_start"] <= page <= entry["page_end"]:
            return entry

    raise ValueError(f"No section map entry found for page {page}")


# 给单个 page 补充 和 include_in_rag。
def annotate_page_record(page_record: dict[str, Any]) -> dict[str, Any]:
    """给页面记录添加章节元数据。"""
    page = page_record.get("page")

    if not isinstance(page, int):
        raise ValueError(f"Invalid page value: {page!r}")

    section_entry = find_section_for_page(page)

    return {
        **page_record,
        "section": section_entry["section"],
        "subsection": section_entry.get("subsection"),
        "include_in_rag": section_entry["include_in_rag"],
    }


# 批量标注 page records
def annotate_page_records(
    page_records: list[dict[str, Any]] | Any,
):
    for page_record in page_records:
        yield annotate_page_record(page_record)