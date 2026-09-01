# Data Layer

Use `britecore_sdk.data_layer` when you only need models and normalization for small scripts.

## Includes

- Domain models: `BritecoreContact`, `BritecorePolicy`, `BritecoreQuote`
- Validators: `AddressValidator`, `EmailValidator`, `NameValidator`, `PhoneValidator`
- Convenience helpers:
  - `normalize_name(...)`
  - `normalize_address(...)`
  - `normalize_phones(...)`
  - `normalize_emails(...)`
  - `normalize_contact_payload(...)`
  - `normalize_policy_payload(...)`
  - `normalize_quote_payload(...)`

## Quick Example

```python
from britecore_sdk.data_layer import normalize_contact_payload

payload = normalize_contact_payload(
    name="acme llc",
    address={
        "address_line1": "123 main st",
        "address_city": "madison",
        "address_state": "wi",
        "address_zip": "53703",
    },
    phone_numbers=[{"phone": "(920) 555-1234", "type": "mobile"}],
    emails=[{"email": "TEAM@ACME.COM", "type": "work"}],
)

print(payload["name"])     # acme LLC
print(payload["phones"])   # [{'phone': '1-920-555-1234', 'type': 'Cell'}]
```
