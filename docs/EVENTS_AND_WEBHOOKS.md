# Events and Webhooks

*Last updated: July 22, 2026* (expanded with webhook framework, event catalog, and integration webhooks reference)
*Document type: Living guide*

For integration engineers: align event-driven and webhook-driven workflows with SDK usage patterns.

---

## Overview

BriteCore operational integrations often combine:

- **API wrapper calls** from this SDK (request/response interactions), and
- **Events/webhooks** for asynchronous workflow notifications.

This guide captures practical patterns that complement SDK usage for event-driven systems.

---

## Core principles

1. Treat webhook/event deliveries as **at-least-once**.
2. Make downstream consumers **idempotent**.
3. Use correlation IDs for traceability across API calls and event handling.
4. Keep event-side retries and API-side retries coordinated.

---

## Envelope and payload handling

When consuming webhook/event payloads:

- Validate required envelope fields before processing.
- Persist a dedupe key (for example event ID + topic + created timestamp) before side effects.
- Store raw payloads for incident replay and debugging.
- Avoid coupling tightly to optional fields that may evolve.

> **Note:** API wrapper responses in this SDK are generally normalized through `process_result(...)`.
> Event/webhook payload contracts are separate and should be validated independently.

---

## Idempotency pattern

A minimal event consumer pattern:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EventRecord:
    event_id: str
    topic: str
    payload: dict[str, Any]


def already_processed(event_id: str) -> bool:
    # Replace with datastore lookup
    return False


def mark_processed(event_id: str) -> None:
    # Replace with durable write
    return None


def handle_event(record: EventRecord) -> None:
    if already_processed(record.event_id):
        return

    # Perform side effects only once.
    # Keep this block small and retry-safe.
    process_payload(record.topic, record.payload)
    mark_processed(record.event_id)


def process_payload(topic: str, payload: dict[str, Any]) -> None:
    # Domain-specific routing logic lives here.
    return None
```

---

## Retry coordination

Use a clear separation of concerns:

- **Webhook receiver retries:** handle network/transient failures on inbound delivery paths.
- **SDK request retries:** use `request_retries` and client retry config for outbound API calls.

Recommended approach:

- Keep outbound SDK calls from webhook handlers short-lived.
- Use queueing for expensive follow-up work.
- Prefer exponential backoff and dead-letter routing for repeated failures.

---

## Correlation and observability

Each outbound SDK request includes `X-SDK-Request-ID`.

Use this value together with your event identifiers:

- log event ID and topic at ingress,
- log SDK request IDs for all follow-up calls,
- attach both IDs to alerting and incident traces.

This makes it easier to trace "event received -> SDK request sent -> downstream status".

---

---

## Webhook framework and listener setup

The SDK provides a webhook framework for receiving and handling events from BriteCore. The `WebhookListener` class handles event registration, signature verification, and dispatching:

```python
from britecore_sdk.webhooks import WebhookListener

# Create a listener with your webhook secret
listener = WebhookListener(secret="your-webhook-secret-from-britecore")

# Register event handlers using decorators
@listener.on("policy.created")
def handle_policy_created(event):
    print(f"Policy created: {event.data['policy_id']}")
    # Process the event...

@listener.on("quote.updated")
def handle_quote_updated(event):
    print(f"Quote updated: {event.data['quote_id']}")

# In your Flask/FastAPI endpoint:
@app.post("/webhooks/britecore")
def receive_webhook(request):
    payload = request.get_json()
    signature = request.headers.get("X-BriteCore-Signature")

    # Process and dispatch to registered handlers
    success = listener.process_webhook(payload, signature)
    return {"success": success}
```

### Event payload structure

BriteCore webhook payloads follow this envelope structure:

```json
{
  "type": "policy.created",
  "timestamp": "2026-07-22T14:30:00Z",
  "data": {
    "policy_id": "POL123456",
    "policy_number": "POL-2026-0001",
    "insured_name": "Jane Doe",
    "effective_date": "2026-08-01",
    "status": "active"
  }
}
```

### Common event topics

Common event types (topics) include:

| Topic | Description | Common data fields |
|-------|-------------|-------------------|
| `policy.created` | Policy has been created | `policy_id`, `policy_number`, `insured_name`, `effective_date` |
| `policy.updated` | Policy has been modified | `policy_id`, `policy_number`, `changes` |
| `policy.cancelled` | Policy has been cancelled | `policy_id`, `policy_number`, `effective_date` |
| `quote.created` | Quote has been created | `quote_id`, `insured_name`, `created_date` |
| `quote.updated` | Quote has been modified | `quote_id`, `changes` |
| `quote.expired` | Quote has expired | `quote_id`, `expiration_date` |
| `contact.created` | Contact has been created | `contact_id`, `first_name`, `last_name`, `email` |
| `contact.updated` | Contact has been modified | `contact_id`, `changes` |
| `risk.created` | Risk/asset has been added | `risk_id`, `policy_id`, `risk_type` |
| `risk.updated` | Risk/asset has been modified | `risk_id`, `changes` |
| `claim.created` | Claim has been filed | `claim_id`, `policy_id`, `claim_date` |
| `claim.updated` | Claim status has changed | `claim_id`, `status` |

### Signature verification

All webhooks include a signature header for security. Verify signatures before processing:

```python
from britecore_sdk.webhooks import WebhookListener

listener = WebhookListener(secret="your-webhook-secret")

# WebhookListener.process_webhook() verifies automatically if signature is provided
payload = {"type": "policy.created", "data": {...}}
signature = request.headers.get("X-BriteCore-Signature")

if not listener.verify_signature(json.dumps(payload), signature):
    # Reject unsigned webhook
    return {"error": "Invalid signature"}, 401
```

---

## Integration webhooks reference

Beyond direct event subscriptions, BriteCore provides integration point codes for third-party integrations. These define where and how external systems can integrate with BriteCore workflows.

### Integration point codes

Common integration point codes include:

| Code | Name | Purpose | Typical consumers |
|------|------|---------|------------------|
| `DOCUMENT_GENERATION` | Document Generation | Generate policy documents externally | Third-party document systems |
| `POLICY_BINDING` | Policy Binding | Bind policies to carrier systems | Carrier systems, MGA platforms |
| `QUOTE_PRICING` | Quote Pricing | Calculate custom pricing logic | Pricing engines, actuarial systems |
| `RISK_ASSESSMENT` | Risk Assessment | External risk evaluation | Risk assessment tools, analytics |
| `CLAIMS_MANAGEMENT` | Claims Management | Route claims to external systems | Claims processing platforms |
| `BILLING_INTEGRATION` | Billing Integration | Send billing data to accounting systems | Accounting software, ERP systems |
| `COMPLIANCE_REPORTING` | Compliance Reporting | Export data for compliance | Compliance platforms, auditors |
| `CUSTOMER_NOTIFICATION` | Customer Notification | Notify customers via external channels | Email/SMS providers, CRM systems |

### Checking integration point availability

Use the integrations API to determine which integration points are installed:

```python
from britecore_sdk.api.api_calls.v2 import integrations

# Check if a specific integration point is installed
result = integrations.is_integration_point_installed(
    integration_point_code="DOCUMENT_GENERATION",
    policy_type_id="policy_type_123"
)

# List all available integration points
all_points = integrations.list_integration_points()

# Get installed integrations for a policy type
installed = integrations.get_installed_integrations(
    policy_type_id="policy_type_123",
    integration_point_code="QUOTE_PRICING"
)
```

### Integration data persistence

When integrating via webhooks or integration points, persist data back to BriteCore:

```python
from britecore_sdk.api.api_calls.v2 import integrations

# Store a file from external processing
integrations.persist_file(
    file_data_base64="base64-encoded-file-content",
    integration_instance_external_id="ext_id_123",
    mime_type="application/pdf",
    title="Generated Policy Document"
)

# Add notes/comments
integrations.make_note(
    integration_instance_external_id="ext_id_123",
    reference_id="ref_123",
    contents="Document generated successfully",
    title="Processing Note"
)

# Send email through BriteCore
integrations.send_britecore_email(
    integration_instance_external_id="ext_id_123",
    subject="Policy Ready",
    to_emails=["customer@example.com"],
    html_body="Your policy is ready for download",
    plain_body="Your policy is ready for download"
)
```

---

## Related SDK modules and docs

- Webhook framework: `src/britecore_sdk/webhooks/` (WebhookListener, WebhookEvent, WebhookManager)
- Integration API wrappers: `src/britecore_sdk/api/api_calls/v2/integrations.py`
- All API wrappers: `src/britecore_sdk/api/api_calls/v2/`
- API narrative guide: `API.md`
- Observability: `docs/OBSERVABILITY.md`
- Rate limiting and backoff: `docs/RATE_LIMITING.md`
- Troubleshooting: `TROUBLESHOOTING.md`

---

## Practical checklist

Before shipping an event-driven integration:

- [ ] Event/webhook payload validation is explicit.
- [ ] Idempotency keys are persisted durably.
- [ ] Retries are bounded with backoff and dead-letter strategy.
- [ ] SDK request correlation IDs are logged.
- [ ] Runbooks include replay and recovery steps.
- [ ] Webhook signatures are verified on all inbound requests.
- [ ] Integration points are checked before assuming availability.
- [ ] Integration data persistence (files, notes, emails) is implemented where needed.
