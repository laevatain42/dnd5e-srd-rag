from dnd5e_srd_rag.chat_service import build_source_items


def _record(
    page: int = 132,
    section: str = "Spells",
    subsection: str | None = "Spell Descriptions",
) -> dict:
    return {
        "metadata": {
            "srd_version": "5.2.1",
            "page": page,
            "section": section,
            "subsection": subsection,
        }
    }


def test_build_source_items_returns_structured_sources() -> None:
    assert build_source_items([_record()]) == [
        {
            "label": "SRD v5.2.1, p. 132, Spells, Spell Descriptions",
            "page": 132,
            "section": "Spells",
            "subsection": "Spell Descriptions",
        }
    ]


def test_build_source_items_deduplicates_sources() -> None:
    assert build_source_items([_record(), _record()]) == [
        {
            "label": "SRD v5.2.1, p. 132, Spells, Spell Descriptions",
            "page": 132,
            "section": "Spells",
            "subsection": "Spell Descriptions",
        }
    ]


def test_build_source_items_keeps_distinct_pages() -> None:
    assert build_source_items([_record(page=132), _record(page=133)]) == [
        {
            "label": "SRD v5.2.1, p. 132, Spells, Spell Descriptions",
            "page": 132,
            "section": "Spells",
            "subsection": "Spell Descriptions",
        },
        {
            "label": "SRD v5.2.1, p. 133, Spells, Spell Descriptions",
            "page": 133,
            "section": "Spells",
            "subsection": "Spell Descriptions",
        },
    ]
