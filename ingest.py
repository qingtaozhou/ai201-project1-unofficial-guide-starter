"""Document ingestion utilities for the Unofficial Guide project."""

from pathlib import Path
import json
import re
import html


COURSE_CODE_RE = re.compile(r"\b(?:CS|MGT)\s*-?\s*\d{4}\b", re.IGNORECASE)
PROFESSOR_RE = re.compile(r"\b(?:Professor|Prof\.?)\s*:\s*([A-Z][A-Za-z'\-]+)")
SOURCE_RE = re.compile(r"^Source:\s*(.+)$", re.MULTILINE)
DATE_RE = re.compile(r"^(?:Date Retrieved|Date|Posted):\s*(.+)$", re.MULTILINE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
BOILERPLATE_LINE_RE = re.compile(
    r"^\s*(?:read more|share|comment|comments|cookie|privacy|subscribe|sign in|"
    r"login|advertisement|navigation|footer)\b",
    re.IGNORECASE,
)


def clean_text(text):
    """Normalize document text without removing meaningful line structure."""
    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = HTML_TAG_RE.sub(" ", text)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip() and not BOILERPLATE_LINE_RE.search(line)
    ]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_metadata(text, filename):
    """Extract lightweight metadata used later for retrieval citations."""
    course_codes = sorted({match.group(0).replace(" ", "").upper() for match in COURSE_CODE_RE.finditer(text)})
    professor_match = PROFESSOR_RE.search(text)
    source_match = SOURCE_RE.search(text)
    date_match = DATE_RE.search(text)

    professor = professor_match.group(1) if professor_match else None
    if professor is None and "ratemyprofs" in filename.lower():
        stem_parts = Path(filename).stem.split("_")
        candidate = stem_parts[-1] if stem_parts else ""
        if candidate and candidate[:1].isupper() and not candidate.upper().startswith("CS"):
            professor = candidate

    return {
        "course_codes": course_codes,
        "professor": professor,
        "source": source_match.group(1).strip() if source_match else None,
        "date": date_match.group(1).strip() if date_match else None,
    }


def load_documents(docs_dir="documents"):
    """Load non-empty .txt documents from docs_dir.

    Returns a list of dictionaries containing filename, filepath, raw text,
    cleaned text, and extracted source metadata. Files that cannot be read are
    skipped with a warning printed to stdout.
    """
    docs_path = Path(docs_dir)
    documents = []

    for path in sorted(docs_path.glob("*.txt")):
        try:
            raw_text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Warning: could not read {path}: {exc}")
            continue

        cleaned_text = clean_text(raw_text)
        if not cleaned_text:
            continue

        documents.append(
            {
                "filename": path.name,
                "filepath": str(path),
                "raw_text": raw_text,
                "clean_text": cleaned_text,
                "metadata": extract_metadata(cleaned_text, path.name),
            }
        )

    return documents


def save_raw_documents(documents, output_path="raw_documents.jsonl"):
    """Save raw source text as JSON Lines before cleaning transformations."""
    output = Path(output_path)
    with output.open("w", encoding="utf-8") as handle:
        for document in documents:
            record = {
                "filename": document["filename"],
                "filepath": document["filepath"],
                "raw_text": document["raw_text"],
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


# Main entry point for the ingestion script
if __name__ == "__main__":
    # Load all documents from the documents directory
    loaded = load_documents()
    # Save raw documents to JSONL format
    save_raw_documents(loaded)
    # Print summary statistics
    print(f"Loaded {len(loaded)} documents")
    print("Saved raw text to raw_documents.jsonl")
    # Print details for each loaded document
    for doc in loaded:
        meta = doc["metadata"]
        print(
            f"- {doc['filename']}: {len(doc['clean_text'])} chars, "
            f"courses={meta['course_codes']}, professor={meta['professor']}"
        )
