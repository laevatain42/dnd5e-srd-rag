from dnd5e_srd_rag.vector_store import sanitize_metadata


def test_sanitize_metadata_converts_none_to_empty_string() -> None:
    metadata = sanitize_metadata(
        {
            "section": "Classes",
            "subsection": None,
            "page": 37,
        }
    )

    assert metadata == {
        "section": "Classes",
        "subsection": "",
        "page": 37,
    }
