# RAG Clarification Questions

1. **Which documents are approved?**
   Current versions of KB-nnn and BUL-yyyy-nn documents of type Policy, Playbook, Guide, FAQ, Casebook or Bulletin. (Spec 6.1)

2. **Which metadata is mandatory?**
   All 10 fields on every passage: evidence_ref, source_id, title, document_type, version, effective_date, access_label, chunk_id, text, score. (Spec 6.2)

3. **What forms a valid citation?**
   evidence_ref, source_id, version and quote. It must name a passage retrieved for this question, with the same source_id and version, and the quote must be word for word from that passage. A supported answer has at least 1 citation. (Spec 6.5)

4. **What should happen when evidence is insufficient?**
   Abstain without generating an answer: supported false, citations [], the reason in limitations, evidence_status insufficient_evidence. (Spec 5.3, 6.4)

5. **Which access labels may each role retrieve?**
   Analyst: Internal only. Supervisor: Internal and Restricted. Restricted text is never shown to an Analyst. (Spec 6.3)

6. **How are superseded versions handled?**
   Never returned or cited (for example KB-001-OLD). Only versions in force on the requested date (default today) are used. (Spec 6.1)
