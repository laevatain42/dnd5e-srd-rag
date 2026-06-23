from dnd5e_srd_rag.retrieval import format_source, preview_text, unique_sources


def test_format_source_with_subsection() -> None:
    source = format_source(
        {
            "srd_version": "5.2.1",
            "page": 37,
            "section": "Classes",
            "subsection": "Cleric",
        }
    )

    assert source == "SRD v5.2.1, p. 37, Classes, Cleric"


def test_preview_text_compacts_whitespace_and_truncates() -> None:
    preview = preview_text("One\n\nTwo   Three", limit=10)

    assert preview == "One Two..."


def test_unique_sources_deduplicates_formatted_sources() -> None:
    records = [
        {
            "metadata": {
                "srd_version": "5.2.1",
                "page": 37,
                "section": "Classes",
                "subsection": "Cleric",
            }
        },
        {
            "metadata": {
                "srd_version": "5.2.1",
                "page": 37,
                "section": "Classes",
                "subsection": "Cleric",
            }
        },
    ]

    assert unique_sources(records) == ["SRD v5.2.1, p. 37, Classes, Cleric"]
