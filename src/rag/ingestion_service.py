"""Policy document ingestion (4.2.1)."""
import csv
from collections import Counter
from pathlib import Path

import re
from zipfile import BadZipFile

import hashlib                 # creates the SHA-256 checksum
from datetime import date, datetime, timezone

import argparse
import json
import sys

from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from docx.text.paragraph import Paragraph

MANIFEST_PATH = Path("05_Manifests_and_Guides") / "knowledge_base_manifest.csv" #relative to src folder
REQUIRED_COLUMNS = ["source_id", "title", "document_type", "version",
                    "effective_date", "access_label", "status", "relative_path"]
ALLOWED_EXTENSIONS = {".docx"}
SKIP_FOLDERS = {"05_Manifests_and_Guides", "Test_Data"}   # not knowledge-base content
HEADING_LEVELS = {"Heading 1": 1, "Heading 2": 2} #title and subheadings

# Allowed values from the metadata model's validation rules (document_metadata_model.md)
SOURCE_ID_PATTERN = r"^(KB-\d{3}|BUL-\d{4}-\d{2}|KB-\d{3}-OLD)$"   # KB-001, BUL-2026-01, KB-001-OLD
VERSION_PATTERN = r"^\d+\.\d$"                                    # 1.0, 2.1
DOCUMENT_TYPES = {"Policy", "Playbook", "Guide", "FAQ", "Casebook", "Bulletin"}
ACCESS_LABELS = {"Internal", "Restricted"}
STATUSES = {"Approved", "Superseded"}

DEFAULT_SOURCE_ROOT = "data/raw"
DEFAULT_OUTPUT_DIR = "data/processed"
DOCUMENTS_FILE = "documents.jsonl"
RUN_LOG_FILE = "ingestion_run_log.json"

class IngestionService:
    def __init__(self, source_root):
        self.source_root = Path(source_root)
        self.accepted = []
        self.rejected = []
        self.warnings = []
        self.documents = []
        self.records = []    # Step 3 output: metadata-enriched document records

    def _reject(self, item, reason):
        self.rejected.append({"item": item, "reason": reason})

    def _load_manifest(self):
        path = self.source_root / MANIFEST_PATH
        if not path.is_file():
            raise IngestionError(f"Manifest not found: {path}")
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)         #reads each row as a dict, with keys from the header row
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise IngestionError(f"Manifest is missing required columns: {', '.join(missing)}")
            
            #return every row and strip spaces from every value so ' KB-001 ' and 'KB-001' match
            return [{k: (v or "").strip() for k, v in row.items()} for row in reader]

#STEP 1:
    def validate_sources(self):
        rows = self._load_manifest()

        # count how many times each source_id appears to spot duplicates
        id_counts = Counter(row["source_id"] for row in rows)

        # remember every file path the manifest mentions
        listed_paths = set()

        for row in rows:
            source_id = row["source_id"] or "(no source_id)"    # use the source_id as a label
            rel_path = row["relative_path"].replace("\\", "/")  # use / even if written with \
            if rel_path:
                listed_paths.add(rel_path)
            
            missing = [c for c in REQUIRED_COLUMNS if not row[c]] # Every required field must be filled in
            if missing:
                self._reject(source_id, f"Manifest row is missing: {', '.join(missing)}")
                continue

            if id_counts[row["source_id"]] > 1: #id dupe check
                self._reject(source_id, f"Duplicate source_id {source_id} appears "
                                        f"{id_counts[row['source_id']]} times in the manifest")
                continue

            file_path = self.source_root / rel_path
            # docx check
            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                self._reject(source_id, f"{rel_path} is not a .docx file")
                continue

            # file exist check
            if not file_path.is_file():
                self._reject(source_id, f"{rel_path} is listed in the manifest but missing from {self.source_root}")
                continue

            # keep the manifest details plus where the file is when all passed, for step 2
            self.accepted.append({**row, "file_path": file_path})


        # catches the unlisted files
        for path in sorted(self.source_root.rglob("*")):  # every file in every subfolder
            rel = path.relative_to(self.source_root)      # e.g. 01_.../KB-001_....docx

            if (path.is_file()
                    and not path.name.startswith(".")        # ignore hidden files like .DS_Store
                    and rel.parts[0] not in SKIP_FOLDERS     # ignore the manifest and test folders
                    and rel.as_posix() not in listed_paths): # not in the manifest = not approved
                self._reject(rel.as_posix(), "File is not listed in the manifest")

        return self.accepted

    
    #STEP 2: open every accepted file and turn it into sections
    def _read_blocks(self, file_path):
        """Open a Word file and return its content from top to bottom. The style tells us later whether a line is a heading or normal text.
        """
        doc = Document(file_path)
        blocks = []

        for block in doc.iter_inner_content():
            if isinstance(block, Paragraph):
                blocks.append((block.style.name, block.text))
            else:
                for row in block.rows:          # if table
                    row_text = " | ".join(cell.text for cell in row.cells)
                    blocks.append(("Table", row_text))
        return blocks

    @staticmethod
    def _normalise(text):
        """Tidy one line of text so the same content always looks the same.
        """
        text = text.replace("\u00a0", " ")
        text = re.sub(r"\s+", " ", text)    
        return text.strip()

    def _extract_sections(self, blocks):
        """Group the document's lines into sections. Every heading starts a new section.
        """
        sections = []
        current = {"section_title": "Document Information", "heading_level": 0, "lines": []}

        for style, raw_text in blocks:
            text = self._normalise(raw_text)

            if text == "" or style == "Title":
                continue

            if style in HEADING_LEVELS:
                sections.append(current)
                current = {"section_title": text,
                           "heading_level": HEADING_LEVELS[style],   # 1 = main heading, 2 = sub-heading
                           "lines": []}
            else:
                # Normal text or a table row: it belongs to the current section
                current["lines"].append(text)

        # The last section
        sections.append(current)

        # Build the final list
        result = []
        for section in sections:
            if section["lines"]:
                result.append({
                    "sequence": len(result) + 1,                # position in the document
                    "section_title": section["section_title"],  # the heading it sits under
                    "heading_level": section["heading_level"],
                    "text": "\n".join(section["lines"]),        # one paragraph/table row per line
                })
        return result

    def extract_documents(self):
        """open every accepted file and turn it into sections.
        """
        readable = []   # accepted files that also pass this step

        for doc in self.accepted:
            try:
                blocks = self._read_blocks(doc["file_path"])
            except (PackageNotFoundError, BadZipFile, KeyError, ValueError) as error:
                self._reject(doc["source_id"],
                             f"{doc['relative_path']} could not be read as a Word document: {error}")
                continue

            # 2. Split it into sections
            sections = self._extract_sections(blocks)

            # 3. reject docs that have no text at all
            if not sections:
                self._reject(doc["source_id"], f"{doc['relative_path']} contains no text")
                continue

            # 4. No headings check, flags that doc is one section only
            if all(s["heading_level"] == 0 for s in sections):
                self.warnings.append({"item": doc["source_id"],
                                      "reason": "No headings found; whole document is one section"})

            # 5. Keep it
            readable.append(doc)
            self.documents.append({
                "source_id": doc["source_id"],
                "relative_path": doc["relative_path"],
                "sections": sections,
            })

        # Only files that passed Steps 1 AND 2 stay accepted
        self.accepted = readable
        return self.documents

    def _sha256(self, file_path):
        """Fingerprint the file; changes if even one byte changes."""
        return "sha256:" + hashlib.sha256(file_path.read_bytes()).hexdigest()

    def _metadata_problems(self, doc):
        """Check a row against the metadata model's validation rules. Empty list = valid."""
        problems = []
        if not re.match(SOURCE_ID_PATTERN, doc["source_id"]):
            problems.append(f"source_id '{doc['source_id']}' is not KB-nnn, BUL-yyyy-nn or KB-nnn-OLD")
        if doc["document_type"] not in DOCUMENT_TYPES:
            problems.append(f"document_type '{doc['document_type']}' is not one of {sorted(DOCUMENT_TYPES)}")
        elif doc["source_id"].startswith("BUL-") and doc["document_type"] != "Bulletin":
            problems.append("BUL- documents must have document_type Bulletin")
        if not re.match(VERSION_PATTERN, doc["version"]):
            problems.append(f"version '{doc['version']}' should look like 1.0")
        try:
            date.fromisoformat(doc["effective_date"])
        except ValueError:
            problems.append(f"effective_date '{doc['effective_date']}' is not a YYYY-MM-DD date")
        if doc["access_label"] not in ACCESS_LABELS:
            problems.append(f"access_label '{doc['access_label']}' must be Internal or Restricted")
        if doc["status"] not in STATUSES:
            problems.append(f"status '{doc['status']}' must be Approved or Superseded")
        elif doc["source_id"].endswith("-OLD") and doc["status"] != "Superseded":
            problems.append("-OLD documents must have status Superseded")
        return problems

    def _version_in_document(self, sections):
        """Return the version the document states in its info table ("Version | 3.0"), or None."""
        first = sections[0]
        if first["section_title"] != "Document Information":
            return None
        match = re.search(r"^Version \| (.+)$", first["text"], re.MULTILINE)
        return match.group(1).strip() if match else None

    def apply_metadata(self):
        """Step 3: build a document record and its pre-chunk records for each accepted document."""
        sections_by_id = {d["source_id"]: d["sections"] for d in self.documents}
        kept = []

        for doc in self.accepted:
            # 1. Validate metadata
            problems = self._metadata_problems(doc)
            if problems:
                self._reject(doc["source_id"], "Invalid metadata: " + "; ".join(problems))
                continue

            # 2. Version evidence: manifest and document must agree
            sections = sections_by_id[doc["source_id"]]
            doc_version = self._version_in_document(sections)
            if doc_version is None:
                self.warnings.append({"item": doc["source_id"],
                                      "reason": "Document does not state its version; using the manifest version"})
            elif doc_version != doc["version"]:
                self._reject(doc["source_id"],
                             f"Manifest says version {doc['version']} but the document says {doc_version}")
                continue

            # 3. Checksum evidence
            checksum = self._sha256(doc["file_path"])

            # 4. Document record
            record = {
                "source_id": doc["source_id"],
                "title": doc["title"],
                "document_type": doc["document_type"],
                "version": doc["version"],
                "effective_date": doc["effective_date"],
                "access_label": doc["access_label"],
                "status": doc["status"],
                "relative_path": doc["relative_path"],
                "checksum": checksum,
            }

            # 5. Pre-chunk records, one per section (Superseded documents are not chunked)
            pre_chunks = []
            if doc["status"] == "Approved":
                for section in sections:
                    pre_chunks.append({
                        "source_id": doc["source_id"],
                        "title": doc["title"],
                        "document_type": doc["document_type"],
                        "version": doc["version"],
                        "effective_date": doc["effective_date"],
                        "access_label": doc["access_label"],
                        "checksum": checksum,
                        "section": section["section_title"],
                        "sequence": section["sequence"],
                        "text": section["text"],
                    })
            record["pre_chunks"] = pre_chunks

            self.records.append(record)
            kept.append(doc)

        self.accepted = kept
        return self.records

    #STEP 4: repeatability and logging
    @staticmethod
    def _now():
        """Current UTC time as text, for the run log."""
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def run(self):
        """Run Steps 1-3 in order. A fatal error is recorded as a failed run, not a crash."""
        started_at = self._now()
        try:
            self.validate_sources()
            self.extract_documents()
            self.apply_metadata()
            status, error = "completed", None
        except IngestionError as problem:
            status, error = "failed", str(problem)
        return self.build_summary(started_at, status, error)

    def build_summary(self, started_at, status, error):
        """Counts, lists and timestamps for the run log."""
        return {
            "status": status,
            "error": error,
            "started_at": started_at,
            "finished_at": self._now(),
            "source_root": str(self.source_root),
            "counts": {
                "accepted": len(self.accepted),
                "rejected": len(self.rejected),
                "warnings": len(self.warnings),
                "pre_chunks": sum(len(record["pre_chunks"]) for record in self.records),
            },
            "accepted": [doc["source_id"] for doc in self.accepted],
            "rejected": self.rejected,
            "warnings": self.warnings,
        }

    def write_outputs(self, summary, output_dir):
        """Write documents.jsonl (only if the run completed) and the run log (always)."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Overwrite, never append, so reruns don't create duplicates.
        # Skipped on a failed run so the last good output isn't wiped
        if summary["status"] == "completed":
            with open(output_dir / DOCUMENTS_FILE, "w", encoding="utf-8") as f:
                for record in self.records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")   # one record per line

        with open(output_dir / RUN_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

def build_argument_parser():
    """Command-line options; both have defaults so the plain command just works."""
    parser = argparse.ArgumentParser(description="Ingest the approved policy documents.")
    parser.add_argument("--source-root", default=DEFAULT_SOURCE_ROOT,
                        help="folder containing the manifest and documents (default: data/raw)")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help="where documents.jsonl and the run log are written (default: data/processed)")
    return parser


def main():
    args = build_argument_parser().parse_args()
    service = IngestionService(args.source_root)
    summary = service.run()
    service.write_outputs(summary, args.output_dir)

    if summary["status"] == "failed":
        print(f"Ingestion FAILED: {summary['error']}")
        print(f"See {Path(args.output_dir) / RUN_LOG_FILE}")
        return 1

    counts = summary["counts"]
    print(f"Ingestion completed: {counts['accepted']} accepted, {counts['rejected']} rejected, "
          f"{counts['warnings']} warnings, {counts['pre_chunks']} pre-chunks")
    for item in summary["rejected"]:
        print(f"  REJECTED {item['item']}: {item['reason']}")
    for item in summary["warnings"]:
        print(f"  WARNING  {item['item']}: {item['reason']}")
    print(f"Wrote {Path(args.output_dir) / DOCUMENTS_FILE} and {Path(args.output_dir) / RUN_LOG_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
