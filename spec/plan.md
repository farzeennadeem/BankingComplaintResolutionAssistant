# Implementation Plan: Banking Complaint Resolution Assistant

## 0. Artifact flow

Problem statement + objective → specification → technical plan → implementation tasks → code and tests.

## 1. Repository context

- Specification: /spec/spec.md
- Plan: /spec/plan.md
- Tasks: /spec/tasks.md
- API conventions: /docs/api-error-conventions.md
- Complaint tests: /tests/unit/complaints/, /tests/integration/complaints/

## 2. Approved technology stack

| **Area** | **Decision** |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI |
| Validation | Pydantic v2 |
| Persistence | PostgreSQL |
| Front end design | React |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Unit tests | pytest |
| API tests | FastAPI TestClient |
| Formatting | Black |
| Linting | Ruff |
| Type checking | mypy |

## 3. Target structure

```
banking-complaint-resolution/
├── src/
│   ├── core/
│   │   └── clock.py
│   ├── customers/
│   │   ├── models.py
│   │   └── repository.py
│   ├── complaints/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repository.py
│   │   ├── urgency_rules.py
│   │   └── router.py
│   └── main.py
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── SubmitComplaint.jsx
│       │   └── MyComplaints.jsx
│       ├── components/
│       │   ├── ComplaintForm.jsx
│       │   ├── ComplaintList.jsx
│       │   └── StatusBadge.jsx
│       └── api/
│           └── complaintsApi.js
├── tests/
│   ├── unit/
│   │   └── complaints/
│   │       └── test_urgency_rules.py
│   └── integration/
│       └── complaints/
│           └── test_complaints_api.py
├── spec/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── .env.example
└── README.md
```

## 4. Proposed API

POST /api/v1/complaints

### 4.1 Submit a complaint

POST /api/v1/complaints

The customer calls this after logging in. For phone and branch complaints, an advisor calls it on the customer's behalf and also sends customerId.

Request:

- channel: PHONE, BRANCH, WEB, EMAIL or MOBILE_APP
- narrative: what the customer said, stored exactly as given
- transactionId: the transaction the complaint is about (optional)
- amount: the transaction amount (optional)
- indicators: risk indicators the customer or advisor states explicitly, such as account takeover or unauthorised use (optional; allowed values depend on CL-005)

Example:

```
{ "channel": "WEB", "narrative": "I do not recognize a $2,750 online electronics purchase.", "transactionId": "txn-10045", "amount": 2750.00, "indicators": ["UNAUTHORISED_USE_STATED"] }
```

Response (201):

- complaintId: the new complaint's ID
- status: RECEIVED, or NEEDS_INFORMATION if the amount or transaction ID is missing
- reasonCode: COMPLAINT_RECORDED
- message: a short, customer-safe message

Example:

```
{ "complaintId": "CMP-2026-00481", "status": "RECEIVED", "reasonCode": "COMPLAINT_RECORDED", "message": "Your complaint has been recorded." }
```

### 4.2 Look up a customer's complaints

GET /api/v1/customers/{customer_id}/complaints

Returns a list of that customer's complaints. Each has complaintId, channel, receivedAt and status.

### 4.3 Status codes

- 201: complaint recorded
- 200: complaints returned
- 401: user is not logged in
- 403: the user asked for another customer's complaints
- 422: the request is invalid (for example, an unsupported channel or an empty narrative), with reasonCode MISSING_REQUIRED_FIELD for a missing field

## 5. Component responsibilities

| **Component** | **Responsibility** |
|---|---|
| router.py | Bind HTTP input, find the logged-in customer, call the urgency rules and repository, and map results to the API response. |
| schemas.py | Pydantic request/response models and enums (channels, statuses, urgency levels, reason codes). |
| urgency_rules.py | Check for missing information, apply the urgency rules and flag Critical and High complaints for human review. |
| customers/repository.py | Check that the customer is registered. |
| complaints/repository.py | Save complaints and find a customer's complaints. |
| models.py | Database tables for customers, complaints and status history. |
| core/clock.py | Provide the received time so tests can set it. |
| frontend | Customer pages to submit a complaint and view their own complaints. |
| tests | Map test names or metadata to acceptance criteria IDs. |

## 6. Deterministic validation order

- Validate the request: the channel is allowed and the narrative is not empty.
- Find the customer from the login (or the customerId sent by an advisor) and confirm they are registered.
- Save the complaint with the narrative unchanged and the received time.
- Check for missing information (amount, transaction ID). If anything is missing, set the status to NEEDS_INFORMATION and do not guess. The order of this check relative to Critical is not decided until CL-003 is resolved.
- Apply the urgency rules. If more than one fits, use the highest: Critical, then High, then Medium, then Standard.
- Flag Critical and High complaints for human review.
- Store the status, urgency and the rule that set it with the complaint.
- Return complaintId, status, reasonCode and message.

## 7. Technical decisions

- Use Decimal for amounts, not float.
- Get the received time from clock.py; do not call datetime.now() inside the rules.
- Keep business rules outside the FastAPI router.
- Keep database access inside repository classes.
- Use string-backed enums for channels, statuses, urgency levels and reason codes.
- Return a result object from urgency_rules.py; the router performs HTTP mapping.
- Do not add a dependency unless it is already approved in pyproject.toml.
- Do not modify RAG, agent or investigation modules.

## 8. Security and data handling

- A customer may only submit and view their own complaints.
- Never log card PAN, account number, authentication token, or full request payload.
- Use the existing not-found/authorization convention to avoid resource enumeration.
- Expose public complaint identifiers only.
- Messages must be customer-safe and must not expose internal database details.
- Do not show urgency or internal rules to the customer.

## 9. Test strategy

| **Level** | **Target** | **Coverage** |
|---|---|---|
| Unit | urgency_rules.py | Missing information, amount boundaries ($499.99, $500.00, $999.99, $1,000.00, $2,499.99, $2,500.00), Critical indicator, highest urgency wins, human review flag. |
| Repository | Repository classes | Saving a complaint unchanged and finding complaints only for the right customer. |
| API | FastAPI endpoints | Request validation, response schema, status codes 201/200/401/403/422, login context. |
| Regression | Existing suite | Existing tests still pass. |

## 10. Quality gates

- pytest passes for affected unit and API tests.
- Ruff reports no new violations.
- Black produces no changes.
- mypy passes for affected modules.
- Every acceptance criterion is mapped to at least one test.
- No open clarification is silently implemented.

## 11. Copilot execution instruction

> **GitHub Copilot prompt**
> Read spec.md, plan.md, and tasks.md before editing code. Inspect every referenced repository file. Execute one task at a time in dependency order. Do not invent behaviour for CL-002, CL-003, CL-004 or CL-005. If the specification, plan, task, or existing code conflicts, report the precise conflict before making an assumption. Run the task-specific tests and quality checks after each task.
