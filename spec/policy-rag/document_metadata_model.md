# Metadata Model
## Document fields
- `source_id`: stable identifier for the source document. Format 'KB-nnn' for all files unless they are bulletins which have format 'BUL-YYYY-nn' or superseded with format 'KB-nnn-OLD'
- `title`: title of document
- `document_type`: document classification used by the retrieval filter; use this exact field name in the retrieval contract.
- `category`: subject or business category, distinct from document type. Business means rules that govern how the organisation operates, such as policies, standards, controls and authority. Subject means subject-matter knowledge about a topic or product, which staff use to do the work.
- `version` and `effective_date`: document version and the date it becomes applicable.
- `access_label`: access-control value used by retrieval filtering (Internal or Restricted)
- `status`: whether the document may be used: Approved or Superseded.
- `checksum`: SHA-256 hash of the file's contents, a fingerprint of the document. If even one character changes, the checksum changes, so edits are detected even when the version number was not updated.
## Chunk fields
A chunk is one passage of an approved document. Superseded documents (`KB-nnn-OLD`) are not chunked.
- `chunk_id`: identifies the passage within its document. Format 'c' + 3 digits (e.g. c004), unique within its source_id.
- `evidence_ref`: citable reference, `source_id` + '#' + `chunk_id` (e.g. BUL-2026-01#c001). Unique across all chunks.
- `source_id`: the document the chunk came from. Must match a document record.
- `version`: must equal the document's version.
- `checksum`: must equal the document's checksum, proving which exact file the chunk came from.
- `section`: the heading the text sits under (e.g. '3.4 Escalation'). A chunk never spans two sections.
- `sequence`: position of the chunk in the document, starting at 1, with no gaps or duplicates within a source_id.
- `text`: the passage text. Must not be empty.
- `access_label`, `document_type`, `effective_date`, `title`: copied from the document so chunks can be filtered and cited. Must always equal the document's values; if the document changes, its chunks are rebuilt.
## Validation rules
| Field | Required | Allowed values / format | Consistency rules |
|---|---|---|---|
| `source_id` | Yes | `KB-nnn`, `BUL-YYYY-nn` or `KB-nnn-OLD` (n = digit) | Unique across all documents |
| `title` | Yes | Text, not empty | — |
| `document_type` | Yes | Policy, Playbook, Guide, FAQ, Casebook, Bulletin | `BUL-` documents must be Bulletin |
| `category` | Yes | Business or Subject | — |
| `version` | Yes | Number with one decimal point, e.g. 1.0, 2.1 | Only one Approved version per document |
| `effective_date` | Yes | Date, YYYY-MM-DD | Not empty for Approved documents |
| `access_label` | Yes | Internal or Restricted | — |
| `status` | Yes | Approved or Superseded | `KB-nnn-OLD` documents must be Superseded; only Approved documents are chunked and searched |
| `checksum` | Yes | `sha256:` followed by 64 hex characters | Generated from the file at load time; must match the stored value or the document is re-processed |
## Access filtering
Every search is filtered by the caller's role before results are ranked.

| Role | Allowed access_label values |
|---|---|
| Analyst | Internal |
| Supervisor | Internal, Restricted |

Filter: access_label IN allowed values for the caller's role.

Example: a Restricted document is excluded when an Analyst asks "How are complaint escalations handled?", but returned to a Supervisor asking the same question. Restricted text is never returned, quoted or cited to an Analyst.

## Citation mapping
- Every chunk traces to exactly one document (`source_id`, `version`, `checksum`) and one `section`.
- A citation is created from the chunk alone: `title`, `version`, `section` and `evidence_ref`.
  Example: Operational Bulletin: Approval Threshold Clarification v1.0, section 1 (BUL-2026-01#c001)