
import pytest

from app.services import embedding


def test_embed_text_returns_vector(monkeypatch):
    def fake_embed(*, model, input):
        assert model == embedding.settings.EMBED_MODEL
        assert input == "Reset the account password."
        return {"embeddings": [[0.1, -0.2, 0.3]]}

    monkeypatch.setattr(embedding.client, "embed", fake_embed)

    result = embedding.embed_text("Reset the account password.")

    assert result == [0.1, -0.2, 0.3]
    assert all(isinstance(value, float) for value in result)


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_embed_text_rejects_empty_input(text):
    with pytest.raises(ValueError, match="cannot be empty"):
        embedding.embed_text(text)


@pytest.mark.parametrize("text", [None, 123, b"some text"])
def test_embed_text_rejects_non_string_input(text):
    with pytest.raises(TypeError, match="must be a string"):
        embedding.embed_text(text)


def test_embed_text_rejects_empty_vector(monkeypatch):
    monkeypatch.setattr(
        embedding.client,
        "embed",
        lambda **kwargs: {"embeddings": [[]]},
    )

    with pytest.raises(RuntimeError, match="empty vector"):
        embedding.embed_text("Some text")


def test_embed_text_rejects_non_finite_values(monkeypatch):
    monkeypatch.setattr(
        embedding.client,
        "embed",
        lambda **kwargs: {"embeddings": [[0.1, float("nan")]]},
    )

    with pytest.raises(RuntimeError, match="invalid values"):
        embedding.embed_text("Some text")
