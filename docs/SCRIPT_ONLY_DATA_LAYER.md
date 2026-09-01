# Script-Only Data Layer

Use `britecore_sdk.data_layer` when your script only needs payload shaping and normalization.

This layer avoids API transport concerns (`get_api_client`, auth, retries) and focuses on:

- Models (`BritecoreContact`, `BritecorePolicy`, `BritecoreQuote`)
- Validators (`AddressValidator`, `EmailValidator`, `NameValidator`, `PhoneValidator`)
- Convenience helpers for normalized payloads

## Helpers

- `normalize_name(name)`
- `normalize_address(address)`
- `normalize_phones(phone_numbers)`
- `normalize_emails(emails)`
- `normalize_contact_payload(...)`
- `normalize_policy_payload(...)`
- `normalize_quote_payload(...)`

## Quick example

```python
import datetime as dt

from britecore_sdk.data_layer import (
    normalize_contact_payload,
    normalize_policy_payload,
    normalize_quote_payload,
)

contact = normalize_contact_payload(
    name="acme llc",
    address={
        "address_line1": "123 Main St",
        "address_city": "Madison",
        "address_state": "WI",
        "address_zip": "53703",
    },
    phone_numbers=[{"phone": "(920) 555-1234", "type": "mobile"}],
    emails=[{"email": "TEAM@ACME.COM", "type": "work"}],
)

policy = normalize_policy_payload(
    policy_number="POL001",
    contacts=[contact],
    effective_date=dt.date(2026, 1, 2),
    policy_type_id="pt-123",
)

quote = normalize_quote_payload(
    number="Q-001",
    policy_type_id="pt-123",
    agency_id="agency-1",
    named_insureds=["ni-1"],
    risks=["risk-1"],
)

print(contact)
print(policy)
print(quote)
```

## CLI usage

Normalize JSON from the command line when you do not want to import Python modules:

```powershell
britecore-normalize-json --kind contact --input .\contact.raw.json --output .\contact.normalized.json --pretty
python .\scripts\normalize_json.py --kind quote --input .\quote.raw.json --pretty
```

`--kind` must be one of: `contact`, `policy`, `quote`.

Inspect expected keys before writing input files:

```powershell
britecore-normalize-json --schema
britecore-normalize-json --schema --kind policy --pretty
```

## When to use this vs API wrappers

- Use `data_layer` for local data cleanup, preflight transformations, and one-off tooling.
- Use API wrappers in `britecore_sdk.api.api_calls` when you need to call BriteCore endpoints.
