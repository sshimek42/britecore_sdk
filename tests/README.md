# Test Suite for BriteCore Libraries

This directory contains comprehensive tests for the britecore_libraries package.

## Structure

```
tests/
├── conftest.py                    # Shared pytest fixtures
├── unit/                          # Unit tests
│   ├── test_config.py             # Configuration module tests
│   ├── test_api_client.py         # API client and lazy init tests
│   ├── test_oauth_token_manager.py # OAuth token tests
│   ├── test_maps.py               # Regex map tests
│   ├── test_validators.py         # Validator tests
│   ├── test_models.py             # Domain model tests
│   └── test_exceptions.py         # Exception and deprecation tests
└── integration/                   # Integration tests
    └── test_endpoints.py          # API endpoint wrapper tests
```

## Running Tests

### All Tests
```powershell
pytest tests/
```

### Unit Tests Only
```powershell
pytest tests/unit -m unit
```

### Integration Tests Only
```powershell
pytest tests/integration -m integration
```

### With Coverage Report
```powershell
pytest tests/ --cov=src/britecore_libraries --cov-report=html
```

### Verbose Output
```powershell
pytest tests/ -v
```

### Specific Test File
```powershell
pytest tests/unit/test_api_client.py -v
```

### Specific Test Class
```powershell
pytest tests/unit/test_api_client.py::TestLazyAPIClientInitialization -v
```

### Specific Test
```powershell
pytest tests/unit/test_api_client.py::TestLazyAPIClientInitialization::test_api_calls_module_imports_without_init -v
```

## Test Coverage

The test suite targets >80% code coverage for core modules:

- **Configuration**: Dynaconf loading, validators, fallbacks
- **API Client**: Lazy initialization, auth modes, request/response handling
- **OAuth Token Manager**: Token refresh, expiration, error handling
- **Validators**: Email, phone, address, name normalization
- **Models**: Contact, Policy, Quote data structures
- **Endpoints**: Quote, Policy, Contact API wrappers
- **Exceptions**: All custom exception types
- **Deprecation**: Legacy class compatibility

## Fixtures

Common fixtures available in `conftest.py`:

- `mock_settings` - Mock Dynaconf settings with API key auth
- `mock_settings_oauth` - Mock Dynaconf settings with OAuth
- `mock_http_response` - Successful HTTP response (200 OK)
- `mock_http_response_error` - Error HTTP response (400)
- `mock_oauth_response` - OAuth token response
- `mock_oauth_response_error` - OAuth error response
- `tmp_config_file` - Temporary TOML config file
- `env_api_key` - Environment with API key setup
- `env_oauth` - Environment with OAuth setup
- `env_no_system` - Environment without system variable

## Installing Test Dependencies

```powershell
pip install -e ".[dev]"
```

## CI Integration

Tests are automatically run in CI/CD pipelines. Coverage reports are generated and can be viewed in `htmlcov/index.html`.

## Markers

Tests can be marked for specific test runs:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may use mocks for external services)
- `@pytest.mark.slow` - Slow tests (skipped by default)

Run slow tests:
```powershell
pytest tests/ -m slow
```

Skip slow tests:
```powershell
pytest tests/ -m "not slow"
```

## Notes

- Tests mock external dependencies (HTTP, ODBC, OAuth endpoints)
- No real API calls or database connections required
- All tests run in isolation without state sharing
- Temporary files and directories are cleaned up automatically

