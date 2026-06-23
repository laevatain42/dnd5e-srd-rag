from dnd5e_srd_rag.ollama_answer import build_context, build_messages


def _record() -> dict:
    return {
        "chunk_id": "srd-5.2.1-en-p132-spells-spell-descriptions-001",
        "text": "Fire Bolt makes a ranged spell attack and deals 1d10 Fire damage.",
        "metadata": {
            "srd_version": "5.2.1",
            "page": 132,
            "section": "Spells",
            "subsection": "Spell Descriptions",
        },
        "distance": 0.12,
    }


def test_build_context_includes_source_and_text() -> None:
    context = build_context([_record()])

    assert "[1] Source: SRD v5.2.1, p. 132, Spells, Spell Descriptions" in context
    assert "Fire Bolt makes a ranged spell attack" in context


def test_build_messages_instructs_model_to_use_context_only() -> None:
    messages = build_messages("What does Fire Bolt do?", [_record()])

    assert [message["role"] for message in messages] == ["system", "user"]
    assert "Answer only from the provided SRD context" in messages[0]["content"]
    assert "What does Fire Bolt do?" in messages[1]["content"]
    assert "SRD context:" in messages[1]["content"]
