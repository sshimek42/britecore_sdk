# BriteCore SDK Examples

This directory contains practical examples of BriteCore SDK usage patterns, from basic to advanced.

## Quick Start Examples

### 1. **complete_workflow.py** - Start Here!
Complete end-to-end example showing:
- Configuration setup
- Client initialization
- Creating and managing policies
- Error handling
- Cleanup

Perfect for understanding the full flow before diving into specific patterns.

```bash
python examples/complete_workflow.py
```

### 2. **configuration_examples.py** - Setup & Config
Examples of different configuration approaches:
- Environment variables
- File-based configuration
- Explicit credential passing
- Multi-site setup
- Dry-run mode

```bash
python examples/configuration_examples.py
```

### 3. **data_layer_quickstart.py** - One-Off Data Shaping (No API Calls)
Use lightweight normalization helpers without initializing API clients:

- Name, phone, and email normalization
- Contact payload shaping for downstream tools

```bash
python examples/data_layer_quickstart.py
```

Command-line JSON normalization alternative:

```bash
britecore-normalize-json --kind contact --input ./contact.raw.json --output ./contact.normalized.json --pretty
```

---

## Advanced Examples

### 4. **advanced_error_handling.py** - Robust Error Handling
Comprehensive exception handling patterns:
- Retry logic with exponential backoff
- Fallback strategies
- Error collection and reporting
- Rate limit recovery

### 5. **async_operations.py** - Async & Concurrent Processing
Non-blocking API calls and batch operations:
- Concurrent policy fetching with concurrency control
- Batch quote creation with rate limiting
- Async error handling
- Orchestrating complex async workflows

```bash
python examples/async_operations.py
```

---

## Domain-Specific Examples

### 6. **basic_api_usage.py** - Core API Operations
Fundamental API operations:
- Retrieving policies and quotes
- Creating contacts and policies
- Error handling basics

Run with:
```bash
python examples/basic_api_usage.py --live-policy-number "POL001"
```

### 7. **batch_quote_creation.py** - Batch Operations
Creating multiple quotes efficiently:
- Parallel quote creation
- Progress tracking
- Error collection
- Performance optimization

### 8. **multi_tenancy_example.py** - Multi-Site Operations
Working with multiple BriteCore environments:
- Switching between sites
- Site isolation in scripts
- Cross-environment workflows

Set credentials via environment variables:
```bash
export PROD_BASE_URL=https://api.prod.example.com
export PROD_API_KEY=your-prod-key
python examples/multi_tenancy_example.py
```

### 9. **rate_limiting_example.py** - Rate Limit Handling
Graceful rate limit management:
- Detecting rate limits
- Exponential backoff
- Request queuing
- Adaptive throttling

### 10. **staged_workflow_creation.py** - Complex Workflows
Multi-step business processes:
- Creating policies with relationships
- Sequential operations with error recovery
- Data transformation pipelines

### 11. **stitched_line_extract.py** - Complex Data
Working with complex nested structures:
- Extracting line items
- Data validation
- Format transformation

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -e ".[dev]"
```

### 2. Configure Credentials
Create `~/.britecore/.secrets.toml`:
```toml
[production]
base_url = "https://api.britecore.example.com"
api_key = "your_api_key"
```

Create `~/.britecore/settings.toml`:
```toml
[default]
target_site = "production"
```

### 3. Verify Setup
```bash
britecore-check-config
britecore-healthcheck
```

---

## Running Examples

### Basic Example (No API calls)
```bash
python examples/complete_workflow.py
# Just shows the flow without connecting to API
```

### With Live API Calls
Set API credentials first, then:
```bash
python examples/basic_api_usage.py --live-policy-number "POL001"
```

### Async Example
```bash
python examples/async_operations.py
```

### Error Handling Example
```bash
python examples/advanced_error_handling.py
```

### Dry-Run Mode (Test without sending)
```bash
python -c "
from britecore_sdk.api.api_calls import init_api_client
init_api_client('production', client_dry_run=True)
exec(open('examples/basic_api_usage.py').read())
"
```

---

## Pattern Reference

| Pattern | Example | Use When |
|---------|---------|----------|
| Policy lookup | `complete_workflow.py` | Retrieving single policies |
| Batch operations | `batch_quote_creation.py` | Creating multiple entities |
| Error recovery | `advanced_error_handling.py` | Handling transient failures |
| Async processing | `async_operations.py` | High-throughput operations |
| Rate limiting | `rate_limiting_example.py` | Hitting rate limits |
| Multi-site | `multi_tenancy_example.py` | Multi-environment setup |
| Complex workflows | `staged_workflow_creation.py` | Multi-step processes |
| Configuration | `configuration_examples.py` | Setting up SDK |
| Script-only data shaping | `data_layer_quickstart.py` | One-off normalization without API calls |

---

## Common Tasks

### Creating a Policy
See: `complete_workflow.py` or `batch_quote_creation.py`

### Querying Multiple Policies Concurrently
See: `async_operations.py`

### Handling Rate Limits
See: `rate_limiting_example.py` or `advanced_error_handling.py`

### Using Different Environments
See: `multi_tenancy_example.py`

### Testing Without Real API Calls
See: `configuration_examples.py` (dry-run example)

---

## Troubleshooting

### "Authentication failed"
```bash
# Check configuration
britecore-check-config

# Verify credentials
echo $BRITECORE_SDK_API_KEY
```

See: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

### "Rate limit exceeded"
See: `rate_limiting_example.py` for backoff logic

### "Connection refused"
- Verify base_url is correct
- Check network connectivity
- See: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

---

## Documentation Links

- **Getting Started:** [GETTING_STARTED.md](../GETTING_STARTED.md)
- **API Reference:** [API.md](../API.md)
- **Common Patterns:** [docs/COMMON_PATTERNS.md](../docs/COMMON_PATTERNS.md)
- **Rate Limiting:** [docs/RATE_LIMITING.md](../docs/RATE_LIMITING.md)
- **Batch Operations:** [docs/BATCH_QUOTE_CREATION.md](../docs/BATCH_QUOTE_CREATION.md)
- **Configuration:** [docs/CONFIGURATION.md](../docs/CONFIGURATION.md)
- **Script-only Data Layer:** [docs/SCRIPT_ONLY_DATA_LAYER.md](../docs/SCRIPT_ONLY_DATA_LAYER.md)
- **Multi-Tenancy:** [docs/MULTI_TENANCY.md](../docs/MULTI_TENANCY.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **Migration v1→v2:** [docs/MIGRATION_v1_to_v2.md](../docs/MIGRATION_v1_to_v2.md)
