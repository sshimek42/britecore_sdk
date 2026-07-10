# API Reference

*Last updated: July 10, 2026*

This page is the generated symbol-level API reference. For narrative usage
guidance, examples, and broader endpoint notes, see the repository-level
`API.md` guide.

## Notable v1.1 additions

- `BritecoreAPIClient` — context manager (`__enter__`/`__exit__`), `__repr__`, `init_client()` returns `Self`
- `do_request(..., dry_run=True)` — synthetic dry-run response with redacted headers by default
- `init_api_client(client_dry_run=True)` / `init_client(client_dry_run=True)` — client-level dry-run defaults
- `init_async_api_client(client_dry_run=True)` / `AsyncBritecoreAPIClient.ado_request(..., dry_run=True)` — async dry-run parity with cache bypass
- `reset_api_client()` — clears module-level client (test isolation)
- `HealthcheckResult.__bool__` — truthiness from `.ok`
- Flat exception aliases in `britecore_sdk.exceptions` and top-level package

## Package exports

```{automodule} britecore_sdk
:members:
:undoc-members:
:show-inheritance:
```

## API clients

```{automodule} britecore_sdk.api.britecore_api_client
:members:
:undoc-members:
:show-inheritance:
```

```{automodule} britecore_sdk.api.britecore_async_api_client
:members:
:undoc-members:
:show-inheritance:
```

```{automodule} britecore_sdk.api.request_cache
:members:
:undoc-members:
:show-inheritance:
```

## Exceptions

```{automodule} britecore_sdk.exceptions
:members:
:undoc-members:
:show-inheritance:
```

## Utilities

```{automodule} britecore_sdk.utils.healthcheck
:members:
:undoc-members:
:show-inheritance:
```

## V2 Package Exports

```{automodule} britecore_sdk.api.api_calls.v2
:members:
:undoc-members:
:show-inheritance:
```

## Workflow Package Exports

```{automodule} britecore_sdk.api.workflows
:members:
:undoc-members:
:show-inheritance:
```

## V2 Synchronous Endpoint Modules

The sections below are representative core modules. For the complete current
module inventory, see `API.md` and `src/britecore_sdk/api/api_calls/v2/`.

### Accounting

```{automodule} britecore_sdk.api.api_calls.v2.accounting
:members:
:undoc-members:
:show-inheritance:
```

### Billing

```{automodule} britecore_sdk.api.api_calls.v2.billing
:members:
:undoc-members:
:show-inheritance:
```

### Quotes

```{automodule} britecore_sdk.api.api_calls.v2.quotes
:members:
:undoc-members:
:show-inheritance:
```

### Contacts

```{automodule} britecore_sdk.api.api_calls.v2.contacts
:members:
:undoc-members:
:show-inheritance:
```

### Policies

```{automodule} britecore_sdk.api.api_calls.v2.policies
:members:
:undoc-members:
:show-inheritance:
```

### Claims

```{automodule} britecore_sdk.api.api_calls.v2.claims
:members:
:undoc-members:
:show-inheritance:
```

### Commissions

```{automodule} britecore_sdk.api.api_calls.v2.commissions
:members:
:undoc-members:
:show-inheritance:
```

### Deliverables

```{automodule} britecore_sdk.api.api_calls.v2.deliverables
:members:
:undoc-members:
:show-inheritance:
```

### Inspections

```{automodule} britecore_sdk.api.api_calls.v2.inspections
:members:
:undoc-members:
:show-inheritance:
```

### Insured

```{automodule} britecore_sdk.api.api_calls.v2.insured
:members:
:undoc-members:
:show-inheritance:
```

### Lines

```{automodule} britecore_sdk.api.api_calls.v2.lines
:members:
:undoc-members:
:show-inheritance:
```

### Notes

```{automodule} britecore_sdk.api.api_calls.v2.notes
:members:
:undoc-members:
:show-inheritance:
```

### Payments

```{automodule} britecore_sdk.api.api_calls.v2.payments
:members:
:undoc-members:
:show-inheritance:
```

### Reports

```{automodule} britecore_sdk.api.api_calls.v2.reports
:members:
:undoc-members:
:show-inheritance:
```

### Utils

```{automodule} britecore_sdk.api.api_calls.v2.utils
:members:
:undoc-members:
:show-inheritance:
```

### Additional v2 modules (July 2026)

`agentcy`, `auth`, `authority_limits`, `background_jobs`,
`claim_adjuster_assignment_configs`, `claim_catastrophes`, `claim_changes`,
`claim_contacts`, `claim_dates`, `claim_estimations`, `claim_exposures`,
`claim_injuries`, `claim_properties`, `claim_vehicles`, `configurations`,
`coverages`, `custom_data`, `disputes`, `drivers`, `files`, `geometries`,
`geometry`, `imports`, `ingestion_job`, `integrations`, `jobrunner`,
`named_insureds`, `permissions`, `policy_types`,
`premium_finance_companies`, `prior_policies`, `quick_code_values`,
`quick_codes`, `quick_quote_templates`, `quote`, `related_policies`,
`rules`, `statement_of_value`, `subjectivities`, `suspensions`, `tasks`,
`term_credit_scores`, `user_groups`, `vehicles`, `violations`,
`watercrafts`

## V2 Asynchronous Endpoint Modules

### Async Quotes

```{automodule} britecore_sdk.api.api_calls.v2.async_quotes
:members:
:undoc-members:
:show-inheritance:
```

### Async Contacts

```{automodule} britecore_sdk.api.api_calls.v2.async_contacts
:members:
:undoc-members:
:show-inheritance:
```

### Async Policies

```{automodule} britecore_sdk.api.api_calls.v2.async_policies
:members:
:undoc-members:
:show-inheritance:
```
