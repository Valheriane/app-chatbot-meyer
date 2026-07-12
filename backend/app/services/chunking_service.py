import re


def split_by_numbered_sections(text: str) -> list[tuple[str | None, str]]:
    """
    Découpe prioritaire sur les sections du type [1], [2], [14] Wrath Cut...
    Si le texte n'a pas ce format, on retourne le texte complet.
    """
    pattern = r"(?=\n?\[\d+\])"
    parts = re.split(pattern, text)

    sections = []
    for part in parts:
        clean = part.strip()
        if not clean:
            continue

        first_line = clean.splitlines()[0][:200]
        sections.append((first_line, clean))

    if not sections:
        return [(None, text)]

    return sections


def split_large_text(text: str, max_chars: int = 1800, overlap: int = 250) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += max_chars - overlap

    return chunks


def chunk_document(text: str) -> list[dict]:
    final_chunks = []
    sections = split_by_numbered_sections(text)

    chunk_index = 0

    for section_title, section_text in sections:
        parts = split_large_text(section_text)

        for part in parts:
            final_chunks.append(
                {
                    "chunk_index": chunk_index,
                    "section_title": section_title,
                    "content": part,
                }
            )
            chunk_index += 1

    return final_chunks