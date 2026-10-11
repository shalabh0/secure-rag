import pymupdf as fitz
import pytest

from app.services.document_parser import extract_text,MAX_DOCUMENT_BYTES,MAX_PDF_PAGES


def create_pdf(text: str | None = None) -> bytes:
    """Create a PDF in memory for testing."""
    document = fitz.open()
    page = document.new_page()

    if text:
        page.insert_text((72, 72), text)

    content = document.tobytes()
    document.close()

    return content


def test_extract_txt():
    result = extract_text("notes.txt", b"Hello Secure RAG")

    assert result == [
        {"page_number": 1, "text": "Hello Secure RAG"}
    ]


def test_extract_txt_with_utf8_bom():
    result = extract_text("notes.txt", b"\xef\xbb\xbfHello")

    assert result[0]["text"] == "Hello"


def test_reject_empty_txt():
    with pytest.raises(ValueError, match="contains no text"):
        extract_text("empty.txt", b"   ")


def test_reject_invalid_utf8():
    with pytest.raises(ValueError, match="UTF-8 encoded"):
        extract_text("invalid.txt", b"\xff\xfe\xfa")


def test_extract_pdf():
    result = extract_text(
        "sample.pdf",
        create_pdf("Secure RAG PDF test"),
    )

    assert result[0]["page_number"] == 1
    assert "Secure RAG PDF test" in result[0]["text"]


def test_reject_text_free_pdf():
    with pytest.raises(ValueError, match="No extractable text"):
        extract_text("blank.pdf", create_pdf())


def test_reject_empty_pdf():
    with pytest.raises(ValueError, match="uploaded document is empty"):
        extract_text("empty.pdf", b"")


def test_reject_malformed_pdf():
    with pytest.raises(ValueError, match="invalid or corrupted"):
        extract_text("broken.pdf", b"This is not a PDF")


def test_reject_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported document format"):
        extract_text("report.docx", b"some content")

def test_reject_oversized_document():
    content = b"a" * (MAX_DOCUMENT_BYTES + 1)

    with pytest.raises(ValueError, match="maximum allowed size"):
        extract_text("large.txt", content)


def test_reject_pdf_exceeding_page_limit():
    document = fitz.open()

    for _ in range(MAX_PDF_PAGES + 1):
        document.new_page()

    content = document.tobytes()
    document.close()

    with pytest.raises(ValueError, match="maximum allowed page count"):
        extract_text("large.pdf", content)


@pytest.mark.parametrize(
    "filename",
    ["report", ".txt", "report."],
)
def test_reject_invalid_filename(filename):
    with pytest.raises(ValueError, match="supported extension"):
        extract_text(filename, b"hello")