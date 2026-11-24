# Specification: Complaint Policy Knowledge Service (Policy RAG)

## 1. Overview

The Policy Knowledge Service gives complaint staff answers grounded in approved, current policy documents. Every answer shows where it came from (citations). When the approved documents do not support an answer, the service says so instead of guessing.

## 2. Scope and non-goals

### 2.1 In scope (what will be done)
- Search approved, current policy documents for evidence relevant to a question.
- Return ranked evidence passages with their source details.
- Produce a short answer that uses only the retrieved evidence, with citations.
- Abstain when evidence is missing, too weak or conflicting.
- Apply document access rules by role.

### 2.2 Non-goals (what will not be done)
- Legal, regulatory or financial advice.
- Creating or editing policy documents.
- Answering questions from outside the approved documents.
- Making decisions on complaints (refunds, compensation, approvals).

## 3. Actors

| Actor | Description | Access |
|---|---|---|
| Complaint Analyst | Investigates complaints and needs to know which policy applies. | Internal documents only |
| Supervisor | Reviews recommendations and approves sensitive actions. | Internal and Restricted documents |

## 4. Preconditions
- Users are logged in to the system.
- The caller is identified with an actor ID and a role (Analyst or Supervisor).
- The approved policy documents have been loaded, each with the metadata in 6.2.
- Superseded document versions are marked as superseded.

## 5. Flows

### 5.1 Search policy evidence
1. The user submits a question and, optionally, how many results they want (top_k: 1 to 10, default 5) and filters (document type, source ID, effective date).
2. The service finds the passages most relevant to the question, considering only documents the user may see (6.3) and versions in force on the effective date (default today).
3. The service returns the passages ranked by relevance, each with its source details (6.2) and a relevance score between 0 and 1.
4. The service states whether the evidence is sufficient, insufficient or conflicting (6.4).

### 5.2 Get a grounded answer
1. The user submits a question and, optionally, how many passages to use (1 to 10, default 5).
2. The service runs the search in 5.1 for the user's role.
3. If the evidence is not sufficient, the service abstains (5.3) without generating an answer.
4. Otherwise, the service produces an answer that uses only the retrieved passages, with citations (6.5).
5. The service checks every citation (6.5). If any check fails, the answer is withheld (5.3).
6. The service returns the answer, its citations, any limitations, and the evidence status.

### 5.3 Abstain or withhold
The service returns:
- answer: "I cannot answer this from approved, current policy. Please refer it to a Supervisor."
- supported: false
- citations: an empty list
- limitations: at least one plain-language reason (for example "No approved, current policy evidence matched the question.")
- evidence_status: the result of the search

## 6. Rules

### 6.1 Approved sources
- Document types: Policy, Playbook, Guide, FAQ, Casebook, Bulletin.
- Source IDs in the form KB-nnn or BUL-yyyy-nn for Bulletins.
- Only the current version of a document is used. Superseded versions (for example KB-001-OLD) are never returned.
- Only versions in use on the requested date are used.

### 6.2 Required metadata for every passage
| Field | Meaning |
|---|---|
| evidence_ref | source_id + "#" + chunk_id, for example KB-003#c004 |
| source_id | The document, for example KB-003 |
| title | Document title |
| document_type | One of the types in 6.1 |
| version | Document version, for example 2.0 |
| effective_date | Date the version came into force |
| access_label | Internal or Restricted |
| chunk_id | The passage within the document, for example c004 |
| text | The passage text |
| score | Relevance, 0 to 1 |

### 6.3 Access boundaries
- Analysts see Internal documents only.
- Supervisors see Internal and Restricted documents.
- Restricted passages are never returned to, quoted to or cited for an Analyst.
- The service may report how many passages were filtered out (superseded, access denied), but never their text.

### 6.4 Business rules
| ID | Rule |
|---|---|
| BR-RAG-01 | Answers use only retrieved passages from approved, current documents the user may see. |
| BR-RAG-02 | Evidence is **sufficient** when at least one passage scores at or above the relevance threshold and no two current sources disagree. |
| BR-RAG-03 | Evidence is **insufficient** when no passage reaches the threshold. The service abstains (BR-024). |
| BR-RAG-04 | Evidence is **conflicting** when two current sources disagree. The service shows both sources and abstains (BR-026). |
| BR-RAG-05 | When evidence is not sufficient, no answer is generated. |
| BR-RAG-06 | supported is true only when every statement in the answer is backed by a checked citation. |
| BR-RAG-07 | Answers never promise an outcome, refund, compensation or approval. |
| BR-RAG-08 | The service is read-only: it never changes complaint or policy data. |

### 6.5 Citation rules
- A supported answer has at least one citation.
- Each citation contains: evidence_ref, source_id, version and quote.
- Each citation must name a passage retrieved for this question, with the same source_id and version.
- The quote must be an exact, word-for-word extract of that passage's text.
- If any citation fails these checks, the whole answer is withheld (5.3).

## 7. Errors

| Situation | Response |
|---|---|
| Missing or invalid actor headers | 401 UNAUTHENTICATED |
| Role not allowed | 403 FORBIDDEN_ROLE |
| Question shorter than 3 or longer than 500 characters, top_k outside 1 to 10, unknown field | 422 VALIDATION_ERROR |
| Wrong HTTP method | 405 METHOD_NOT_ALLOWED |
| Document store or answer generation unavailable | 503 DEPENDENCY_UNAVAILABLE, retryable true |
| Search takes too long | 504 TIMEOUT |
| Anything unexpected | 500 INTERNAL_ERROR |
| No, weak or conflicting evidence; failed citation check | **Not an error**: 200 with an abstained or withheld answer (5.3) |

All errors use the standard error envelope (code, message, correlation_id, retryable).

## 8. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-RAG-01 | A search returns within 2 seconds and an answer within 5 seconds for 95% of requests. |
| NFR-RAG-02 | Logs contain only IDs, codes and timings: never the question text, passage text or user names. |
| NFR-RAG-03 | The same question, documents and role return the same passages in the same order. |
| NFR-RAG-04 | Every request carries a correlation ID that appears in the response and the logs. |

## 9. API expectations
Defined by contract v2.2.0. Both routes allow Analyst and Supervisor only.

| Route | Purpose | Request | Response |
|---|---|---|---|
| POST /policy/query | Search (5.1) | PolicyQueryRequest: query, top_k, filters | PolicyQueryResponse: query, results (PolicyEvidence), evidence_status, conflicts, filtered_out |
| POST /policy/answer | Grounded answer (5.2) | PolicyAnswerRequest: question, top_k | GroundedAnswer: answer, supported, citations, limitations, evidence_status |

## 10. Acceptance criteria

### Citations
- AC-01: Every answer with supported true has at least 1 citation.
- AC-02: Every citation's evidence_ref matches a passage in the retrieved results, with the same source_id and version.
- AC-03: Every citation's quote appears word for word in that passage's text.
- AC-04: An answer with an invented citation (not in the results) is returned with supported false and citations [].

### Abstention
- AC-05: A question with no relevant evidence (for example "What is our cryptocurrency complaint process?") returns supported false, citations [], evidence_status insufficient_evidence and at least 1 limitation.
- AC-06: When evidence is insufficient, no answer is generated (the answer is the fixed text in 5.3).
- AC-07: When evidence_status is conflicting_evidence, supported is false and the response names both conflicting sources.

### Metadata
- AC-08: Every returned passage includes all 10 fields in 6.2.
- AC-09: Every evidence_ref has the form KB-nnn#cnnn or BUL-yyyy-nn#cnnn.

### Retrieval and access
- AC-10: A search returns at most top_k passages, ordered by score, highest first.
- AC-11: No superseded version (for example KB-001-OLD) is ever returned.
- AC-12: An Analyst never receives a Restricted passage; a Supervisor asking the same question can.
- AC-13: With effective_on set to a date, only versions in force on that date are returned.
- AC-14: For each question in the agreed test set, the expected source appears in the top 5 results.

### Safe behaviour
- AC-15: No answer promises a refund, compensation, approval or outcome.
- AC-16: A question of 2 characters, or 501 characters, returns 422 VALIDATION_ERROR.
- AC-17: When answer generation is unavailable, the response is 503 DEPENDENCY_UNAVAILABLE with retryable true.
