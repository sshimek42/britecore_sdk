# Phase 1: Client Lifecycle Design Notes (Archived)

*Last updated: July 22, 2026*
*Document type: Archived implementation record (reference/archive)*

## Overview

This archived note explains the client-lifecycle design work that landed around the first stable 2.x release.
The main change was a shift in recommended examples from implicit module-level client usage to explicit client ownership.

This is **not** a policy document saying all existing integrations must be rewritten immediately.
It exists to explain why explicit `client=` examples became the preferred pattern for new code.

---

## Why the explicit client pattern was introduced

Explicit client ownership improves:

- **Testability** — dependencies are visible and easy to mock
- **Multi-site usage** — separate clients can coexist safely
- **Readability** — the call site shows which client performs the request
- **Lifecycle control** — context managers and explicit cleanup are straightforward

---

## Quick Reference

| Pattern | Earlier implicit-client usage | Explicit-client pattern highlighted in 2.x |
|---------|-------------------------------|--------------------------------------------|
| **Setup** | `init_api_client(target_site="site")` | `client = BritecoreAPIClient("site").init_client()` |
| **Use** | `retrieve_quote(quote_id="Q123")` | `retrieve_quote(quote_id="Q123", client=client)` |
| **Cleanup** | Shared/module-level lifecycle | `client.close()` or context manager |
| **Multi-site** | Swap module-level state carefully | Multiple explicit client instances |

---

## Pattern Comparison

### Simple one-site script

**Earlier implicit-client pattern:**

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import quotes, policies

init_api_client(target_site="production")
quote = quotes.retrieve_quote(quote_number="Q123")
policy = policies.retrieve_policy(policy_number="P456")
```

**Explicit-client pattern:**

```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes, policies

with BritecoreAPIClient("production").init_client() as client:
    quote = quotes.retrieve_quote(quote_number="Q123", client=client)
    policy = policies.retrieve_policy(policy_number="P456", client=client)
```

### Multi-site usage

**Earlier shared-state pattern:**

```python
from britecore_sdk.api.api_calls import init_api_client, reset_api_client
from britecore_sdk.api.api_calls.v2 import quotes

client_a = init_api_client(target_site="site_a")
quote_a = quotes.retrieve_quote(quote_number="Q1")

reset_api_client()

client_b = init_api_client(target_site="site_b")
quote_b = quotes.retrieve_quote(quote_number="Q2")
```

**Explicit multi-client pattern:**

```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes

client_a = BritecoreAPIClient("site_a").init_client()
client_b = BritecoreAPIClient("site_b").init_client()

quote_a = quotes.retrieve_quote(quote_number="Q1", client=client_a)
quote_b = quotes.retrieve_quote(quote_number="Q2", client=client_b)

client_a.close()
client_b.close()
```

### Testing

**Earlier patch-heavy pattern:**

```python
from unittest.mock import patch, MagicMock
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import quotes


def test_get_quote():
    init_api_client(target_site="test")

    with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
        mock.do_request.return_value = MagicMock()
        mock.process_result.return_value = {"id": "Q1", "premium": 100}

        result = quotes.get_quote(quote_id="Q1")
        assert result["premium"] == 100
```

**Explicit-client test pattern:**

```python
from unittest.mock import MagicMock
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes


def test_get_quote():
    mock_client = MagicMock(spec=BritecoreAPIClient)
    mock_client.do_request.return_value = MagicMock()
    mock_client.process_result.return_value = {"id": "Q1", "premium": 100}

    result = quotes.get_quote(quote_id="Q1", client=mock_client)

    assert result["premium"] == 100
    mock_client.do_request.assert_called_once()
```

---

## Compatibility Note

Older implicit-client usage may still appear in codebases and historical examples.
This document should not be read as a blanket deprecation/removal promise for every older call pattern.
Instead, treat the explicit-client approach as the preferred direction for:

- new examples,
- tests,
- multi-site workflows,
- code that benefits from explicit lifecycle control.

---

## Practical Adoption Checklist

Use this list when you choose to modernize an existing integration:

- [ ] Replace shared/module-level client assumptions with explicit `client=` passing where practical
- [ ] Prefer `with BritecoreAPIClient(...).init_client() as client:` when automatic cleanup is useful
- [ ] Update tests to inject mock clients directly instead of patching module-level state
- [ ] Keep supported `api_calls/v1` wrappers when they are still the correct upstream/API match
- [ ] Verify behavior with targeted tests after any modernization work

---

## FAQ

### Do I have to migrate immediately?

No. Use explicit client ownership for new code and for places where it clearly improves maintainability.

### Can I still use shared helpers such as `get_api_client()`?

Yes. Shared lazy client access remains a valid SDK capability. This note only explains why many newer examples prefer explicit ownership.

### Does this document mean `api_calls/v1` wrappers are legacy?

No. Upstream API version numbers and client lifecycle patterns are separate concerns.
`api_calls/v1` wrappers remain supported when they are the correct wrapper for the upstream API.

---

## Summary

The enduring lesson from Phase 1 is simple:

- **Prefer explicit clients in new examples and tests**
- **Do not infer a blanket v1-endpoint removal policy from this archived design note**
- **Modernize older code when it provides value, not because the SDK requires a forced rewrite**
