# Examples

This folder contains runnable usage samples for `britecore_sdk`.

## Available scripts

### `basic_api_usage.py`

Demonstrates basic SDK usage with local-only model/validator examples.

- Runs local model/validator examples by default (no network calls)
- Supports optional live read call with `--live-policy-number`
- Shows domain models, validators, and exception handling patterns

```powershell
python examples/basic_api_usage.py
python examples/basic_api_usage.py --help
python examples/basic_api_usage.py --live-policy-number "POL001"
```

```bash
python examples/basic_api_usage.py
python examples/basic_api_usage.py --help
python examples/basic_api_usage.py --live-policy-number "POL001"
```

### `multi_tenancy_example.py`

Demonstrates multi-site/multi-tenant patterns for managing multiple BriteCore environments.

Includes:
- Sequential processing across multiple sites
- Context manager isolation patterns
- Service registry for long-lived clients
- Bulk operations and error handling

```powershell
python examples/multi_tenancy_example.py
```

```bash
python examples/multi_tenancy_example.py
```

**Set site credentials via environment variables:**

```powershell
$env:PROD_BASE_URL = "https://api.prod.example.com"
$env:PROD_API_KEY = "your-prod-key"
python examples/multi_tenancy_example.py
```

```bash
export PROD_BASE_URL=https://api.prod.example.com
export PROD_API_KEY=your-prod-key
python examples/multi_tenancy_example.py
```

**For more details, see:**
- [docs/MULTI_TENANCY.md](../docs/MULTI_TENANCY.md) — Comprehensive multi-tenancy guide
- [CONFIG_MANAGEMENT.md](../CONFIG_MANAGEMENT.md) — Configuration details
