# POST Contract Probing

Use `probe_post_requirements` to run controlled POST probes against sandbox endpoints and collect validation errors that reveal missing required fields.

This utility is intended for manual contract discovery in a sandbox or explicit test environment. It is **not** part of the automated `run_all_checks` flow.

## Safety Rules

- Use sandbox credentials only.
- Keep payloads intentionally invalid to force validation errors before persistence.
- Keep action/trigger endpoints (`risk: "high"`) disabled unless explicitly allowed.

## Probe Plan Format

The plan file is JSON with a `probes` list and optional `default_headers`:

```json
{
  "default_headers": {"X-Probe-Run": "sdk-contract-discovery"},
  "probes": [
    {
      "name": "create_quote_missing_required_fields",
      "path": "/api/v2/quotes/create_quote",
      "payload": {},
      "risk": "medium",
      "notes": "Expected validation error with required fields"
    }
  ]
}
```

A starter plan is available at `examples/post_probe_plan.json`.

## Run

```powershell
python -m britecore_sdk.utils.probe_post_requirements --plan examples/post_probe_plan.json --site your_sandbox_site
```

Generate probes directly from the reference spec for POST endpoints with no documented arguments:

```powershell
python -m britecore_sdk.utils.probe_post_requirements --use-spec-no-args --site your_sandbox_site
```

Broader mode: include POST endpoints whose `application/json` schema exists but has no `properties`/`required` fields:

```powershell
python -m britecore_sdk.utils.probe_post_requirements --use-spec-empty-properties --site your_sandbox_site
```

Preview selected endpoints without sending any requests:

```powershell
python -m britecore_sdk.utils.probe_post_requirements --use-spec-empty-properties --include-path-regex "/api/v2/quotes/" --print-selected-paths --site your_sandbox_site
```

Export the preview list for review in JSON or CSV:

```powershell
python -m britecore_sdk.utils.probe_post_requirements --use-spec-empty-properties --export-selected-paths examples/selected_no_args.json --site your_sandbox_site
python -m britecore_sdk.utils.probe_post_requirements --use-spec-empty-properties --export-selected-paths examples/selected_no_args.csv --site your_sandbox_site
```

`--print-selected-paths` and `--export-selected-paths` are mutually exclusive preview modes.

Narrow to a domain and persist the generated probe plan for review/editing:

```powershell
python -m britecore_sdk.utils.probe_post_requirements --use-spec-no-args --include-path-regex "/api/v2/quotes/" --max-probes 25 --write-generated-plan examples/generated_no_args_probe_plan.json --site your_sandbox_site
```

With explicit credentials (bypass file-based config lookup):

```powershell
python -m britecore_sdk.utils.probe_post_requirements --plan examples/post_probe_plan.json --base-url api.example.com --api-key your_api_key
```

To include `risk: "high"` probes:

```powershell
python -m britecore_sdk.utils.probe_post_requirements --plan examples/post_probe_plan.json --site your_sandbox_site --allow-high-risk
```

## Output

- `post_probe_report.json`: machine-readable results for test/doc updates.
- `post_probe_report.md`: review-friendly summary with inferred required fields.

Use these outputs to update wrapper docstrings and add focused tests for discovered validation behavior.

