# Deployment & CI/CD Guide

*Last updated: September 2, 2026*
*Document type: Integration guide*

This guide covers deploying `britecore_sdk` in containerized environments, CI/CD pipelines, serverless functions, and production services.

---

## Overview

The SDK is optimized for deployment in:

- **Containers** (Docker, Kubernetes)
- **CI/CD pipelines** (GitHub Actions, GitLab CI, Jenkins)
- **Serverless** (AWS Lambda, Google Cloud Functions, Azure Functions)
- **Long-running services** (Django, FastAPI, etc.)

Key design decisions enabling this:

- **No file I/O required** (inline credentials supported)
- **Lazy initialization** (config loads on first request)
- **Explicit-client friendly** (module-level client fallback still exists for compatibility)
- **Thread-safe** (urllib3 connection pooling)
- **Lightweight** (minimal dependencies)

---

## Docker Deployment

### Basic Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install SDK
COPY requirements.txt .
RUN pip install --no-cache-dir britecore_sdk

# Copy your application
COPY . .

# Set environment for SDK (no config files needed)
ENV BRITECORE_SDK_BASE_URL=https://api.example.com
ENV BRITECORE_SDK_API_KEY=${BRITECORE_SDK_API_KEY}
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["python", "app.py"]
```

**requirements.txt:**

```text
britecore_sdk>=2.0.0
flask>=3.0.0
# ... other deps
```

### Using Docker Compose

```yaml
version: "3.9"

services:
  app:
    build: .
    environment:
      # API credentials from .env (not committed to git)
      BRITECORE_SDK_BASE_URL: ${BRITECORE_BASE_URL}
      BRITECORE_SDK_API_KEY: ${BRITECORE_API_KEY}
      FLASK_ENV: production
      PYTHONUNBUFFERED: "1"
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: separate background worker
  worker:
    build: .
    environment:
      BRITECORE_SDK_BASE_URL: ${BRITECORE_BASE_URL}
      BRITECORE_SDK_API_KEY: ${BRITECORE_API_KEY}
      WORKER_MODE: "true"
    depends_on:
      - app
```

### Health Check Endpoint

Add a simple health check to your app to verify SDK readiness:

```python
from flask import Flask, jsonify
from britecore_sdk.api.api_calls import get_api_client

app = Flask(__name__)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        # Test SDK initialization
        client = get_api_client()
        return jsonify({
            "status": "ok",
            "sdk": "initialized",
            "auth_mode": client.auth_mode,
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 503
```

---

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: britecore-api-client
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: britecore-client
  template:
    metadata:
      labels:
        app: britecore-client
    spec:
      containers:
      - name: app
        image: myrepo/britecore-client:latest
        ports:
        - containerPort: 8000
        env:
        # Inject API credentials from Secret
        - name: BRITECORE_SDK_BASE_URL
          valueFrom:
            secretKeyRef:
              name: britecore-creds
              key: base_url
        - name: BRITECORE_SDK_API_KEY
          valueFrom:
            secretKeyRef:
              name: britecore-creds
              key: api_key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Store Credentials in a Secret

**Windows (PowerShell):**

```powershell
kubectl create secret generic britecore-creds `
  --from-literal=base_url=https://api.example.com `
  --from-literal=api_key=<YOUR_API_KEY>
```

**Linux/macOS (bash):**

```bash
kubectl create secret generic britecore-creds \
  --from-literal=base_url=https://api.example.com \
  --from-literal=api_key=<YOUR_API_KEY>
```

---

## GitHub Actions CI/CD

### Environment Setup

Store sensitive credentials in GitHub Secrets:

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add:
   - `BRITECORE_API_KEY`: Your API key
   - `BRITECORE_BASE_URL`: API endpoint URL

### Test Workflow

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    - name: Lint
      run: ruff check .

    - name: Type check
      run: mypy src/

    - name: Unit tests
      run: pytest tests/unit -v --cov=src --cov-report=term-missing

    - name: Integration tests (with credentials)
      env:
        BRITECORE_SDK_BASE_URL: ${{ secrets.BRITECORE_BASE_URL }}
        BRITECORE_SDK_API_KEY: ${{ secrets.BRITECORE_API_KEY }}
      run: pytest tests/integration -v

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

### Validate Configuration Before Deploy

```yaml
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install SDK
      run: pip install britecore_sdk

    - name: Validate SDK configuration
      env:
        BRITECORE_SDK_BASE_URL: ${{ secrets.BRITECORE_BASE_URL }}
        BRITECORE_SDK_API_KEY: ${{ secrets.BRITECORE_API_KEY }}
      run: |
        python -m britecore_sdk.utils.check_site_configs --json
```

---

## AWS Lambda Deployment

### Lambda Function Handler

```python
"""
Lambda function using britecore_sdk.
"""

import json
import logging
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

logger = logging.getLogger(__name__)
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)


def lambda_handler(event, context):
    """
    Retrieve a policy from BriteCore API via Lambda.

    Event format:
    {
        "policy_number": "POL001"
    }
    """
    try:
        # Initialize client with inline credentials (from env vars)
        import os
        client = init_api_client(
            "lambda",
            base_url=os.environ["BRITECORE_BASE_URL"],
            api_key=os.environ["BRITECORE_API_KEY"],
        )

        # Call API
        policy_number = event.get("policy_number")
        result = policies.retrieve_policy(policy_number=policy_number)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "policy": result["data"],
                "request_id": context.request_id
            })
        }

    except Exception as e:
        logger.exception(f"Error retrieving policy: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
```

### Lambda Configuration

**Environment variables (set in AWS console or SAM template):**

```yaml
Environment:
  Variables:
    BRITECORE_BASE_URL: !Sub "https://api.example.com"
    BRITECORE_API_KEY: !Sub "{{resolve:secretsmanager:britecore-api-key:SecretString:api_key}}"
```

**SAM template:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  PolicyLookupFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.lambda_handler
      Runtime: python3.11
      CodeUri: ./
      Timeout: 30
      MemorySize: 512
      Environment:
        Variables:
          BRITECORE_BASE_URL: !Sub "https://api.example.com"
          BRITECORE_API_KEY: !Sub "{{resolve:secretsmanager:britecore-api-key}}"
```

### Deploy to Lambda

**Windows (PowerShell):**

```powershell
# Package function
Compress-Archive -Path * -DestinationPath package.zip -Force

# Update function
aws lambda update-function-code `
  --function-name policy-lookup `
  --zip-file fileb://package.zip

# Or use SAM
sam deploy --guided
```

**Linux/macOS (bash):**

```bash
# Package function
zip -r package.zip . -x "*.git*" __pycache__ "*.pyc"

# Update function
aws lambda update-function-code \
  --function-name policy-lookup \
  --zip-file fileb://package.zip

# Or use SAM
sam deploy --guided
```

---

## Google Cloud Functions Deployment

### Cloud Function Code

```python
"""
Google Cloud Function using britecore_sdk.
"""

import functions_framework
import logging
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)


@functions_framework.http
def get_policy(request):
    """HTTP Cloud Function."""
    import os
    from flask import jsonify

    try:
        policy_number = request.args.get("policy_number")
        if not policy_number:
            return jsonify({"error": "Missing policy_number"}), 400

        # Initialize with inline credentials
        client = init_api_client(
            "gcf",
            base_url=os.environ["BRITECORE_BASE_URL"],
            api_key=os.environ["BRITECORE_API_KEY"],
        )

        result = policies.retrieve_policy(policy_number=policy_number)
        return jsonify(result["data"])

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**Deploy:**

**Windows (PowerShell):**

```powershell
$secretValue = (gcloud secrets versions access latest --secret=britecore-api-key)
gcloud functions deploy get_policy `
  --runtime python311 `
  --trigger-http `
  --allow-unauthenticated `
  --set-env-vars BRITECORE_BASE_URL=https://api.example.com `
  --set-env-vars BRITECORE_API_KEY=$secretValue
```

**Linux/macOS (bash):**

```bash
gcloud functions deploy get_policy \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars BRITECORE_BASE_URL=https://api.example.com \
  --set-env-vars BRITECORE_API_KEY=$(gcloud secrets versions access latest --secret=britecore-api-key)
```

---

## GitLab CI/CD

### .gitlab-ci.yml

```yaml
stages:
  - test
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

test:
  stage: test
  image: python:3.11
  before_script:
    - pip install -e ".[dev]"
  script:
    - ruff check .
    - mypy src/
    - pytest tests/unit -v --cov=src
  coverage: '/TOTAL.*\s+(\d+%)$/'

integration_test:
  stage: test
  image: python:3.11
  before_script:
    - pip install britecore_sdk
  script:
    - python -m britecore_sdk.utils.check_site_configs --json
  only:
    - develop
    - main
  environment:
    name: integration
  variables:
    BRITECORE_SDK_BASE_URL: $BRITECORE_API_URL
    BRITECORE_SDK_API_KEY: $BRITECORE_API_KEY

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - echo "Deploying to production..."
    - # Your deployment commands here
  only:
    - main
  environment:
    name: production
```

---

## Production Best Practices

### 1. Use Explicit Credentials (No Config Files)

```python
# ✅ Good: Inline credentials from env vars
import os
client = init_api_client(
    base_url=os.environ["BRITECORE_BASE_URL"],
    api_key=os.environ["BRITECORE_API_KEY"]
)

# ❌ Avoid: Config file lookup in containerized env
client = get_api_client()  # Looks for settings.toml
```

### 2. Set Timeouts for Long-Running Requests

```python
from britecore_sdk.api.api_calls.v2 import policies

# Increase timeout for long operations
result = policies.retrieve_policy(
    policy_number="POL001",
    request_timeout=30  # 30 seconds instead of default 5
)
```

### 3. Configure Logging for Production

```python
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(timestamp)s %(level)s %(name)s %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        }
    },
    'loggers': {
        'britecore_sdk': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING)
```

### 4. Monitor Request Latency

```python
import time
from britecore_sdk.api.api_calls.v2 import policies

start = time.time()
result = policies.retrieve_policy(policy_number="POL001")
latency_ms = (time.time() - start) * 1000

# Send to monitoring system (DataDog, Prometheus, etc.)
statsd.timing("britecore.policy_lookup", latency_ms)
```

### 5. Handle Rate Limits Gracefully

The SDK retries automatically. For fine-grained control:

```python
from britecore_sdk.exceptions import RateLimitError
from britecore_sdk.api.api_calls.v2 import policies

try:
    result = policies.retrieve_policy(policy_number="POL001")
except RateLimitError as e:
    logger.warning(f"Rate limited: {e}. Retrying later...")
    # Implement exponential backoff if needed
    time.sleep(5)
    result = policies.retrieve_policy(policy_number="POL001")
```

### 6. Use Health Checks for Orchestration

```python
@app.get("/ready")
def readiness():
    """Readiness check — can accept requests?"""
    try:
        client = get_api_client()
        # If initialization succeeds, the client is ready for requests.
        return {"ready": True, "client": repr(client)}, 200
    except Exception as e:
        return {"ready": False, "error": str(e)}, 503
```

---

## Environment Variable Reference

|Variable|Purpose|Example|
|--------|-------|-------|
|`BRITECORE_SDK_BASE_URL`|API endpoint URL|`https://api.example.com`|
|`BRITECORE_SDK_API_KEY`|API authentication key|`sk_live_...`|
|`BRITECORE_SDK_CLIENT_ID`|OAuth client ID|`client_id_123`|
|`BRITECORE_SDK_CLIENT_SECRET`|OAuth client secret|`secret_456`|
|`BRITECORE_SDK_SETTINGS_FILE`|Optional config file path|`/etc/britecore/config.toml`|

---

## Troubleshooting Deployment

### "No module named britecore_sdk"

**Solution:** Ensure SDK is in requirements.txt and installed:

**Windows (PowerShell):**

```powershell
pip install britecore_sdk
pip freeze | Select-String britecore_sdk
```

**Linux/macOS (bash):**

```bash
pip install britecore_sdk
pip freeze | grep britecore_sdk
```

### "BRITECORE_SDK_BASE_URL not set"

**Solution:** Set environment variables in container/function config:

**Windows (PowerShell):**

```powershell
docker run -e BRITECORE_SDK_BASE_URL=https://api.example.com ...
```

**Linux/macOS (bash):**

```bash
docker run -e BRITECORE_SDK_BASE_URL=https://api.example.com ...
```

### "Connection timeout"

**Solution:** Increase timeout and check network connectivity:

```python
result = policies.retrieve_policy(
    policy_number="POL001",
    request_timeout=30
)
```

### "Rate limit 429 responses"

**Solution:** SDK retries automatically. Configure retry count if needed:

```toml
# settings.toml
[default]
web_retry = 3  # Reduce retries to back off faster
web_timeout = 10  # Increase timeout per request
```

---

## See Also

- [CONFIG_MANAGEMENT.md](../CONFIG_MANAGEMENT.md) — Configuration details
- [docs/MULTI_TENANCY.md](MULTI_TENANCY.md) — Multi-site patterns
- [docs/OBSERVABILITY.md](OBSERVABILITY.md) — Logging and monitoring
