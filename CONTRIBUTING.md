# Contributing

*Last updated: April 28, 2026*
*Document type: Living contributor guide*

This guide covers the project workflow for contributing changes safely and consistently.

## Start here

- Read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before participating in project discussions or
  reviews.
- Read `AGENTS.md` first for repository-specific coding patterns.
- Install in editable mode with dev dependencies.
- Run targeted tests for changed modules, then run full test suite.

Related docs:

- [README.md](README.md) for project overview
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations
- [GETTING_STARTED.md](GETTING_STARTED.md) for setup and first run
- [API.md](API.md) for endpoint behavior and examples
- [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known issues
- [DEPRECATION.md](DEPRECATION.md) for deprecation policy
- [docs/MULTI_TENANCY.md](docs/MULTI_TENANCY.md) for multi-site patterns
- [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) for logging and monitoring
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment

## Development setup

```bash
python -m pip install -e ".[dev]"
```

### Git hooks and fileshare settings sync

Enable tracked hooks once per clone (this turns on `.githooks/pre-push`):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-git-hooks.ps1
```

`fileshare-settings` is a fileshare-only branch used for local `settings.toml` and `.secrets.toml` updates. Sync it with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync-fileshare-settings.ps1
```

Preview staged changes without pushing:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync-fileshare-settings.ps1 -DryRun
```

The pre-push hook blocks `fileshare-settings` from being pushed to `origin`.

### Pre-commit hooks

Install Git hooks once per clone:

```bash
pre-commit install
```

Run hooks manually across the repo:

```bash
pre-commit run --all-files
```

Notes:

- Python hooks include `ruff`, `ruff-format`, and `black`.
- Markdown structure linting runs via `pymarkdown` and only triggers when `*.md` files are changed.
- CI also runs `Vale` on changed Markdown files for low-noise prose/style checks.
- If you have `Vale` installed locally, you can run it manually with `vale --config=.vale.ini README.md`.

Optional virtual environment:

**Linux/macOS (bash):**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

### Configuration

The SDK uses a **layered configuration system** (lowest → highest priority):

1. SDK package defaults (`src/britecore_sdk/settings/settings.toml` + `.secrets.toml` — in `.gitignore`, optional)
2. User-level config (`~/.britecore/settings.toml` + `~/.britecore/.secrets.toml`)
3. Project-local config (`./britecore.toml` + `./.britecore_secrets.toml` in CWD)
4. Explicit file path (`BRITECORE_SDK_SETTINGS_FILE` env var)
5. `BRITECORE_SDK_*` environment variables (highest priority)

#### Option A: Environment variables

Set `target_site` and `system` for basic multi-site testing:

**Linux/macOS (bash):**

```bash
export target_site="your_site"
export system="your_system"
```

**Windows (PowerShell):**

```powershell
$env:target_site = "your_site"
$env:system = "your_system"
```

#### Option B: Local config file

Create `britecore.toml` in your project root:

```toml
target_site = "your_site"
system = "your_system"
base_url = "https://api.example.com"
api_key = "your_api_key"
```

#### Option C: Explicit inline credentials (recommended for tests)

Bypass file lookup entirely by passing credentials directly:

```python
from britecore_sdk import init_api_client

# API key auth
client = init_api_client(
    base_url="https://api.example.com",
    api_key="your_api_key"
)

# OAuth auth
client = init_api_client(
    base_url="https://api.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

This pattern is best for test isolation and CI/CD environments where environment variables should not be set globally.

## Branch and commit workflow

```bash
git checkout -b feature/short-description
```

- Keep changes focused and small.
- Update docs when behavior or public usage changes.
- Keep public exports current in package `__init__.py` files when adding new top-level APIs.

## Testing workflow

Minimum validation command set for API-client or exception changes:

```bash
python -m pytest tests/unit/test_exceptions.py tests/unit/test_core_client_coverage.py -v
python -m pytest tests/unit/test_api_client.py -v
python -c "import britecore_sdk; from britecore_sdk.api.britecore_api_client import BritecoreAPIClient; print(britecore_sdk.__version__)"
```

Run targeted tests first:

```bash
python -m pytest tests/unit/test_api_client.py -v
```

Run standard suites before opening a PR:

```bash
python -m pytest tests/ -v
python -m pytest tests/unit -m unit -v
python -m pytest tests/integration -m integration -v

```

Coverage output is configured in `pyproject.toml` via pytest addopts.

Quality gates run in CI:

- `ruff check src tests`
- `black --check src tests`
- `mypy` for core client and key endpoint modules
- `pytest tests/unit -m unit --cov ...`

## Project-specific coding conventions

- Treat `src/britecore_sdk/` as source of truth; ignore generated artifacts under build and egg-info folders.
- For endpoint wrappers, follow existing `v2` module pattern: build payload, call `API_CLIENT.do_request(...)`, return `API_CLIENT.process_result(...)`.
- Use `RequestParameters` and `**kwargs: Unpack[RequestParameters]` in new endpoint functions where request overrides are supported.
- Use `API_CLIENT.multiple_parameter_verification(...)` for mutually exclusive identifiers.
- Use imports from `models` and `validators`; `classes` import paths are removed.

## Repo layout contract

- Edit authored code in `src/britecore_sdk/` and tests in `tests/`; avoid direct edits in generated paths like `build/`, `dist/`, `.venv/`, `htmlcov/`, and `docs/_build/`.
- Keep root docs as canonical when mirrored by docs includes (currently `PYTHON_COMPATIBILITY.md` and `UNIMPLEMENTED_API_STUBS.md`), and let `docs/*.md` include those files.
- Keep dependency/version definitions in `pyproject.toml` as the single source of truth.

## Pull request checklist

- [ ] Tests pass locally for changed behavior.
- [ ] Docs updated when public behavior changes.
- [ ] New exports added to relevant `__all__` lists.
- [ ] New endpoint wrappers follow existing `v2` request/response pattern.
- [ ] Config/env assumptions are documented if needed.

## Need help?

If behavior is unclear, compare your change against existing endpoint modules in `src/britecore_sdk/api/api_calls/v2/` and check `AGENTS.md` for current guidance.
