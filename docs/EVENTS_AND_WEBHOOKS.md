# Events and Webhooks

*Last updated: July 22, 2026*
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

## Related SDK modules and docs

- API wrappers: `src/britecore_sdk/api/api_calls/v2/`
- Vendor/integration endpoints (example webhook-related utilities): `src/britecore_sdk/api/api_calls/v2/vendors.py`
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
