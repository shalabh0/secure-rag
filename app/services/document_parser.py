from io import BytesIO
import pymupdf as fitz

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
MAX_PDF_PAGES = 500



def extract_text(filename: str, content: bytes) -> list[dict]:


    if len(content) > MAX_DOCUMENT_BYTES:
        raise ValueError("The document exceeds the maximum allowed size.")

    name = filename.rsplit("/",1)[-1].rsplit("\\",1)[-1]
    if "." not in name or name.startswith(".") or name.endswith("."):
        raise ValueError("The filename must have a supported extension.")


    extension = filename.rsplit(".",1)[-1].lower()


    if extension == "txt":
        
        try:
            text = content.decode("utf-8-sig").strip()
        
        except UnicodeDecodeError as exc:
            raise ValueError("The TXT document must be UTF-8 encoded.") from exc

        if not text:
            raise ValueError("The document contains no text.")

        return [{
            "page_number": 1,
            "text": text
        }]

    elif extension == "pdf":
        
        if not content:
            raise ValueError("The uploaded document is empty.")
        
        pages = []



        try:
            with fitz.open(
                stream = BytesIO(content),
                filetype = "pdf",
            )as document:


                if document.page_count > MAX_PDF_PAGES:
                  raise ValueError("The PDF exceeds the maximum allowed page count.")

                for page_number,page in enumerate(document, start = 1):
                    text = page.get_text().strip()


                    if text:
                        pages.append(
                            {
                                "page_number": page_number,
                                "text": text,
                            }
                      )
        except fitz.FileDataError as exc:
            raise ValueError(
                "The PDF is invalid or corrupted."
            ) from exc


        if not pages:
            raise ValueError("No extractable text found in the PDF.")
        
        return pages


    raise ValueError("Unsupported document format.")