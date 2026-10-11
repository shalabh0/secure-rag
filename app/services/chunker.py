import re
from collections.abc import Callable

SEPARATORS = (
    
    r"\n\s*\n",          # Paragraph boundary
    r"\n",               # Line boundary
    r"(?<=[.!?])\s+",    # Sentence boundary
    r"\s+",              # Word boundary
)

def _count_tokens(text: str, token_counter: Callable[[str], int]) -> int:
    """Count tokens using the counter supplied by the caller."""
    count = token_counter(text)

    if not isinstance(count, int) or isinstance(count, bool) or count < 0:

        raise ValueError("Token counter must return a non-negative integer.")

    return count

def _split_preserving(text: str, separator: str) -> list[str]:
    """Split at a boundary while retaining the separator in the text."""
    parts = re.split(f"({separator})",text) 
    units = []


    for index in range(0, len(parts), 2):
        unit = parts[index]


        if index + 1 < len(parts):
            unit += parts[index+1]

        if unit.strip():
            units.append(unit)
    
    return units


def _recursive_split(
 text: str,
 max_tokens: int,
 token_counter: Callable[[str],int],
 separator_index: int = 0,
 ) -> list[str]:
 """Split oversized text using progressively smaller boundaries."""

 if _count_tokens(text,token_counter) <= max_tokens:
    return [text]

 for index in range(separator_index,len(SEPARATORS)):
    units = _split_preserving(text,SEPARATORS[index])


    if len(units) > 1:
        result = []

        for unit in units:
            result.extend(
                _recursive_split(
                    unit,
                    max_tokens,
                    token_counter,
                    index + 1,
                )
            )

        return result

 raise ValueError(
        "Text cannot be split within the configured token limit."
    )


def _select_overlap(
    units: list[str],
    next_unit: str,
    overlap_tokens: int,
    max_tokens: int,
    token_counter: Callable[[str], int],
) -> list[str]:
    """Select trailing text for overlap within both token budgets."""
    previous_text = "".join(units)

    # Keep whitespace after each word so adjoining text remains separated.
    words = re.findall(r"\S+\s*", previous_text)
    selected = ""

    for word in reversed(words):
        candidate = word + selected

        if _count_tokens(candidate, token_counter) > overlap_tokens:
            break

        if _count_tokens(
            candidate + next_unit, token_counter
        ) > max_tokens:
            break

        selected = candidate

    return [selected] if selected.strip() else []


def chunk_pages(
    pages : list[dict],
    *,
    token_counter: Callable[[str], int],
    max_tokens: int = 400,
    overlap_tokens: int = 50
) -> list[dict]:

    """Create token-bounded, page-aware chunks from parser output."""
    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than zero.")  

    if overlap_tokens < 0 or overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be non-negative and less than max_tokens.")

    chunks = []


    for page in pages:
        page_number = page.get("page_number")
        text = page.get("text")


        if(
            not isinstance(page_number, int)
            or isinstance(page_number, bool)
            or page_number < 1
        ):
             raise ValueError("Each page needs a positive page_number.")
        
        if not isinstance(text, str):
            raise ValueError("Each page needs text as a string.")


        if not text.strip():
            continue

        units = _recursive_split(
            text.strip(),
            max_tokens,
            token_counter
        )


        current_units = []


        for unit in units:
            candidate = "".join(current_units) + unit

            if _count_tokens(candidate, token_counter) <= max_tokens:
                current_units.append(unit)
                continue

            if not current_units:
                raise ValueError(
                    "A text unit exceeds the configured token limit."
                )

            chunks.append({
                "chunk_index": len(chunks),
                "text": "".join(current_units).strip(),
                "page_start": page_number,
                "page_end": page_number,
            })

            current_units = _select_overlap(
                current_units,
                unit,
                overlap_tokens,
                max_tokens,
                token_counter,
            )
            current_units.append(unit)

        if current_units:
            chunks.append({
                "chunk_index": len(chunks),
                "text": "".join(current_units).strip(),
                "page_start": page_number,
                "page_end": page_number,
            })

    return chunks