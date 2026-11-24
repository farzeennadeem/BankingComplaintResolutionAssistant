# Implementation Plan: Policy RAG

How we will build the service in spec.md.

1. **Load documents** – load the approved policy documents with their metadata and skip superseded versions. (Spec 6.1, 6.2)
2. **Split into chunks** – break each document into small passages, each keeping its document's metadata. (Spec 6.2)
3. **Make chunks searchable** – generate embeddings for each chunk and store them so they can be searched by meaning. (Spec 5.1)
4. **Retrieve** – for a question, find the top_k most relevant chunks the user is allowed to see, and decide whether the evidence is sufficient. (Spec 5.1, 6.3, 6.4)
5. **Answer or abstain** – if evidence is sufficient, generate an answer from the chunks with citations and check the citations; otherwise abstain. (Spec 5.2, 5.3, 6.5)
6. **Expose through the API** – add the two routes from the contract: one returns the evidence, one returns the answer. (Spec 7, 9)
7. **Test** – a test for every acceptance criterion. (Spec 10)
