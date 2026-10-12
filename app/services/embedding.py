import math
import ollama

from app.config import settings

client = ollama.Client(host=settings.OLLAMA_HOST)


def embed_text(text: str) -> list[float]:
    """Convert text into an embedding vector using Ollama."""

    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    if not text.strip():
        raise ValueError("Text cannot be empty.")


    response = client.embed(
        model = settings.EMBED_MODEL,
        input = text
    )


    embeddings = response["embeddings"]


    if not embeddings or not embeddings[0]:
        raise RuntimeError("The embedding model returned an empty vector.")


    vector = embeddings[0]

    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in vector
    ):
        raise RuntimeError("The embedding vector contains invalid values.")

    return [float(value) for value in vector]