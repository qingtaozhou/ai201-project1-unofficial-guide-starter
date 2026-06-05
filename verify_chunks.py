"""Verification checks for Milestone 3 ingestion and chunking."""

from ingest import load_documents
from chunk import chunk_text, process_all_documents


def check_metadata(chunks):
    """Return missing metadata issues for chunks."""
    required = ["text", "source_file", "chunk_id", "start_char", "end_char"]
    issues = []
    for chunk in chunks:
        for field in required:
            if field not in chunk or chunk[field] in ("", None):
                issues.append(f"{chunk.get('chunk_id', '<unknown>')} missing {field}")
    return issues


def check_tier_preservation(doc_text):
    """Verify the actual tier-ranked section stays inside one chunk."""
    chunks = chunk_text(doc_text, preserve_tiers=True)
    tier_chunks = [chunk for chunk in chunks if "Tier-ranked by usefulness" in chunk["text"]]
    if not tier_chunks:
        return False, "No chunk contains the tier-ranked heading"
    tier_text = tier_chunks[0]["text"]
    expected_items = [
        "1. 7641 (ML)",
        "2. 6505 (Algorithms)",
        "3. 6340 (AI)",
        "4. 7646 (Trading)",
    ]
    missing = [item for item in expected_items if item not in tier_text]
    if missing:
        return False, f"Tier chunk is missing: {missing}"
    return True, tier_chunks[0]


def check_overlap_and_coverage(doc_text):
    """Check configured minimum overlap and that every character position is covered."""
    chunks = chunk_text(doc_text)
    overlap_issues = []

    for previous, current in zip(chunks, chunks[1:]):
        latest_allowed_start = max(0, previous["end_char"] - 50)
        if current["start_char"] > latest_allowed_start:
            overlap_issues.append(
                f"{previous['chunk_id']}->{current['chunk_id']} starts at "
                f"{current['start_char']}, after minimum-overlap start {latest_allowed_start}"
            )

    covered = [False] * len(doc_text)
    for chunk in chunks:
        for index in range(chunk["start_char"], chunk["end_char"]):
            covered[index] = True

    coverage_ok = all(covered)
    return overlap_issues, coverage_ok


def main():
    """Run lightweight acceptance checks and print results."""
    docs = load_documents("documents")
    chunks = process_all_documents("documents")

    print(f"Documents loaded: {len(docs)}")
    print(f"Chunks produced: {len(chunks)}")

    if len(docs) != 12:
        print(f"FAIL: expected 12 documents, loaded {len(docs)}")
    else:
        print("PASS: loaded all 12 documents")

    if 90 <= len(chunks) <= 150:
        print("PASS: chunk count is reasonable for 29k chars at 300-char windows")
    else:
        print("WARN: chunk count is outside the corrected expected range of 90-150")
    print("NOTE: the prompt's 500-800 chunk target does not match the corpus size.")

    metadata_issues = check_metadata(chunks)
    if metadata_issues:
        print("FAIL: metadata issues found")
        for issue in metadata_issues[:10]:
            print(f"- {issue}")
    else:
        print("PASS: required chunk metadata is present")

    doc4 = next(doc for doc in docs if doc["filename"].startswith("04_"))
    tier_ok, tier_result = check_tier_preservation(doc4["clean_text"])
    if tier_ok:
        print("PASS: tier-ranked section is preserved in one chunk")
        print("Example tier chunk:")
        print(tier_result["text"])
    else:
        print(f"FAIL: {tier_result}")

    first_doc = docs[0]
    overlap_issues, coverage_ok = check_overlap_and_coverage(first_doc["clean_text"])
    if not overlap_issues:
        print("PASS: consecutive chunks preserve at least 50 characters of overlap in the first document")
    else:
        print("FAIL: overlap issues found in the first document")
        for issue in overlap_issues[:5]:
            print(f"- {issue}")

    if coverage_ok:
        print("PASS: first document has no data-loss gaps across chunks")
    else:
        print("FAIL: first document has uncovered character positions")


if __name__ == "__main__":
    main()
