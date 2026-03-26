# Getting Started Guide

**BriteCore Libraries** - Setup and first steps

---

## Prerequisites

- Python 3.14+
- pip or uv package manager
- Git (for cloning)
- Text editor or IDE

---

## Installation

### Option 1: Development Install (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd britecore_libraries

# Install with development tools
pip install -e ".[dev]"

# Verify installation
python -c "import britecore_libraries; print(f'Version: {britecore_libraries.__version__}')"
```

### Option 2: Production Install

```bash
pip install -e .
```

### Option 3: From Source

```bash
git clone <repository-url>
cd britecore_libraries
python -m pip install --upgrade pip
pip install -e .
```

---

## Configuration

### Step 1: Set Environment Variables

```bash
# On Windows (PowerShell)
$env:target_site = "your_site"
$env:system = "system_variant"

# On Linux/Mac
export target_site=your_site
export system=system_variant
```

### Step 2: Configure Settings

Create or update configuration files in `src/britecore_libraries/config/`:

**settings.toml:**
```toml
[default]
web_timeout = 5
web_timeout_long = 50
web_retry = 3

[production]
base_url = "https://your-api-endpoint.com"
client_id = ""           # Leave blank for API key auth
client_secret = ""       # Leave blank for API key auth
api_key = "your_api_key"

[staging]
base_url = "https://staging-api-endpoint.com"
client_id = ""
client_secret = ""
api_key = "your_test_api_key"
```

**OR use environment variables:**
```bash
export BRITECORE_BASE_URL="https://your-api-endpoint.com"
export BRITECORE_API_KEY="your_api_key"
```

---

## Verify Installation

### Quick Check

```bash
# Check version
python -c "import britecore_libraries; print(britecore_libraries.__version__)"

# Test import
python -c "from britecore_libraries.models import BritecoreContact; print('✓ Models working')"

# Test API client
python -c "from britecore_libraries.api.api_calls import get_api_client; print('✓ API client ready')"
```

### Run Tests

```bash
# Install dev dependencies (if not already done)
pip install -e ".[dev]"

# Run quick test
python -m pytest tests/unit/test_maps.py -v

# Run full test suite
python -m pytest tests/ -v
```

---

## First Steps

### 1. Working with Domain Models

```python
from britecore_libraries.models import BritecoreContact, BritecorePolicy

# Create a contact
contact = BritecoreContact(
    name="John Doe",
    address={
        "street": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "zip": "62701",
        "type": "Mailing/Billing"
    },
    phone_number=[{
        "phone": "5551234567",
        "type": "Home"
    }],
    email=[{
        "email": "john@example.com",
        "type": "Home"
    }]
)

# Process and validate
processed = contact.process_contact()
print(processed)
```

### 2. Validating Data

```python
from britecore_libraries.validators import EmailValidator, PhoneValidator

# Validate email
emails = [{"email": "test@example.com", "type": "Home"}]
validated_emails = EmailValidator(emails).process()

# Validate phone
phones = [{"phone": "5551234567", "type": "Home"}]
validated_phones = PhoneValidator(phones).process()
```

### 3. Using the API Client

```python
from britecore_libraries.api.api_calls.v2 import policies, quotes

# Get a policy
policy = policies.retrieve_policy(policy_number="POL001")
print(f"Policy: {policy['id']}")

# Get a quote
quote = quotes.get_quote("quote_123")
print(f"Quote: {quote['number']}")
```

### 4. Working with API Client Directly

```python
from britecore_libraries.api.api_calls import get_api_client

# Get client (lazy initialization)
client = get_api_client()

# Make API request
response = client.do_request(
    path="/api/v2/policies/retrieve_policy",
    json={"policy_number": "POL001"}
)

# Process response
data = client.process_result(response)
print(data)
```

---

## Running Tests

### Basic Test Run

```bash
# Run all tests
python -m pytest tests/ -v

# Run faster (without coverage)
python -m pytest tests/ -v --no-cov

# Run specific test file
python -m pytest tests/unit/test_validators.py -v

# Run with coverage report
python -m pytest tests/ --cov=src/britecore_libraries --cov-report=html
```

### View Coverage

```bash
# After running tests with coverage
open htmlcov/index.html        # On Mac
xdg-open htmlcov/index.html    # On Linux
start htmlcov/index.html       # On Windows
```

---

## Common Tasks

### Add a New Validator

```python
# In src/britecore_libraries/validators/custom_validator.py
from britecore_libraries.validators import EmailValidator

class CustomValidator:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        # Validate and normalize data
        return self.data

# Export in src/britecore_libraries/validators/__init__.py
from .custom_validator import CustomValidator

__all__ = [..., "CustomValidator"]
```

### Call a New API Endpoint

```python
# In api/api_calls/v2/my_module.py
from britecore_libraries.api.api_calls import API_CLIENT

def my_endpoint(param1: str, **kwargs):
    """My endpoint description."""
    response = API_CLIENT.do_request(
        path="/api/v2/my_module/my_endpoint",
        json={"param1": param1},
        **kwargs
    )
    return API_CLIENT.process_result(response)

# Export in api/api_calls/v2/__init__.py
from . import my_module
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'britecore_libraries'"

**Solution:**
```bash
pip install -e .
```

### "No target site assigned"

**Solution:**
```bash
export target_site=your_site
```

### "Configuration validation failed"

**Solution:** Ensure `settings.toml` has required keys:
- `base_url`
- `api_key` OR (`client_id` + `client_secret`)
- `web_timeout`
- `web_retry`

### Tests failing with import errors

**Solution:**
```bash
pip install -e ".[dev]"
python -m pytest tests/ -v --tb=short
```

---

## Next Steps

1. **Read the Architecture Guide:** [AGENTS.md](AGENTS.md)
2. **Review API Coverage:** [API_COVERAGE_ANALYSIS.md](API_COVERAGE_ANALYSIS.md)
3. **Explore Tests:** [tests/README.md](tests/README.md)
4. **Start Developing:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Getting Help

- Check [README.md](README.md) for overview
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review [AGENTS.md](AGENTS.md) for architecture details
- Look at test examples in `tests/` directory

---

**Ready to start!** 🚀

