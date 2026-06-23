import pytest

from dnd5e_srd_rag.sections import annotate_page_record, find_section_for_page


def test_find_section_for_page_returns_subsection() -> None:
    entry = find_section_for_page(37)

    assert entry["section"] == "Classes"
    assert entry["subsection"] == "Cleric"
    assert entry["include_in_rag"] is True


def test_find_section_for_page_excludes_front_matter() -> None:
    entry = find_section_for_page(1)

    assert entry["section"] == "Front Matter"
    assert entry["include_in_rag"] is False


def test_find_section_for_page_rejects_unknown_page() -> None:
    with pytest.raises(ValueError):
        find_section_for_page(999)


def test_annotate_page_record_adds_section_metadata() -> None:
    annotated = annotate_page_record({"page": 31, "text": "Bard text."})

    assert annotated["section"] == "Classes"
    assert annotated["subsection"] == "Bard"
    assert annotated["include_in_rag"] is True
