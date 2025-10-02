# BriteCore Libraries

A comprehensive Python library suite for interacting with the BriteCore insurance platform API and processing insurance-related data. This project provides utilities for API communication, data parsing, validation, and transformation of policies, risks, contacts, and insured entities.

## Overview

The **britecore_libraries** project is designed to simplify integration with BriteCore insurance management systems. It includes:

- **API Client**: OAuth and API key authentication, HTTP request handling with retry logic
- **Data Processing**: Address, phone, email validation and normalization
- **Contact Management**: Policy holder, insured, and contact data processing
- **Browser Automation**: Selenium-based web automation for BriteCore portal interactions
- **Database Integration**: ODBC wrapper for database connectivity

## Features

### API Integration
- ✅ OAuth 2.0 and API key authentication
- ✅ Automatic token refresh and management
- ✅ Configurable retry logic with exponential backoff
- ✅ Timeout handling for long-running requests
- ✅ Comprehensive error handling and logging

### Data Processing & Validation
- ✅ Address parsing and standardization (street, city, state, ZIP)
- ✅ Phone number formatting and validation
- ✅ Email address validation
- ✅ Contact information normalization
- ✅ Policy data transformation

### Automation
- ✅ Selenium-based browser automation
- ✅ Interactive menu-driven line selection
- ✅ Export functionality for lines and policies


## Requirements

- **Python**: 3.13.7
- **Package Manager**: virtualenv
- **Core Dependencies**:
  - `urllib3` - HTTP client with connection pooling
  - `pyinputplus` - Interactive menu handling
  - `selenium` - Browser automation
  - `pyodbc` - Database connectivity
  - `sclogging` - Structured logging
  - `pandas` - Data manipulation (for related data processing)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd britecore_libraries
```

### 2. Create Virtual Environment
```bash
python -m virtualenv .venv
```
#### Windows
```bash
.\.venv\Scripts\activate
```
#### macOS/Linux
```bash
source .venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Package (Development Mode)
```bash
pip install -e .
```
## Configuration
### Settings File
Create or edit : `britecore_libraries/settings.toml`

```toml
[default]
base_url = "your-britecore-instance.britecore.com"
web_timeout = 30
web_timeout_long = 120
web_retry = 3

# OAuth Configuration
client_id = "your_client_id"
client_secret = "your_client_secret"

# OR API Key Configuration (if OAuth not available)
api_key = "your_api_key"

# Database Configuration (optional)
[default.db_conn_options]
autocommit = true

db_conn_string = "DRIVER={SQL Server};SERVER=server;DATABASE=db;UID=user;PWD=pass"
```

# Environment Variables
Alternatively, set the target site via environment variable:
## Windows
```bash
set target_site=your-site-name
```

## macOS/Linux
```bash
export target_site=your-site-name
```

## Usage

```python
### API Client Initialization
from britecore_libraries.britecore_api_client import BritecoreAPIClient

# Initialize API service
api_service = BritecoreAPIClient(target_site="your-site").init_client()
```
### Extract line configuration
```python
# Get all effective dates
dates = api_service.get_all_effective_dates()

# Get states for a specific date
states = api_service.get_all_states(effective_date_id=123)

# Get lines for a date and state
lines = api_service.get_all_lines(
    effective_date_id=123,
    state_id=456
    )

# Export line file
"""Date ID, State ID, Line ID"""
export_data = api_service.get_export_line_file(
    line=(
    123,
    456,
    789),
    line_name="Line Name",
    line_type="Line"
    )
```
### Data Validation
```python
from britecore_libraries.britecore_class import (
    BritecoreAddress,
    BritecorePhone,
    BritecoreEmail,
    BritecoreContact,
    )
```
### Address validation
```python
address = BritecoreAddress("123 Main St, Springfield, IL 62701")
cleaned_address = address.process_address()
```
### Phone validation
```python
phone = BritecorePhone("555-123-4567")
cleaned_phone = phone.process_phone()
```
### Email validation
```python
email = BritecoreEmail("user@example.com")
cleaned_email = email.process_email()
```
### Contact processing
```python
contact = BritecoreContact(
    name="John Doe",
    address="123 Main St",
    phone="555-1234",
    email="john@example.com",
    contact_type="Named Insured"
    )
contact.process_contact()
```
## Policy Management
### Add line item to policy
```python
success = api_service.add_line_item(
    revision_id="policy-revision-uuid",
    line_id="line-item-uuid"
    )
```
### Get policies with specific line item
```python
policies = api_service.get_policies_with_line_item(line_id="line-uuid")

# Retrieve policy IDs
revision_id, property_id = api_service.retrieve_policy_ids(
    policy_number="POL-12345"
    )
```
## Advanced Features
### Custom Timeout Configuration
```python
from urllib3.util import Timeout, Retry

# Custom timeout
custom_timeout = Timeout(connect=10, read=60)

# Custom retry logic
custom_retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)

response = api_service.api_client.do_request(
    path="/api/v2/custom/endpoint",
    json={"param": "value"},
    request_timeout=custom_timeout,
    request_retries=custom_retry
)
```
### Direct API Client Usage
```python
from britecore_libraries.britecore_api_client import BritecoreAPIClient

client = BritecoreAPIClient("your-site").init_client()

# Make custom API request
response = client.do_request(
    path="/api/v2/custom/endpoint",
    json={
        "key": "value"
        },
    method="POST"
    )

# Process response
data = client.process_result(response, logs=True)
```
## Logging
The library uses structured logging via `sclogging`. Configure logging level: 
```python
import logging
import sclogging.sclogging_main as scl

# Set log level
scl.set_log_level(logging.DEBUG)

# Get logger
logger = scl.get_logger(__name__)
logger.info("Custom log message")
```

## Testing
### Run tests (if available)
```bash
python -m pytest tests/ -v
````
### Run specific test file
```bash
python -m pytest tests/test_api_client.py -v
````
## Error Handling
The library provides custom exception types:
```python
from britecore_libraries.britecore_exceptions import BritecoreError

try:
    api_service = BritecoreAPIClient()
except BritecoreError.BritecoreKeyError as e:
    print(f"Authentication error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
## Development
### Code Quality
The project uses DeepSource for static analysis. Configuration is in . `.deepsource.toml`
### Contributing
1. Create a feature branch
2. Make your changes
3. Ensure code follows PEP 8 style guide
4. Add tests for new functionality
5. Submit a pull request

## Troubleshooting
### Authentication Issues
- **API Key Error**: Ensure is set in settings.toml `api_key`
- **OAuth Error**: Verify `client_id` and `client_secret` are correct
- **Invalid URL**: Check format (no trailing slash, no protocol) `base_url`

### Connection Issues
- **Timeout**: Increase or values`web_timeout` or `web_timeout_long`
- **Retry Exhausted**: Check network connectivity and API availability
- **SSL Errors**: Verify SSL certificates are valid

### Data Validation Issues
- **Address Parsing**: Ensure address format matches expected patterns
- **Phone Validation**: Use standard US phone number format
- **Email Validation**: Check for valid email syntax

## Changelog
### Version 1.0.0 (Current)
- Initial release
- API client with OAuth and API key support
- Data validation classes
- Selenium automation utilities
- ODBC database wrapper

**Note**: This library is designed for use with BriteCore insurance management systems. Ensure you have proper API credentials and permissions before use.