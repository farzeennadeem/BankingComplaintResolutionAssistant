"""4.2.2
Input:  data/processed/documents.jsonl (from 4.2.1)
Output: data/processed/chunks_baseline.jsonl
"""

import json
from pathlib import Path

DOCUMENTS_PATH = Path("data/processed/documents.jsonl")
BASELINE_PATH = Path("data/processed/chunks_baseline.jsonl")
SELECTED_PATH = Path("data/processed/chunks_selected.jsonl") #step2

CHUNK_SIZE = 500    # characters per chunk
OVERLAP = 50

MAX_SIZE = 1000 #step2
# Paragraphs starting with these are exceptions/conditions and stay with the paragraph before
EXCEPTION_STARTS = ("Exception", "Except", "Unless", "However", "If")


# Document fields copied onto every chunk
METADATA_FIELDS = ["source_id", "title", "document_type", "version",
                   "effective_date", "access_label", "checksum"]

def load_documents(path=DOCUMENTS_PATH):
    """Read documents.jsonl (one document record per line). Never re-reads the raw .docx files."""
    documents = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                documents.append(json.loads(line))
    return documents

def write_jsonl(chunks, path):
    """Write one chunk per line"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

def make_chunk(document, number, section, text):
    """Build one chunk: the document's metadata plus the chunk fields."""
    chunk_id = f"c{number:03d}"
    chunk = {field: document[field] for field in METADATA_FIELDS}
    chunk.update({
        "chunk_id": chunk_id,
        "evidence_ref": f"{document['source_id']}#{chunk_id}",   # e.g. KB-001#c004
        "section": section,
        "sequence": number,
        "text": text,
    })
    return chunk

# STEP 1

def fixed_chunk(document, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Cut a document into chunk_size-character pieces, overlapping by overlap characters"""
    # Join all sections into one string, remembering where each section starts
    full_text = ""
    section_starts = []                      # e.g. [(0, "Document Information"), (612, "1. Purpose"), ...]
    for section in document["pre_chunks"]:
        if full_text:
            full_text += " "
        section_starts.append((len(full_text), section["section"]))
        full_text += section["text"]

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(full_text), step):
        text = full_text[start:start + chunk_size].strip()

        # Label the chunk with the section it starts in
        section = section_starts[0][1]
        for section_start, section_name in section_starts:
            if section_start <= start:
                section = section_name
            else:
                break

        if text:
            chunks.append(make_chunk(document, len(chunks) + 1, section, text))

        if start + chunk_size >= len(full_text):   # reached the end: stop
            break

    return chunks

# Step 2
def is_exception(paragraph):
    """True if the paragraph is an exception/condition to the one before it."""
    return paragraph.lstrip("•- ").startswith(EXCEPTION_STARTS)


def structure_aware_chunk(document, max_size=MAX_SIZE):
    """One chunk per section; long sections split only between paragraphs,
    never just before an exception. Each chunk starts with its heading."""
    chunks = []

    for section in document["pre_chunks"]:
        heading = section["section"]
        paragraphs = section["text"].split("\n")
        current = []

        for paragraph in paragraphs:
            size_if_added = len("\n".join([heading] + current + [paragraph]))

            if current and size_if_added > max_size and not is_exception(paragraph):
                # Too big and safe to split: save this chunk, start a new one
                text = "\n".join([heading] + current)
                chunks.append(make_chunk(document, len(chunks) + 1, heading, text))
                current = [paragraph]
            else:
                current.append(paragraph)

        if current:
            text = "\n".join([heading] + current)
            chunks.append(make_chunk(document, len(chunks) + 1, heading, text))

    return chunks

def chunk_all(documents, strategy):
    """Run one strategy over every document."""
    all_chunks = []
    for document in documents:
        all_chunks.extend(strategy(document))
    return all_chunks


if __name__ == "__main__":
    documents = load_documents()

    baseline = chunk_all(documents, fixed_chunk)
    write_jsonl(baseline, BASELINE_PATH)
    print(f"Baseline: {len(baseline)} chunks from {len(documents)} documents "
          f"({CHUNK_SIZE} characters, {OVERLAP} overlap) -> {BASELINE_PATH}")

    structured = chunk_all(documents, structure_aware_chunk)
    write_jsonl(structured, SELECTED_PATH)
    print(f"Structure-aware: {len(structured)} chunks (max {MAX_SIZE} characters, "
          f"split only between paragraphs) -> {SELECTED_PATH}")