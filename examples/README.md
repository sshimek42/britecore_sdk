# Examples

This folder contains runnable usage samples for `britecore_libraries`.

## Available scripts

- `basic_api_usage.py`
  - Runs local-only model/validator examples by default (no network calls).
  - Supports an optional live read call with `--live-policy-number`.

## Run

```powershell
python examples/basic_api_usage.py
```

Show CLI options:

```powershell
python examples/basic_api_usage.py --help
```

Optional live read-only API example (requires configured credentials and `target_site`):

```powershell
python examples/basic_api_usage.py --live-policy-number "POL001"
```

