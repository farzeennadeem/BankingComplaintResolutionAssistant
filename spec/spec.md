# Specification: Banking Complaint Resolution Assistant


## 1. Objective

Create a guided digital assitant that helps an analyst prepare a recommendation for a complaint by presenting required information, and route any sensitive decision to a human reviewer.

## 2. Problem statement

Complaint handling currently depends on repeated manual checks across structured operational data and unstructured policy documents. Analysts must determine which facts are relevant, whether information is missing, which policy applies and when a case needs escalation. Because the information is spread across systems, handling is slow, inconsistent and difficult to audit. Reviewers also struggle to challenge a recommendation when its sources are unclear.
## 3. Scope

#### In scope
  
- Record a complaint and its available identifiers.
- Identify missing information.
- Present verified facts from approved records.
- Present approved policy evidence with citations.
- Prepare a recommendation.
- Pause sensitive actions for a human reviewer.




#### Out of scope
- Using real or production banking data.
- Automatic final legal, regulatory, fraud, credit or compensation decisions.
- giving the model unrestricted database or system access
- Treating generated text as policy evidence without valid source
- Building every possible complaint process or product integration.



## 4. Requirements
| ID | Requirement |
|---|---|
| FR-001 | The system shall record a complaint with its narrative, channel, received time and available identifiers |
| FR-002 | The system shall identify missing information |
| FR-003 | The system must gather verified facts and policies from approved records with citation before preparing a recommendation|
| FR-004 | The system shall route any high risk decision to a human reviewer |
| FR-005 |The reviewer shall be able to approve, reject or request changes|
| FR-006 |The system shall prompt the analyst with the information the complaint requires but does not include|
| FR-007 |The system shall not give customers access to the investigation assistant. Customers may only submit and view their own complaints.|
| FR-008 | For web, mobile app and email complaints, the system shall store the narrative exactly as submitted. |
| FR-009 | The system shall assign each complaint a controlled category and an urgency using the business rules. |
| FR-010 | The system shall display the urgency together with the rule that determined it. |
| FR-011 | The system shall prepare a draft customer response and shall not send it until a human has approved the outcome. |
| NFR-001 | The system shall use synthetic data only. |
| NFR-002 | Access shall be limited by role: customers shall access only their own complaints, and analysts and reviewers shall access only the functions their role requires. |
| NFR-003 | No secrets or credentials shall be stored in the repository. |
| NFR-004 | Screens and messages shall not display full card or account numbers. |
| NFR-005 | Audit records shall identify who or what performed each action and when, and shall not be editable by analysts. |
| NFR-006 | Every cited policy passage shall include its source document, section, version and effective date. |
| NFR-007 | When a data source or tool fails, the system shall show a clear state, reason and next step, and shall not present a guessed result. |
| NFR-008 | The system shall display a triage result within 5 seconds of a complaint being saved. |
| NFR-009 | Another consultant shall be able to set up, run and test the solution from the repository instructions alone. |
| NFR-010 | Automated tests shall cover normal, boundary, denied and dependency-failure scenarios. |
| NFR-011 | Failures shall be logged so that they are observable. |

## Core flow

A customer logs in and submits a complaint through the website or mobile app. For phone and branch complaints, an advisor submits it on the customer's behalf. The complaint includes its narrative, channel and any available identifiers. The system assigns a complaint ID and received time, sets the status to RECEIVED (or NEEDS_INFORMATION if required information is missing), and returns COMPLAINT_RECORDED. The investigation assistant then picks up the logged complaint; customers never use the assistant.


## 5. Data Model
**Customer**

| Attribute | Description|
|---|---|
| customerId | string |
| name | string|
| segment | string | 

**Account**
| Attribute | Description |
|---|---|
| accountId | string|
| customerId | string |
| type | string (e.g. chequing) | 
| status | string|


**Complaint**

| Attribute | Description 
|---|---|
| complaintId | unique string| 
| accountId | unique string|
| customerId | unique string|
| channel | How the complaint arrived |
| narrative | complaint message |
| receivedAt | Date and time received |
| category | e.g. fee|
| status | Current status |


**Transaction**

| Attribute | Description |
|---|---|
| transactionId | Unique string| 
| accountId | Related account  |
| type | e.g. Scheduled Payment |
| amount | Amount of the transaction | 
| processedAt | | 

**Fee**

| Attribute | Description |
|---|---|
| feeId | Unique string |
| accountId | Related account |
| type | e.g. NSF Fee | 
| amount | Fee amount | 
| chargedAt | |

**Service Request**

| Attribute | Description | 
|---|---|
| requestId | Unique string| 
| accountId | Related account |
| type | e.g. Fee Inquiry  |
| createdAt | When it was created |
| status | e.g. Closed  |

**Status History**

| Attribute | Description | 
|---|---|
| complaintId | The complaint |
| fromStatus | Previous status |
| toStatus | New status |


## 6. Business rules
| ID | Requirement |
|--------|-----------------|
| BR-001 | A complaint shall have urgency of 'Critical' when it explicitly indicates an immediate safety concern, active account takeover, repeated unauthorised activity, or the customer being unable to secure access. |
| BR-002 | A complaint shall have urgency 'High' when the transaction amount is greater than or equal to $2,500, or greater than or equal to $1,000 and the customer explicitly states unauthorized use or fraud. |
| BR-003 | A complaint shall have urgency 'Medium' when the transaction amount is between $500.00 and $2,499.99 inclusive and no Critical indicator is present. |
| BR-004 | A complaint shall have urgency Standard when the transaction amount is below $500.00 and no unauthorised-use, vulnerability or repeat-impact indicator is present. |
| BR-005 | A complaint shall have the state 'Needs Information' when the transaction amount, transaction identity or authorisation statement is missing. The system shall not guess the missing value. |
| BR-006 | The system shall not make final decisions on reimbursement, compensation or liability. Critical and High complaints shall be sent to a human reviewer before any solution. |

## 7. Contracts
### Input

The customer is identified from their login, so the customer ID is not sent in the request. For phone and branch complaints, the advisor also sends the customer ID.

```
{
  "channel": "WEB",
  "narrative": "I do not recognize a $2,750 online electronics purchase.",
  "transactionId": "txn-10045",
  "amount": 2750.00,
  "indicators": ["UNAUTHORISED_USE_STATED"]
}
```

`transactionId`, `amount` and `indicators` are optional. `indicators` lists only the risk indicators the customer or advisor states explicitly. The allowed values depend on CL-005.

### Output

```
{
  "complaintId": "CMP-2026-00481",
  "status": "RECEIVED",
  "reasonCode": "COMPLAINT_RECORDED",
  "message": "Your complaint has been recorded."
}
```

`status` is RECEIVED, or NEEDS_INFORMATION when the amount or transaction ID is missing (BR-005).

### Reason codes
| Code | Meaning |
|---|---|
| COMPLAINT_RECORDED | The complaint was recorded with the status RECEIVED or NEEDS_INFORMATION |
| MISSING_REQUIRED_FIELD| A required field is missing or blank. The response names the field and nothing is recorded |
| RECOMMENDATION_READY | verified facts and policies were gathered and a recommendation is prepared|
| REVIEW_REQUIRED | High risk decision requires a human reviewer |



## 8. Acceptance criteria

| ID | Given / condition | Expected result |
|---|---|---|
| AC-001 | A complaint with a channel, a customer identifier and a narrative | reasonCode=COMPLAINT_RECORDED, a unique complaint ID and received time are assigned |
| AC-002 | A complaint whose narrative is empty | reasonCode=MISSING_REQUIRED_FIELD, response names narrative, nothing is recorded |
| AC-003 | A complaint with missing information | The analyst is shown a prompt for each missing item before a recommendation is prepared |
| AC-004 |Verified facts and an approved policy passage are available, and the proposed action is not high risk or sensitive|reasonCode=RECOMMENDATION_READY, each fact and policy show their source record|
| AC-005 | Amount $499.99, no risk indicator | urgency=Standard |
| AC-006 | Amount $500.00, no Critical indicator | urgency=Medium |
| AC-007 | Amount $1,000.00 with an explicit fraud or unauthorised-use statement | urgency=High |
| AC-008 | Amount $2,500.00 | urgency=High |
| AC-009 | An active account takeover indicator is present | urgency=Critical |
| AC-010 | Amount is missing | status=NEEDS_INFORMATION; no value is guessed |
| AC-011 | A customer asks for another customer's complaints | Rejected with 403 |


## 9. Clarification

| ID | Question | Status | Decision / instruction |
|--------|--------------|------------|----------------------------|
| CL-001 | What amount thresholds define each urgency level? | RESOLVED | High: $2,500.00 or more, or $1,000.00 or more with an explicit unauthorised-use or fraud statement. Medium: $500.00 to $2,499.99. Standard: below $500.00. |
| CL-002 | What urgency applies below $500 when an unauthorized-use, vulnerability or repeat-impact indicator is present? | OPEN | Do not invent behaviour. Confirm with the coach; route to human review until then. |
| CL-003 | If a Critical indicator is present but the amount, transaction identity or authorisation statement is missing, is the complaint Critical or Needs information? | OPEN | Must be confirmed and recorded in the implementation plan. |
| CL-004 | Which currency do the dollar thresholds use, and how are transactions in other currencies handled? | OPEN | The Domain Guide uses CAD. Do not convert or guess; route other currencies to human review until confirmed. |
| CL-005 | How are "vulnerability indicator", "repeat-impact indicator", "repeated unauthorised activity" and "authorisation statement" defined, and what values can the request's indicators list hold? | OPEN | Must be defined before BR-001, BR-004 and BR-005 can be fully tested. Leave the authorisation statement check out until then. |


## 10. Actors and Roles

### Maya (Complaint Analyst)

**Bio**
Maya is a Complaint Analyst at the bank. Complaints arrive by phone, branch, web and email, and she checks several systems by hand to find account history and the relevant policy. She wants one place that shows what is known, what is missing and what the evidence supports.

**Responsibilities**
- Review the complaint intake and identify missing information
- Investigate the evidence from structured records and approved policy
- Validate the evidence and prepare a recommendation
- Submit sensitive or escalated cases to the Supervisor/Reviewer
- Communicate the approved outcome

**Behaviors**
- Detail-oriented
- Evidence-driven
- Methodical
- Cautious about unsupported claims

**Goals**
- Understand the complaint and its urgency quickly
- Verify the customer's history and locate the applicable policy
- Prepare a traceable recommendation for review

**Pain Points**
- Information is spread across systems and documents
- Manual checks are slow, inconsistent and hard to audit
- Missing information is easy to overlook

### Alex (Supervisor/Reviewer)

**Bio**
Alex reviews Critical, High, sensitive or uncertain complaints before any action is taken. Alex is accountable for the outcome, so needs to see where every fact came from and what is still unknown.

**Responsibilities**
- Review sensitive, uncertain or compensatory outcomes before action is taken
- Control high risk decision
- View verified facts, policy evidence with citations, the proposed action and the reasoning trace
- Approve, reject or request changes on a proposed action
- Escalate a case to a specialist when there is high risk or an exception
- Record a rationale for each decision

**Behaviors**
- Risk-aware
- Thorough
- Accountable for decisions
- Challenges weak evidence

**Goals**
- Review a complete evidence package quickly
- Approve, reject or request changes with a clear rationale
- Keep sensitive decisions under human control

**Pain Points**
- Incomplete evidence packages
- Hard to tell verified facts from generated analysis
- Unclear audit trail of who decided what

### Delivery Reviewer (Coach)

**Bio**
The Delivery Reviewer assesses consultant work during training. They check that the solution is reproducible, traceable and safe, and they have no role in individual complaint decisions.

**Responsibilities**
- Confirm that the consultant solution is reproducible, traceable and safe
- Inspect test evidence, source references, step records, approval records and setup documentation
- Review whether the specification, plan and tasks trace to each other

**Behaviors**
- Quality-focused
- Systematic
- Asks "what is the source for this?"

**Goals**
- Confirm the solution can be set up and tested from the repository
- Trace recommendations back to facts and sources
- Confirm safety controls work

**Pain Points**
- Missing tests or setup documentation
- Results that can't be traced to evidence
- Unclear design decisions

### Jordan Lee (Customer)

**Bio**
Jordan is a Personal Banking customer who has raised a complaint. Jordan never uses the internal assistant and only receives the human-approved response.

**Responsibilities**
- Provide the complaint
- Provide additional information when asked
- Receive the human-approved response

**Behaviors**
- Contacts the bank through everyday channels
- Expects a prompt, clear reply
- Wants an explanation, not just an outcome

**Goals**
- Have the complaint understood and handled fairly
- Receive an accurate, easy-to-follow response

**Pain Points**
- Waiting without updates
- Repeating the same story to different people
- Vague or inconsistent explanations

# 11. Assumptions

- The supplied policy documents are the approved knowledge base. No other source counts as policy evidence.
- Every complaint comes from a registered customer and links to an existing customer and account record. Complaints from non-customers are out of scope.
- Analysts and reviewers are authenticated before they use the assistant, and authentication already identifies the current user and their role.
- Customers log in through the bank's existing login to submit and view their own complaints. For phone and branch complaints, an advisor submits on the customer's behalf. Customers never use the investigation assistant.
- Each complaint refers to one transaction.
- The data and policy sources needed for investigation are available. When one is not, the system reports the failure instead of guessing.