from fastapi.testclient import TestClient

from dnd5e_srd_rag import api


client = TestClient(api.app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_answer_and_sources(monkeypatch) -> None:
    def fake_chat_with_srd(
        question: str,
        top_k: int,
        section: str | None,
        model: str,
    ) -> dict:
        assert question == "What does Fire Bolt do?"
        assert top_k == 3
        assert section == "Spells"
        assert model == "llama3.1:8b"

        return {
            "answer": "Fire Bolt makes a ranged spell attack.",
            "sources": [
                {
                    "label": "SRD v5.2.1, p. 132, Spells, Spell Descriptions",
                }
            ],
        }

    monkeypatch.setattr(api, "chat_with_srd", fake_chat_with_srd)

    response = client.post(
        "/api/chat",
        json={
            "question": "What does Fire Bolt do?",
            "top_k": 3,
            "section": "Spells",
            "model": "llama3.1:8b",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Fire Bolt makes a ranged spell attack.",
        "sources": [
            {
                "label": "SRD v5.2.1, p. 132, Spells, Spell Descriptions",
            }
        ],
    }


def test_chat_rejects_empty_question() -> None:
    response = client.post(
        "/api/chat",
        json={
            "question": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422


def test_chat_rejects_too_large_top_k() -> None:
    response = client.post(
        "/api/chat",
        json={
            "question": "What does Fire Bolt do?",
            "top_k": 999,
        },
    )

    assert response.status_code == 422
