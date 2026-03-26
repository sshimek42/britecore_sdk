# API Reference

**BriteCore Libraries** - Complete API endpoint documentation

---

## Overview

This document provides reference for all implemented API endpoints.

**Total Endpoints:** 374 in britecore_api.json  
**Currently Implemented:** 250 endpoints (66.8%)  
**Coverage by Category:** See sections below

---

## Authentication

All API calls require authentication (automatic):

```python
# API Key Authentication (if client_id/client_secret blank)
headers = {"Authorization": "ApiKey <api_key>"}

# OAuth2 Authentication (if client_id/client_secret provided)
headers = {"Authorization": "Bearer <access_token>"}
```

---

## Request/Response Pattern

### Standard Request

```python
from britecore_libraries.api.api_calls.v2 import policies
from britecore_libraries.api.api_calls import RequestParameters

response = policies.retrieve_policy(
    policy_number="POL001",
    request_timeout=5,        # seconds
    request_retries=3,        # number of retries
    # ... endpoint-specific params ...
)
```

### Standard Response

```python
{
    "success": True,
    "data": {
        "id": "uuid",
        "policy_number": "POL001",
        # ... policy fields ...
    },
    "message": "Success"  # or "messages": ["msg1", "msg2"]
}
```

---

## Implemented Endpoints

### 1. Policies (87 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/policies.py`

#### Policy Retrieval

```python
from britecore_libraries.api.api_calls.v2.policies import (
    retrieve_policy,
    retrieve_policies_by_contact_id,
    retrieve_revision_status,
)

# Get single policy
policy = retrieve_policy(policy_number="POL001")
policy = retrieve_policy(policy_id="uuid")

# Get multiple policies
policies = retrieve_policies_by_contact_id(contact_id="uuid")

# Get revision status
status = retrieve_revision_status(revision_id="uuid")
```

#### Policy Management

```python
from britecore_libraries.api.api_calls.v2.policies import (
    create_full_policy,
    new_revision_contact,
    create_risk,
    add_line_item,
)

# Create new policy
policy = create_full_policy(policy_json={...})

# Add revision contact
contact = new_revision_contact(revision_id="uuid", ...)

# Add risk/property
risk = create_risk(revision_id="uuid", ...)

# Add line item
item = add_line_item(revision_id="uuid", item_id="uuid")
```

---

### 2. Contacts (42 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/contacts.py`

```python
from britecore_libraries.api.api_calls.v2.contacts import (
    retrieve_contact,
    create_contact,
    update_contact,
    remove_contact_from_role,
)

# Retrieve contact
contact = retrieve_contact(contact_id="uuid")

# Create new contact
contact = create_contact(contact_json={...})

# Update contact
updated = update_contact(contact_id="uuid", ...)

# Remove role
remove_contact_from_role(contact_id="uuid", role_name="Named Insured")
```

---

### 3. Quotes (15 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/quotes.py`

```python
from britecore_libraries.api.api_calls.v2.quotes import (
    create_full_quote,
    get_quote,
    update_quote,
)

# Create quote
quote = create_full_quote(quote_json={...})

# Retrieve quote
quote = get_quote(quote_id="uuid")

# Update quote
updated = update_quote(quote_id="uuid", ...)
```

---

### 4. Reports (14 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/reports.py`

```python
from britecore_libraries.api.api_calls.v2.reports import (
    retrieve_reports,
    retrieve_report,
    create_report,
)

# List reports
reports = retrieve_reports(policy_id="uuid")

# Get single report
report = retrieve_report(report_id="uuid")

# Create new report
report = create_report(report_json={...})
```

---

### 5. Deliverables (24 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/deliverables.py`

```python
from britecore_libraries.api.api_calls.v2.deliverables import (
    get_deliverables,
    create_deliverable,
)

# List deliverables
deliverables = get_deliverables(policy_id="uuid")

# Create deliverable
deliverable = create_deliverable(deliverable_json={...})
```

---

### 6. Utilities (24 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/utils.py`

```python
from britecore_libraries.api.api_calls.v2.utils import (
    get_available_function_names,
    rebuild_search_index,
    meta,
)

# Get available functions
functions = get_available_function_names()

# Rebuild search
rebuild_search_index()

# Get metadata
meta_info = meta()
```

---

### 7. Lines (16 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/lines.py`

```python
from britecore_libraries.api.api_calls.v2.lines import (
    get_lines,
    create_line,
    update_line,
)

# Get lines
lines = get_lines(revision_id="uuid")

# Create line
line = create_line(revision_id="uuid", ...)

# Update line
updated = update_line(line_id="uuid", ...)
```

---

### 8. Claims (7 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/claims.py`

```python
from britecore_libraries.api.api_calls.v2.claims import (
    get_claims,
    retrieve_claim,
    create_claim,
)

# List claims
claims = get_claims(policy_id="uuid")

# Get claim
claim = retrieve_claim(claim_id="uuid")

# Create claim
claim = create_claim(claim_json={...})
```

---

### 9. Insured (16 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/insured.py`

```python
from britecore_libraries.api.api_calls.v2.insured import (
    get_insureds,
    add_insured,
)

# List insureds
insureds = get_insureds(policy_id="uuid")

# Add insured
insured = add_insured(policy_id="uuid", ...)
```

---

### 10. Notes (4 endpoints) ✅ COMPLETE

**File:** `api/api_calls/v2/notes.py`

```python
from britecore_libraries.api.api_calls.v2.notes import (
    get_notes,
    create_note,
)

# Get notes
notes = get_notes(policy_id="uuid")

# Create note
note = create_note(policy_id="uuid", ...)
```

---

### 11. Inspections (1 endpoint) ✅ COMPLETE

**File:** `api/api_calls/v2/inspections.py`

```python
from britecore_libraries.api.api_calls.v2.inspections import (
    get_inspections,
)

# Get inspections
inspections = get_inspections(policy_id="uuid")
```

---

## Not Yet Implemented

### High Priority (42 endpoints)

- ❌ **payments.py** (29 endpoints) - Payment processing [CRITICAL]
- ❌ **billing.py** (4 endpoints) - Billing management
- ❌ **commissions.py** (9 endpoints) - Commission tracking

### Medium Priority (61 endpoints)

- ❌ **settings.py** (11 endpoints)
- ❌ **vendors.py** (16 endpoints)
- ❌ **attachments.py** (11 endpoints)
- ❌ **dashboards.py** (8 endpoints)
- ❌ **nightly_jobs.py** (4 endpoints)
- ❌ **printing.py** (5 endpoints)
- ❌ **intacct.py** (5 endpoints)
- ❌ **signatures.py** (6 endpoints)

### Low Priority (21 endpoints)

- ❌ **accounting.py** (3 endpoints)
- ❌ **custom_ui.py** (4 endpoints)
- ❌ **notifications.py** (2 endpoints)
- ❌ **search.py** (2 endpoints)
- ❌ **data.py** (2 endpoints)
- ❌ **errors.py** (1 endpoint)
- ❌ **uploads.py** (1 endpoint)
- ❌ **return_premium.py** (1 endpoint)

See [API_COVERAGE_ANALYSIS.md](API_COVERAGE_ANALYSIS.md) for implementation roadmap.

---

## Common Request Parameters

All endpoints support these optional parameters:

```python
from urllib3 import Timeout, Retry

endpoint(
    # ... required and optional endpoint-specific parameters ...
    request_timeout=Timeout(total=5),      # Custom timeout
    request_retries=Retry(total=3),        # Custom retries
)
```

---

## Error Handling

```python
from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.api.api_calls.v2 import policies

try:
    policy = policies.retrieve_policy(policy_number="INVALID")
except BritecoreError.NoDataReturned as e:
    print(f"Not found: {e}")
except BritecoreError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Rate Limiting

The API implements rate limiting. If you receive 429 status:

```python
import time
from britecore_libraries.api.api_calls.v2 import policies

max_retries = 3
retry_delay = 5  # seconds

for attempt in range(max_retries):
    try:
        policy = policies.retrieve_policy(policy_number="POL001")
        break
    except BritecoreError.NoDataReturned as e:
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
        else:
            raise
```

---

## Pagination

Some endpoints support pagination:

```python
from britecore_libraries.api.api_calls.v2 import reports

# Get first page
reports = get_reports(
    policy_id="uuid",
    page=1,
    page_size=25
)

# Get next page
reports = get_reports(
    policy_id="uuid",
    page=2,
    page_size=25
)
```

---

## Filtering and Sorting

Many endpoints support filters:

```python
from britecore_libraries.api.api_calls.v2 import claims

# Filter claims
claims = get_claims(
    policy_id="uuid",
    status="open",
    sort="date_created",
    sort_direction="desc"
)
```

---

## Batch Operations

For bulk operations, use loops rather than batch endpoints (most don't exist):

```python
from britecore_libraries.api.api_calls.v2 import policies

policy_numbers = ["POL001", "POL002", "POL003"]

for policy_number in policy_numbers:
    try:
        policy = policies.retrieve_policy(policy_number=policy_number)
        process_policy(policy)
    except Exception as e:
        logger.error(f"Failed for {policy_number}: {e}")
```

---

## Using with Models

```python
from britecore_libraries.models import BritecorePolicy
from britecore_libraries.api.api_calls.v2 import policies

# Create policy from model
policy_model = BritecorePolicy(
    policy_number="POL001",
    effective_date=datetime.now(),
    policy_type_id="type_1",
    contacts=[]
)

# Convert to API format
api_payload = policy_model.to_dict()

# Submit to API
response = policies.create_full_policy(policy_json=api_payload)
```

---

## Using with Validators

```python
from britecore_libraries.validators import EmailValidator, PhoneValidator
from britecore_libraries.api.api_calls.v2 import contacts

# Validate data before submission
email_data = [{"email": "test@example.com", "type": "Home"}]
phone_data = [{"phone": "5551234567", "type": "Home"}]

emails = EmailValidator(email_data).process()
phones = PhoneValidator(phone_data).process()

# Create contact with validated data
contact = contacts.create_contact(
    contact_json={
        "name": "John Doe",
        "emails": emails,
        "phones": phones
    }
)
```

---

## Webhook/Callback Pattern

For long-running operations, poll for completion:

```python
import time
from britecore_libraries.api.api_calls.v2 import reports

# Create report
report = create_report(report_json={...})
report_id = report["id"]

# Poll for completion
max_wait = 300  # 5 minutes
poll_interval = 5

start = time.time()
while time.time() - start < max_wait:
    status = retrieve_report(report_id=report_id)
    if status["status"] == "completed":
        return status
    time.sleep(poll_interval)

raise TimeoutError(f"Report {report_id} did not complete")
```

---

## Examples by Use Case

### Get a Policy and All Related Data

```python
from britecore_libraries.api.api_calls.v2 import policies, contacts, lines, claims

# Get policy
policy = policies.retrieve_policy(policy_number="POL001")

# Get contacts
policy_contacts = contacts.retrieve_contacts(policy_id=policy["id"])

# Get lines
policy_lines = lines.get_lines(revision_id=policy["active_revision"]["id"])

# Get claims
policy_claims = claims.get_claims(policy_id=policy["id"])

# Combine
complete_policy = {
    **policy,
    "contacts": policy_contacts,
    "lines": policy_lines,
    "claims": policy_claims
}
```

---

### Create New Policy with Validation

```python
from britecore_libraries.models import BritecoreContact, BritecorePolicy
from britecore_libraries.validators import EmailValidator
from britecore_libraries.api.api_calls.v2 import policies

# Create contact with validation
contact = BritecoreContact(
    name="Jane Doe",
    email=[{"email": "jane@example.com", "type": "Home"}]
)

# Create policy
policy = BritecorePolicy(
    policy_number="POL002",
    effective_date=datetime.now(),
    policy_type_id="type_1",
    contacts=[contact]
)

# Validate and submit
policy_data = policy.to_dict()
response = policies.create_full_policy(policy_json=policy_data)
```

---

See [README.md](README.md) for more examples and [CONTRIBUTING.md](CONTRIBUTING.md) for adding new endpoints.

---

**API Version:** 2.0.0  
**Last Updated:** March 26, 2026  
**Status:** 250/374 endpoints implemented (66.8%)

