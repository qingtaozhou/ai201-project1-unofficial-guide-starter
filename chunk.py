"""Chunking pipeline for the Unofficial Guide project."""

from pathlib import Path
import argparse
import json
import re

from ingest import load_documents


DEFAULT_CHUNK_SIZE = 600
DEFAULT_OVERLAP = 100
TIER_HEADER_RE = re.compile(r"(?im)^(?:\*\*)?\s*(?:Tier\s+\d+|Tier-ranked)[^\n]*")
HEADING_RE = re.compile(r"(?m)^(?:\*\*[^*\n]+:\*\*|#{1,6}\s+.+)$")
NUMBERED_LINE_RE = re.compile(r"(?m)^\s*\d+[\.\)]\s+")
COURSE_CODE_RE = re.compile(r"\b(?:CS|MGT)\s*-?\s*\d{4}\b", re.IGNORECASE)


def _line_end(text, index):
    """Return the index just after the current line."""
    end = text.find("\n", index)
    return len(text) if end == -1 else end + 1


def _line_start(text, index):
    """Return the index at the start of the current line."""
    start = text.rfind("\n", 0, max(0, index))
    return 0 if start == -1 else start + 1


def _protected_ranges(text):
    """Find ranges that should not be split across chunks.

    Tier sections are detected from either explicit headers like "Tier 1:" or
    the actual corpus format, "Tier-ranked by usefulness...". Numbered-list
    blocks are protected because several documents store study steps and
    rankings as lists.
    """
    ranges = []

    headings = list(HEADING_RE.finditer(text))
    for match in TIER_HEADER_RE.finditer(text):
        start = _line_start(text, match.start())
        next_heading = None
        for heading in headings:
            if heading.start() > match.start():
                next_heading = heading.start()
                break
        end = next_heading if next_heading is not None else len(text)
        ranges.append((start, end))

    lines = text.splitlines(keepends=True)
    offset = 0
    list_start = None
    list_end = None
    for line in lines:
        line_start = offset
        line_end = offset + len(line)
        if NUMBERED_LINE_RE.match(line):
            if list_start is None:
                list_start = line_start
            list_end = line_end
        elif list_start is not None and line.strip() == "":
            list_end = line_end
        elif list_start is not None:
            ranges.append((list_start, list_end))
            list_start = None
            list_end = None
        offset = line_end
    if list_start is not None:
        ranges.append((list_start, list_end))

    return _merge_ranges(ranges)


def _merge_ranges(ranges):
    """Merge overlapping protected ranges."""
    if not ranges:
        return []

    ranges = sorted(ranges)
    merged = [ranges[0]]
    for start, end in ranges[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def _extend_past_protected_range(start, proposed_end, protected_ranges):
    """Extend a chunk end if it would split a protected range."""
    end = proposed_end
    changed = True
    while changed:
        changed = False
        for protected_start, protected_end in protected_ranges:
            if start < protected_end and protected_start < end < protected_end:
                end = protected_end
                changed = True
    return end


def _trim_boundary_to_sentence(text, start, end, chunk_size):
    """Prefer ending at a nearby newline or sentence boundary."""
    if end >= len(text):
        return len(text)

    minimum = start + max(120, chunk_size // 2)
    window = text[minimum:end]
    candidates = [
        minimum + match.end()
        for match in re.finditer(r"(?:\n\n|[.!?]\s+|\n)", window)
    ]
    if candidates:
        return candidates[-1]
    return end


def _snap_start_to_readable_boundary(text, target_start, max_extra_overlap=160):
    """Move a chunk start backward to a nearby sentence, line, or word boundary."""
    if target_start <= 0:
        return 0

    search_floor = max(0, target_start - max_extra_overlap)
    window = text[search_floor:target_start]
    sentence_matches = list(re.finditer(r"(?:\n+|[.!?]\s+)", window))
    if sentence_matches:
        return search_floor + sentence_matches[-1].end()

    if text[target_start - 1].isspace():
        return target_start

    for index in range(target_start, search_floor, -1):
        if text[index - 1].isspace():
            return index
    return target_start


def chunk_text(text, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP, preserve_tiers=True):
    """Split text into chunks using the configured size and overlap.

    Chunks normally use a 600-character sliding window with 100 characters of
    overlap. When preserve_tiers is enabled, boundaries are extended so tier
    sections and numbered-list blocks remain intact.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    protected_ranges = _protected_ranges(text) if preserve_tiers else []
    chunks = []
    start = 0

    while start < len(text):
        proposed_end = min(start + chunk_size, len(text))
        end = _extend_past_protected_range(start, proposed_end, protected_ranges)
        if end == proposed_end:
            end = _trim_boundary_to_sentence(text, start, end, chunk_size)
        end = min(max(end, start + 1), len(text))

        chunk_body = text[start:end]
        if chunk_body.strip():
            chunks.append(
                {
                    "text": chunk_body,
                    "chunk_id": len(chunks) + 1,
                    "start_char": start,
                    "end_char": end,
                }
            )

        if end >= len(text):
            break

        next_start = _snap_start_to_readable_boundary(text, max(0, end - overlap))
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks


def _chunk_course_codes(text, document_codes):
    """Return course codes present in a chunk, falling back to document codes."""
    codes = sorted({match.group(0).replace(" ", "").upper() for match in COURSE_CODE_RE.finditer(text)})
    return codes or document_codes


def process_all_documents(docs_dir="documents", chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP):
    """Load all documents, chunk them, and attach document-level metadata."""
    all_chunks = []
    documents = load_documents(docs_dir)

    for document_sequence, document in enumerate(documents, start=1):
        doc_chunks = chunk_text(
            document["clean_text"],
            chunk_size=chunk_size,
            overlap=overlap,
            preserve_tiers=True,
        )
        document_metadata = document["metadata"]

        for chunk_number, chunk in enumerate(doc_chunks, start=1):
            all_chunks.append(
                {
                    "text": chunk["text"],
                    "source_file": document["filename"],
                    "source_path": document["filepath"],
                    "chunk_id": f"{document_sequence:02d}_{chunk_number:03d}",
                    "start_char": chunk["start_char"],
                    "end_char": chunk["end_char"],
                    "document_sequence": document_sequence,
                    "course_codes": _chunk_course_codes(
                        chunk["text"], document_metadata["course_codes"]
                    ),
                    "professor": document_metadata["professor"],
                    "source": document_metadata["source"],
                    "date": document_metadata["date"],
                }
            )

    return all_chunks


def write_chunks(chunks, output_path):
    """Write chunks as pretty JSON for inspection or the next pipeline stage."""
    output = Path(output_path)
    output.write_text(json.dumps(chunks, indent=2), encoding="utf-8")


def main():
    """Run ingestion and chunking from the command line."""
    parser = argparse.ArgumentParser(description="Ingest and chunk source documents.")
    parser.add_argument("--docs-dir", default="documents")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    parser.add_argument("--output", default="chunks.json")
    args = parser.parse_args()

    chunks = process_all_documents(args.docs_dir, args.chunk_size, args.overlap)
    write_chunks(chunks, args.output)

    print(f"Wrote {len(chunks)} chunks to {args.output}")
    by_file = {}
    for chunk in chunks:
        by_file[chunk["source_file"]] = by_file.get(chunk["source_file"], 0) + 1
    for source_file, count in sorted(by_file.items()):
        print(f"- {source_file}: {count} chunks")


if __name__ == "__main__":
    main()
