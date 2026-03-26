# Contributing Guide

**BriteCore Libraries** - How to contribute code and improvements

---

## Code of Conduct

- Be respectful and inclusive
- Focus on improving the codebase
- Review code objectively
- Test thoroughly before submitting

---

## Development Setup

### Local Environment

```bash
# Clone repository
git clone <repository-url>
cd britecore_libraries

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -m pytest tests/unit/test_maps.py -v
```

### Configuration

Set environment variables for local testing:

```bash
export target_site=your_site
export system=system_variant
```

---

## Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/description
```

### 2. Make Changes

Follow the coding patterns described in [AGENTS.md](AGENTS.md):

- **New Endpoint:** See "API module pattern" section
- **New Validator:** See `validators/` directory examples
- **New Model:** See `models/` directory examples

### 3. Write Tests

```python
# tests/unit/test_my_feature.py
import pytest

@pytest.mark.unit
def test_my_feature():
    """Test description."""
    # Arrange
    # Act
    # Assert
    assert result == expected
```

### 4. Run Tests & Check Coverage

```bash
# Run all tests
python -m pytest tests/ -v

# Check coverage
python -m pytest tests/ --cov=src/britecore_libraries --cov-report=term-missing

# View HTML coverage
python -m pytest tests/ --cov=src/britecore_libraries --cov-report=html
htmlcov/index.html
```

### 5. Commit & Push

```bash
git add .
git commit -m "feat: add my feature"
git push origin feature/description
```

### 6. Create Pull Request

- Describe the change
- Reference any related issues
- Ensure CI/CD passes
- Request review

---

## Coding Standards

### Python Style

Follow PEP 8 with these additions:

```python
# Good: Type hints and docstrings
def my_function(param: str, optional: Optional[int] = None) -> dict:
    """
    Brief description.
    
    Parameters:
        param: Description
        optional: Description
    
    Returns:
        Description of return value
    """
    pass

# Good: Clear variable names
contact_data = process_contact(contact)

# Avoid: Cryptic abbreviations
cd = process_contact(c)
```

### Import Order

```python
# 1. Standard library
import os
from typing import Optional
from datetime import datetime

# 2. Third-party
import pytest
from dynaconf import Dynaconf

# 3. Local
from britecore_libraries.models import BritecoreContact
from britecore_libraries.api.api_calls import get_api_client
```

### Naming Conventions

```python
# Classes: PascalCase
class BritecoreContact:
    pass

# Functions/methods: snake_case
def process_contact(contact):
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 5

# Private: _leading_underscore
def _internal_helper():
    pass

# Special methods: __dunder__
def __init__(self):
    pass
```

---

## Adding API Endpoints

### Step 1: Create Function

```python
# In api/api_calls/v2/my_module.py
from typing import Optional, Unpack, Any
from britecore_libraries.api.api_calls import (
    API_CLIENT,
    RequestParameters
)

def my_endpoint(
    required_param: str,
    optional_param: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Endpoint description from britecore_api.json.
    
    Parameters:
        required_param: Description
        optional_param: Description
        **kwargs: request_timeout, request_retries, etc.
    
    Returns:
        Dictionary with response data
    """
    # Build request
    payload = {
        "required_param": required_param,
    }
    if optional_param:
        payload["optional_param"] = optional_param
    
    # Make request
    response = API_CLIENT.do_request(
        path="/api/v2/my_module/my_endpoint",
        json=payload,
        **kwargs
    )
    
    # Process and return
    return API_CLIENT.process_result(response)
```

### Step 2: Export Function

```python
# In api/api_calls/v2/__init__.py
from . import my_module

__all__ = [
    # ... existing exports ...
    "my_module",
]
```

### Step 3: Add Tests

```python
# In tests/integration/test_endpoints.py
@pytest.mark.integration
def test_my_endpoint(mock_http_response):
    """Test my_endpoint."""
    with patch("britecore_libraries.api.api_calls.v2.my_module.API_CLIENT") as mock:
        mock.do_request.return_value = mock_http_response
        mock.process_result.return_value = {"id": "test_123"}
        
        from britecore_libraries.api.api_calls.v2.my_module import my_endpoint
        
        result = my_endpoint("required_value")
        
        assert result["id"] == "test_123"
        mock.do_request.assert_called_once()
```

---

## Adding Validators

### Step 1: Create Validator Class

```python
# In validators/my_validator.py
from britecore_libraries.exceptions import BritecoreError

class MyValidator:
    """Validate and normalize my data."""
    
    def __init__(self, data):
        self.data = data
    
    def process(self):
        """Process and validate data."""
        validated = []
        for item in self.data:
            # Validate
            if not self._is_valid(item):
                raise BritecoreError.InvalidData(f"Invalid: {item}")
            # Normalize
            normalized = self._normalize(item)
            validated.append(normalized)
        return validated
    
    def _is_valid(self, item):
        # Your validation logic
        return True
    
    def _normalize(self, item):
        # Your normalization logic
        return item
```

### Step 2: Export Validator

```python
# In validators/__init__.py
from .my_validator import MyValidator

__all__ = [
    # ... existing ...
    "MyValidator",
]
```

### Step 3: Add Tests

```python
# In tests/unit/test_validators.py
@pytest.mark.unit
def test_my_validator_valid():
    """Test validator with valid data."""
    data = [{"field": "value"}]
    result = MyValidator(data).process()
    assert result is not None

@pytest.mark.unit
def test_my_validator_invalid():
    """Test validator with invalid data."""
    data = [{"field": ""}]  # Invalid
    with pytest.raises(BritecoreError.InvalidData):
        MyValidator(data).process()
```

---

## Testing Guidelines

### Test Structure

```python
@pytest.mark.unit
def test_feature_happy_path(fixture):
    """Test normal operation."""
    # Arrange
    input_data = ...
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected
```

### Using Fixtures

```python
def test_with_fixture(mock_http_response):
    """Use provided fixture."""
    assert mock_http_response.status == 200
```

### Mocking External Calls

```python
@pytest.mark.unit
def test_with_mock(monkeypatch):
    """Mock external API call."""
    mock_response = {"data": "test"}
    
    def mock_request(*args, **kwargs):
        return mock_response
    
    monkeypatch.setattr(API_CLIENT, "do_request", mock_request)
    
    result = endpoint_function()
    assert result == mock_response
```

---

## Documentation

### Module Docstrings

```python
"""
Module description.

This module provides functions for working with X.

Functions:
    function1: Description
    function2: Description
"""
```

### Function Docstrings

```python
def my_function(param1: str, param2: Optional[int] = None) -> dict:
    """
    Brief one-line description.
    
    Longer description if needed. Explain the purpose and behavior.
    
    Parameters:
        param1: Description of param1
        param2: Description of param2 (optional)
    
    Returns:
        Description of return value
        Format if applicable: {...}
    
    Raises:
        BritecoreError: When something is wrong
    
    Examples:
        >>> result = my_function("test")
        >>> print(result)
        {'key': 'value'}
    """
```

---

## Before Submitting

### Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Coverage maintained: `pytest --cov=src/britecore_libraries`
- [ ] New code has tests
- [ ] Docstrings added/updated
- [ ] No breaking changes
- [ ] Commit messages are clear
- [ ] Documentation updated (README, AGENTS.md, etc.)

### Run Locally

```bash
# Full test suite
python -m pytest tests/ -v --tb=short

# With coverage
python -m pytest tests/ --cov=src/britecore_libraries --cov-report=term-missing

# Specific category
python -m pytest tests/unit -m unit -v
```

---

## Code Review

### What We Look For

1. **Correctness** - Does it work as intended?
2. **Testing** - Are edge cases covered?
3. **Clarity** - Can others understand the code?
4. **Consistency** - Does it follow project patterns?
5. **Documentation** - Is it well-documented?

### Providing Feedback

- Be specific and constructive
- Suggest improvements, not criticism
- Ask questions if unclear
- Acknowledge good work

---

## Common Issues

### Import Errors

**Solution:** Install in editable mode
```bash
pip install -e ".[dev]"
```

### Tests Failing

**Solution:** Check dependencies
```bash
pip install -e ".[dev]"
python -m pytest tests/unit/test_maps.py -v
```

### Coverage Drops

**Solution:** Add tests for new code
```bash
python -m pytest tests/ --cov=src/britecore_libraries --cov-report=html
```

---

## Questions?

- Review [AGENTS.md](AGENTS.md) for architecture
- Check test examples in `tests/`
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Review existing endpoints for patterns

---

Thank you for contributing! 🙏

