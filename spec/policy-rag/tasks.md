# Tasks: Policy RAG

| ID | Task | Spec | Tested by |
|---|---|---|---|
| T1 | Load approved policy documents with their metadata; skip superseded versions. | 6.1, 6.2 | AC-11 |
| T2 | Split documents into chunks, each with a chunk_id, evidence_ref and the document's metadata. | 6.2 | AC-08, AC-09 |
| T3 | Generate embeddings for the chunks and store them for search. | 5.1 | – |
| T4 | Retrieve the top_k chunks for a question, filtered by role and effective date. | 5.1, 6.1, 6.3 | AC-10, AC-12, AC-13 |
| T5 | Set the evidence status and abstain when evidence is not sufficient. | 5.3, 6.4 | AC-05, AC-06, AC-07 |
| T6 | Generate an answer with citations and check every citation. | 5.2, 6.5 | AC-01 to AC-04, AC-15 |
| T7 | Add POST /policy/query and POST /policy/answer with validation, errors and logging. | 7, 8, 9 | AC-16, AC-17 |
| T8 | Test retrieval against the agreed question set. | 10 | AC-14 |
