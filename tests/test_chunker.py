import pytest

from app.services.chunker import chunk_pages


def word_counter(text: str) -> int:
    """Simple test counter; not a production model tokenizer."""
    return len(text.split())


def sample_pages():
    return [{
        "page_number": 1,
        "text": (
            "The maximum temperature is 80 degrees. "
            "If temperature exceeds 80 degrees, the controller "
            "starts the shutdown procedure. "
            "Inspect the cooling system before restarting."
        ),
    }]


def test_short_text_returns_one_chunk():
    chunks = chunk_pages(
        [{"page_number": 1, "text": "Temperature is 80 degrees."}],
        token_counter=word_counter,
        max_tokens=10,
        overlap_tokens=2,
    )

    assert len(chunks) == 1
    assert chunks[0]["text"] == "Temperature is 80 degrees."


def test_long_text_is_split_within_token_budget():
    chunks = chunk_pages(
        sample_pages(),
        token_counter=word_counter,
        max_tokens=12,
        overlap_tokens=3,
    )

    assert len(chunks) > 1
    assert all(
        word_counter(chunk["text"]) <= 12
        for chunk in chunks
    )


def test_chunk_indexes_are_sequential():
    chunks = chunk_pages(
        sample_pages(),
        token_counter=word_counter,
        max_tokens=12,
        overlap_tokens=3,
    )

    assert [chunk["chunk_index"] for chunk in chunks] == list(
        range(len(chunks))
    )


def test_page_metadata_is_preserved():
    chunks = chunk_pages(
        sample_pages(),
        token_counter=word_counter,
        max_tokens=12,
        overlap_tokens=3,
    )

    assert all(chunk["page_start"] == 1 for chunk in chunks)
    assert all(chunk["page_end"] == 1 for chunk in chunks)


def test_overlap_repeats_boundary_context():
    chunks = chunk_pages(
        sample_pages(),
        token_counter=word_counter,
        max_tokens=12,
        overlap_tokens=3,
    )

    assert len(chunks) > 1

    previous_words = chunks[0]["text"].split()
    next_words = chunks[1]["text"].split()

    assert any(
        previous_words[-size:] == next_words[:size]
        for size in range(
            1,
            min(3, len(previous_words), len(next_words)) + 1,
        )
    )


def test_empty_pages_return_no_chunks():
    assert chunk_pages(
        [],
        token_counter=word_counter,
    ) == []


def test_whitespace_only_page_is_skipped():
    chunks = chunk_pages(
        [{"page_number": 1, "text": "   \n  "}],
        token_counter=word_counter,
    )

    assert chunks == []


@pytest.mark.parametrize("max_tokens", [0, -1])
def test_invalid_max_tokens_are_rejected(max_tokens):
    with pytest.raises(ValueError, match="max_tokens"):
        chunk_pages(
            sample_pages(),
            token_counter=word_counter,
            max_tokens=max_tokens,
        )


@pytest.mark.parametrize("overlap_tokens", [-1, 12])
def test_invalid_overlap_is_rejected(overlap_tokens):
    with pytest.raises(ValueError, match="overlap_tokens"):
        chunk_pages(
            sample_pages(),
            token_counter=word_counter,
            max_tokens=12,
            overlap_tokens=overlap_tokens,
        )


def test_invalid_page_number_is_rejected():
    with pytest.raises(ValueError, match="page_number"):
        chunk_pages(
            [{"page_number": 0, "text": "Some text"}],
            token_counter=word_counter,
        )