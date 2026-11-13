# Implementation Tasks: Banking Complaint Resolution

> **Execution model**
> These are engineering implementation tasks, not Agile user stories. They are derived from the approved specification and technical plan, and GitHub Copilot should execute them in dependency order. Each task is bounded by files, requirements, acceptance criteria, tests and a definition of done.

## TASK-001: Create complaint, response, and enum schemas

| **Field** | **Value** |
|---|---|
| Requirements | FR-001, FR-008 |
| Files | src/complaints/schemas.py |

### Implementation instructions

- Define the channel values PHONE, BRANCH, WEB, EMAIL and MOBILE_APP.
- Define the urgency values Critical, High, Medium and Standard, and the statuses.
- Define the reason codes COMPLAINT_RECORDED and MISSING_REQUIRED_FIELD.
- Use Decimal for amount, not float.
- Reject unsupported channels and an empty narrative.

### Definition of done

- Schema unit tests pass.

### Copilot command

Implement TASK-001 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## TASK-002: Create the Database Models

| **Field** | **Value** |
|---|---|
| Requirements | FR-002 |
| Files | src/customers/models.py; src/complaints/models.py |

### Implementation instructions

- Use synthetic data only.
- Create a customer table with customer ID, name and segment.
- Create a complaint table with complaint ID, customer ID, channel, narrative, received time, category and status.
- Add fields to hold the urgency and the rule that set it.
- Create a status history table.

### Definition of done

- Model unit tests pass.
- Attributes match the specification's data model.
- No real production data is present.

### Copilot command

Implement TASK-002 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## TASK-003: Save a complaint and find the right customer's complaints

| **Field** | **Value** |
|---|---|
| Requirements | FR-001, FR-007, FR-008 |
| Files | src/complaints/repository.py; src/customers/repository.py; src/core/clock.py; tests/integration/complaints/test_complaints_api.py |

### Implementation instructions

- Check that the customer is registered before saving a complaint.
- Save the complaint with its narrative, channel, received time and customer ID.
- Save the narrative exactly as the customer wrote it.
- Get the received time from clock.py so tests can set the time.
- Give each complaint its own unique ID.
- Find complaints by customer ID, and return only that customer's complaints.

### Definition of done

- A saved complaint can be found again with the same narrative.
- Asking for one customer's complaints never returns another customer's.
- All database code stays in the two repository files.

### Copilot command

Implement TASK-003 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## TASK-004: Implement missing information check

| **Field** | **Value** |
|---|---|
| Requirements | FR-002, BR-005 |
| Files | src/complaints/urgency_rules.py; tests/unit/complaints/test_urgency_rules.py |

### Implementation instructions

- If the amount is missing, set the status to Needs Information.
- If the transaction ID is missing, set the status to Needs Information.
- Say which item is missing.
- Never guess or fill in a missing value.
- Leave the authorisation statement check out until it is defined.

### Definition of done

- Tests cover each missing item and the case where nothing is missing.

### Copilot command

Implement TASK-004 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## TASK-005: Work out the urgency of a complaint

| **Field** | **Value** |
|---|---|
| Requirements | FR-001, BR-001, BR-002, BR-003, BR-004 |
| Files | src/complaints/urgency_rules.py; tests/unit/complaints/test_urgency_rules.py |

### Implementation instructions

- Critical applies when a Critical indicator is present.
- High applies at \$2,500.00 or more, or at \$1,000.00 or more with a fraud or unauthorised-use statement.
- Medium applies from \$500.00 to \$2,499.99, with no Critical indicator.
- Standard applies below \$500.00 with no risk indicator.
- Record which rule set the urgency.
- If a complaint is below \$500 and has a risk indicator, do not mark it Standard. Send it to human review (CL-002).
- Do not convert currencies (CL-004).

### Definition of done

- Tests exist at \$499.99, \$500.00, \$999.99, \$1,000.00, \$2,499.99 and \$2,500.00.
- A test covers a Critical indicator.
- Each test checks which rule was applied.

### Copilot command

Implement TASK-005 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## TASK-006: Route critical and high-risk complaints to human review

| **Field** | **Value** |
|---|---|
| Requirements | FR-004, BR-006 |
| Files | src/complaints/urgency_rules.py; tests/unit/complaints/test_urgency_rules.py |

### Implementation instructions

- Mark a complaint as requiring human review when its urgency is Critical or High.
- Return REVIEW_REQUIRED for a complaint that requires review.

### Definition of done

- No complaint marked for review is processed further without a recorded decision.

### Copilot command

Implement TASK-006 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## TASK-007: Add the endpoint to submit a complaint

| **Field** | **Value** |
|---|---|
| Requirements | FR-001, FR-007, FR-008, FR-009 |
| Files | src/complaints/router.py; src/main.py; tests/integration/complaints/test_complaints_api.py |

### Implementation instructions

- Add POST /api/v1/complaints.
- Find the customer from the login, not from the request. For phone and branch complaints, the advisor also sends the customer ID.
- Save the complaint, then work out the urgency using TASK-004 to TASK-006.
- Return the complaint ID, status, reason code and message.
- If the narrative is empty, return 422 with MISSING_REQUIRED_FIELD and save nothing.
- If the user is not logged in, return 401.

### Definition of done

- Add POST /api/v1/complaints.
- Find the customer from the login, not from the request. For phone and branch complaints, the advisor also sends the customer ID.
- Save the complaint, then work out the urgency using TASK-004 to TASK-006.
- Return the complaint ID, status, reason code and message.
- If the narrative is empty, return 422 with MISSING_REQUIRED_FIELD and save nothing.
- If the user is not logged in, return 401.

### Copilot command

Implement TASK-007 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## TASK-008: Add the endpoint to view a complaint

| **Field** | **Value** |
|---|---|
| Requirements | FR-007 |
| Files | src/complaints/router.py; tests/integration/complaints/test_complaints_api.py |

### Implementation instructions

- Add GET /api/v1/customers/{customer_id}/complaints.
- Return the complaint ID, channel, received time and status for each complaint.
- If the logged-in customer asks for someone else's complaints, return 403.

### Definition of done

- A customer sees their own complaints.
- A customer asking for another customer's complaints gets 403.

### Copilot command

Implement TASK-008 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## TASK-009: Implement front-end (incomplete section)

| **Field** | **Value** |
|---|---|
| Requirements | All |
| Files | frontend/src/pages/SubmitComplaint.jsx; frontend/src/pages/MyComplaints.jsx; frontend/src/components/ComplaintForm.jsx; frontend/src/components/ComplaintList.jsx; frontend/src/components/StatusBadge.jsx; frontend/src/api/complaintsApi.js |

### Implementation instructions

### Definition of done

## TASK-010: Complete traceability and quality checks

| **Field** | **Value** |
|---|---|
| Requirements | All |
| Files | tests; spec/; no unrelated production files |

### Implementation instructions

- Map tests to acceptance criteria IDs.
- Confirm automated tests cover normal, boundary, denied and dependency failure scenarios (NFR-010).
- Review the final diff for unrelated changes.

### Definition of done

- All quality gates pass.
- No open clarification was guessed.
- The implementation matches spec and plan.

### Copilot command

Implement TASK-010 only. Read the specification and plan first. Modify only the listed files unless a build-preserving change is necessary. Run the tests and quality checks named in this task, then summarize changed files, requirement coverage, test results, and unresolved questions.

## Final review checklist

- No refund, investigation, evidence, RAG, agent, or complaint-resolution functionality was added.
- No fictional GitHub URL was treated as a real production dependency.
- No open clarification was resolved by assumption.
- No sensitive banking data is logged or exposed.
- Customers can only submit and view their own complaints, and no final decision on reimbursement, compensation or liability is made.
- The final change set is traceable from requirement to task to test.
