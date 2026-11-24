# Vector Index Strategy

## Vector Index
Purpose: Semantic similarity search. The question is converted to a vector and compared with chunk embeddings to find the most similar chunks.
Indexed fields:
- text (embedding)

## Text Index
Purpose: Keyword search for exact terms (e.g. "escalation", "CAD 10,000", "BR-024").
Indexed fields:
- title
- section
- text

## Metadata Index
Purpose: Filtering and compliance. Filters are applied before ranking, so excluded chunks are never returned.
Indexed fields:
- source_id
- version
- effective_date
- access_label
- document_type
- status

## Filters required by the spec

| Filter | Field | Rule | Spec |
|---|---|---|---|
| Access | access_label | Set from the caller's role (see Access filtering in the metadata model). Always applied. | 6.3 |
| Approved only | status | Only Approved. Always applied. | 6.1 |
| Effective version | effective_date | Only versions in force on the requested date (default today). Always applied. | 6.1 |
| Document type | document_type | Optional, chosen by the caller. | 5.1 |
| Source | source_id | Optional, chosen by the caller. | 5.1 |

Search combines vector and text results into one ranked list (score 0 to 1) and returns the top_k chunks.

## Keeping the index up to date
Each document's `checksum` is compared with the stored value whenever documents are loaded:
- **Unchanged** (checksum matches): skip it. No new chunks or embeddings, which saves time and cost.
- **Changed** (checksum differs): delete its old chunks, re-chunk, re-embed and update all three indexes.
- **Duplicate** (two documents with the same checksum): store and embed only one copy, so repeated text does not appear twice in results.

Each chunk stores its document's `checksum`, so a retrieved chunk can be checked against the current version of its source and is never left over from an older one.

## Citation requirements
Every returned chunk includes `title`, `version`, `section` and `evidence_ref` so it can be cited (see Citation mapping in document_metadata_model.md).