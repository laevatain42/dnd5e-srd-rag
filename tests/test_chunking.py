from dnd5e_srd_rag.chunking import build_chunk_id, slugify, split_text


def test_slugify_normalizes_text() -> None:
    assert slugify("Playing the Game") == "playing-the-game"
    assert slugify("Magic Items A-Z") == "magic-items-a-z"
    assert slugify(None) == "unknown"


def test_split_text_respects_max_length() -> None:
    text = "First sentence. Second sentence. Third sentence."

    chunks = split_text(text, chunk_size=30, chunk_overlap=10)

    assert chunks
    assert all(len(chunk) <= 30 for chunk in chunks)


def test_build_chunk_id_includes_section_and_subsection() -> None:
    chunk_id = build_chunk_id(
        page=37,
        section="Classes",
        subsection="Cleric",
        index=1,
    )

    assert chunk_id == "srd-5.2.1-en-p37-classes-cleric-001"
