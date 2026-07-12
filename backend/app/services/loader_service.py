from pathlib import Path

import yaml
from pypdf import PdfReader


def parse_markdown(path: Path) -> tuple[str, dict]:
    text = path.read_text(encoding="utf-8")

    metadata = {
        "document_uid": path.stem,
        "title": path.stem,
        "source_type": "unknown",
        "language": "unknown",
        "truth_level": "unknown",
        "file_path": str(path),
    }

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            yaml_block = parts[1]
            body = parts[2].strip()
            loaded = yaml.safe_load(yaml_block) or {}
            metadata.update(loaded)
            metadata["file_path"] = str(path)
            return body, metadata

    return text, metadata


def parse_pdf(path: Path) -> list[tuple[str, dict]]:
    reader = PdfReader(str(path))
    documents = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        metadata = {
            "document_uid": f"{path.stem}-page-{page_index}",
            "title": path.stem,
            "source_type": "secondary_pdf",
            "language": "french",
            "truth_level": "secondary_translation",
            "file_path": str(path),
            "notes": f"Page {page_index}",
        }

        documents.append((text, metadata))

    return documents


def load_corpus(data_dir: str) -> list[tuple[str, dict]]:
    root = Path(data_dir).resolve()
    loaded_documents = []

    for path in root.rglob("*"):
        if path.suffix.lower() == ".md":
            loaded_documents.append(parse_markdown(path))

        elif path.suffix.lower() == ".pdf":
            loaded_documents.extend(parse_pdf(path))

    return loaded_documents