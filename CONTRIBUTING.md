# Contributing

*Last updated: March 31, 2026*
*Document type: Living contributor guide*

This guide covers the project workflow for contributing changes safely and consistently.

## Start here

- Read `AGENTS.md` first for repository-specific coding patterns.
- Install in editable mode with dev dependencies.
- Run targeted tests for changed modules, then run full test suite.

Related docs:

- [README.md](README.md) for project overview
- [GETTING_STARTED.md](GETTING_STARTED.md) for setup and first run
- [API.md](API.md) for endpoint behavior and examples
- [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known issues

## Development setup

```powershell

python -m pip install -e ".[dev]"

```

Optional virtual environment:

```powershell

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

```

Set local environment variables:

```powershell

$env:target_site = "your_site"
$env:system = "your_system"

```

## Branch and commit workflow

```powershell

git checkout -b feature/short-description

```

- Keep changes focused and small.
- Update docs when behavior or public usage changes.
- Keep public exports current in package `__init__.py` files when adding new top-level APIs.

## Testing workflow

Minimum validation command set for API-client or exception changes:

```powershell

python -m pytest tests/unit/test_exceptions.py tests/unit/test_core_client_coverage.py -v
python -m pytest tests/unit/test_api_client.py -v
python -c "import britecore_libraries; from britecore_libraries.api.britecore_api_client import BritecoreAPIClient; print(britecore_libraries.__version__)"

```

Run targeted tests first:

```powershell

python -m pytest tests/unit/test_api_client.py -v

```

Run standard suites before opening a PR:

```powershell

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

- Treat `src/britecore_libraries/` as source of truth; ignore generated artifacts under build and egg-info folders.
- For endpoint wrappers, follow existing `v2` module pattern: build payload, call `API_CLIENT.do_request(...)`, return `API_CLIENT.process_result(...)`.
- Use `RequestParameters` and `**kwargs: Unpack[RequestParameters]` in new endpoint functions where request overrides are supported.
- Use `API_CLIENT.multiple_parameter_verification(...)` for mutually exclusive identifiers.
- Prefer models and validators packages over legacy imports from `classes`.

## Pull request checklist

- [ ] Tests pass locally for changed behavior.
- [ ] Docs updated when public behavior changes.
- [ ] New exports added to relevant `__all__` lists.
- [ ] New endpoint wrappers follow existing `v2` request/response pattern.
- [ ] Config/env assumptions are documented if needed.

## Need help?

If behavior is unclear, compare your change against existing endpoint modules in `src/britecore_libraries/api/api_calls/v2/` and check `AGENTS.md` for current guidance.
