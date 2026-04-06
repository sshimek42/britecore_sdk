# Configuration Strategy Analysis: Dynaconf Evaluation

**Date:** April 6, 2026  
**Topic:** Is Dynaconf the best way to handle configuration files?

## Executive Summary

**Yes, Dynaconf is an excellent choice for this project.** However, there are some minor optimization opportunities and a simpler alternative to consider for future migrations if needs change.

---

## Current Implementation Review

### What We're Using

**Tool:** Dynaconf v3.2.13  
**Config Files:**
- `settings.toml` (public, tracked) — non-sensitive defaults and site configs
- `.secrets.toml` (private, gitignored) — sensitive credentials
- `config.py` — Dynaconf loader and validator

**Current Features:**
✅ Environment-based configuration (per-site overrides)  
✅ Hierarchical settings (defaults + overrides)  
✅ Validation with typed constraints  
✅ Environment variable integration  
✅ Secrets separation (public vs private)  
✅ TOML file format (human-readable)  

---

## Strengths of Dynaconf for This Project

### 1. **Multi-Environment Support** (Perfect fit)
Dynaconf's environment sections (`[default]`, `[example_site]`, `[example_site_test]`) directly align with the project's need for:
- Multiple BriteCore instance support
- Per-site API credentials
- Test vs production separation

```toml
[default]
base_url = ""

[example_site]
base_url = "api.example.com"

[example_site_test]
base_url = "api-test.example.com"
```

No other config library handles this pattern as naturally.

### 2. **Secrets/Public Separation** (Excellent)
The dual-file approach keeps credentials out of version control while maintaining a clear public-facing config:
- Reduces attack surface
- Makes `.secrets.toml` easy to .gitignore
- Developers can use `settings.toml` as a template

### 3. **Validation** (Strong feature)
```python
Validator("base_url", "client_id", "client_secret", "api_key", must_exist=True, is_type_of=str)
```

Catches configuration errors early, improving reliability.

### 4. **Environment Variable Overrides** (Critical for CI/CD)
Supporting env vars like `BRITECORE_LIBRARIES_BASE_URL` enables:
- GitHub Actions workflows (without committing secrets)
- Docker container configuration
- Production deployments
- Local development flexibility

### 5. **Low Dependency Weight**
Dynaconf is:
- Pure Python (no native extensions)
- Lightweight (small footprint)
- Well-maintained (active project)
- Industry-standard (used by major projects)

---

## Weaknesses and Concerns

### 1. **Complexity for Simple Cases** (Minor)
If the project only needed a single static config file, Dynaconf would be overkill. But multi-site support justifies it.

**Current mitigation:** Good documentation (CONFIGURATION.md) helps developers understand the hierarchy.

### 2. **Validation Timing** (Medium)
Current code validates only on non-default environments:
```python
_active_env = os.environ.get("ENV_FOR_DYNACONF", "default").lower()
if _active_env != "default":
    settings.validators.validate()
```

**Why:** Development uses the default (incomplete) config, but production must be valid.

**Risk:** Missing credentials might not be caught until deployment.

**Mitigation:** API client validates again at init time:
```python
if not base_url or not (client_id and client_secret or api_key):
    raise BritecoreError("Missing required configuration")
```

### 3. **TOML Format Limitations** (Minor)
TOML is human-readable but less flexible than YAML/JSON for complex nested structures. However, the current config doesn't need complexity.

### 4. **Hot Reload Not Supported** (Not needed)
Dynaconf doesn't reload config on file changes without restart. This is fine for a library but would be a problem for long-running services.

---

## Alternatives Evaluated

### Alternative 1: **Simple Environment Variables Only**

**Pattern:**
```python
base_url = os.environ.get("BRITECORE_BASE_URL", "")
api_key = os.environ.get("BRITECORE_API_KEY", "")
```

**Pros:**
- ✅ No dependencies
- ✅ Zero configuration overhead
- ✅ Works everywhere (dev, CI/CD, prod)

**Cons:**
- ❌ No per-site configuration structure
- ❌ No validation
- ❌ Hard to document defaults
- ❌ Scaling to 50+ sites becomes unmaintainable

**Verdict:** Too simplistic for multi-site support. Would require env vars like `BRITECORE_SITE_A_*`, `BRITECORE_SITE_B_*`, etc. Not recommended.

---

### Alternative 2: **Python-Dict Config** (Like Django settings)

**Pattern:**
```python
# config.py
SITES = {
    "example_site": {
        "base_url": "api.example.com",
        "client_id": "...",
        "client_secret": "...",
    },
    "example_site_test": {
        "base_url": "api-test.example.com",
        "api_key": "...",
    },
}
```

**Pros:**
- ✅ Native Python (no external tool)
- ✅ Easy to validate at module load time
- ✅ Type-checkable with mypy

**Cons:**
- ❌ Can't keep secrets out of version control (no natural private/public split)
- ❌ Environment variables need explicit mapping code
- ❌ Less flexible for CI/CD (no standard format for env vars)
- ❌ Secrets would be in Python source → security risk

**Verdict:** Not suitable without major refactoring. Secrets management becomes a problem.

---

### Alternative 3: **python-dotenv** (For env vars only)

**Pattern:**
```python
from dotenv import load_dotenv
load_dotenv()
base_url = os.environ["BRITECORE_BASE_URL"]
```

**Pros:**
- ✅ Simple
- ✅ Works with .env files

**Cons:**
- ❌ Same issues as bare env vars
- ❌ Doesn't solve multi-site or secrets separation
- ❌ No validation
- ❌ .env files are easy to accidentally commit

**Verdict:** python-dotenv + TOML would just recreate what Dynaconf does. Not worth the reinvention.

---

### Alternative 4: **Pydantic Settings** (Modern approach)

**Pattern:**
```python
from pydantic_settings import BaseSettings

class SiteConfig(BaseSettings):
    base_url: str
    api_key: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
```

**Pros:**
- ✅ Type-safe (mypy compatible)
- ✅ Built-in validation
- ✅ Env var support
- ✅ Modern (Pydantic v2)

**Cons:**
- ❌ Requires code changes (separate model per site vs config file)
- ❌ Less flexible for adding new sites without code
- ❌ Multi-file config (like Dynaconf) still needs manual management
- ❌ Not significantly better for this use case

**Verdict:** Viable upgrade path for future, but requires code refactoring. Dynaconf is sufficient now.

---

## Recommendation: Keep Dynaconf

### Why It's the Right Choice

1. **Minimal disruption** — Already implemented and working well
2. **Future-proof** — Scales to 100+ sites without code changes (just config files)
3. **Security** — Secrets properly separated
4. **Operations** — Works with CI/CD, Docker, cloud platforms
5. **Documentation** — Clear CONFIGURATION.md guide

### Minor Improvements to Consider

#### 1. **Add Runtime Validation** (Low priority)
```python
# In LoadClientSettings.load_config()
if not config.base_url:
    raise ValueError("base_url is required")
if not (config.api_key or (config.client_id and config.client_secret)):
    raise ValueError("api_key or (client_id + client_secret) required")
```

**Status:** Already done in `BritecoreAPIClient.init_client()`

#### 2. **Document the Validation Hierarchy** (Medium priority)
Add diagram to CONFIGURATION.md showing:
```
Load order:
1. settings.toml defaults
2. settings.toml [site_name] overrides
3. .secrets.toml [site_name] overrides
4. Environment variables (BRITECORE_LIBRARIES_*)
5. Runtime validation (BritecoreAPIClient.init_client)
```

**Status:** Already in CONFIGURATION.md

#### 3. **Add Schema Validation Example** (Low priority)
Show users how to validate their config files before deployment:
```powershell
# Check config is valid
python -c "from britecore_libraries.config import settings; settings.validators.validate()"
```

**Status:** Not yet documented

---

## Future Migration Path (If Needed)

If the project scales significantly or requirements change, here's the upgrade path:

### Year 1-2: Current State (Dynaconf)
✅ Multi-site support  
✅ Secrets management  
✅ Validation  

### Year 3+: If needs dictate...
**Option A:** Migrate to **Pydantic Settings v2** (for stricter typing)  
**Option B:** Adopt **Kubernetes ConfigMaps** (if deployed on K8s)  
**Option C:** Use **AWS Secrets Manager** / **HashiCorp Vault** (for enterprise secrets)  

Migration would be non-breaking if done via adapter pattern:
```python
# Existing code stays unchanged
settings = LoadClientSettings("example_site").load_config()

# Internally, adapter could use Pydantic, K8s, or Vault
# without changing the public API
```

---

## Conclusion

**Dynaconf is the right tool** for this project's configuration needs:
- ✅ Multi-site support (perfect match)
- ✅ Secrets separation (critical)
- ✅ Validation (excellent)
- ✅ CI/CD friendly (proven)
- ✅ Low maintenance (well-maintained library)

**No action needed** — the current implementation is solid and follows best practices. Continue using Dynaconf unless requirements dramatically change (e.g., moving to Kubernetes or adopting a secrets management service).

---

## See Also

- [CONFIGURATION.md](docs/CONFIGURATION.md) — User guide
- [src/britecore_libraries/config/config.py](src/britecore_libraries/config/config.py) — Implementation
- [pyproject.toml](pyproject.toml) — Dependency specification

