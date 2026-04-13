# CI/CD and Coverage Guide

This guide explains the continuous integration (CI) pipeline and code coverage reporting setup for `britecore_sdk`.

## Overview

The project uses:

- **GitHub Actions** — automated testing, linting, docs building
- **DeepSource** — static analysis and coverage tracking
- **Codecov** — coverage artifacts storage
- **pytest** — test framework with coverage collection

## GitHub Actions Workflows

### Location

```text
.github/workflows/
├── tests.yml       # Run pytest + coverage on all Python versions
├── lint.yml        # Run ruff, black, mypy checks
├── ci.yml          # Coordination job
└── docs.yml        # Build Sphinx documentation
```

### `tests.yml` — Test Matrix

**Trigger:** Push to `master`, `main`, `develop`; pull requests to these branches

**What it does:**

1. Run tests on **Python 3.11, 3.12, 3.13, 3.14** (full matrix)
2. Collect coverage from all runs
3. Upload coverage to **Codecov** and **DeepSource** (from Python 3.11, non-randomized run)
4. Generate coverage HTML report

**Key steps:**

```yaml
- name: Run tests with pytest
  run: pytest tests/ -v --cov=src/britecore_sdk --cov-report=xml

- name: Upload coverage to Codecov
  if: matrix.python-version == '3.11'
  uses: codecov/codecov-action@v4

- name: Report test coverage to DeepSource
  if: matrix.python-version == '3.11' && matrix.randomized == false
  uses: deepsourcelabs/test-coverage-action@master
  with:
    key: python
    coverage-file: coverage.xml
    dsn: ${{ secrets.DEEPSOURCE_DSN }}
```

**Why one canonical upload only?**

- Tests run on all versions for compatibility
- But uploading from every matrix leg creates duplicate/noisy reports
- 3.11 is the minimum supported version, so it's canonical

### `lint.yml` — Code Quality

**Trigger:** Same as tests

**What it does:**

1. Run **ruff** (linting: E9, F63, F7, F82)
2. Run **black** (formatting check)
3. Run **mypy** (type checking on core modules)

**Passes silently** — all checks use `continue-on-error: true` to not block PRs.

### `docs.yml` — Documentation Build

**Trigger:** Same as tests

**What it does:**

1. Install Sphinx + dependencies
2. Build docs using the **dummy builder** (quick validation)
3. Upload `htmlcov/` artifacts

**Why dummy builder?**

- Fast validation that docs syntax is correct
- Doesn't generate full HTML (that's optional locally)
- Ensures docs can be built in any environment

### `ci.yml` — Coordination

Simple status check. Can be expanded for complex workflows.

## DeepSource Integration

### What it does

DeepSource runs on every PR to:

1. **Static analysis** — finds code smell, potential bugs
2. **Test coverage** — tracks which code paths are tested
3. **Secret detection** — flags committed credentials and tokens

### Enabled Analyzers

In `.deepsource.toml`:

```toml
[[analyzers]]
name = "python"      # Static analysis
enabled = true

  [analyzers.meta]
  runtime_version = "3.x.x"
  max_line_length = 120
  skip_doc_coverage = ["module", "magic", "init", "class", "nonpublic"]

[[analyzers]]
name = "secrets"     # Credential detection
enabled = true

[[analyzers]]
name = "test-coverage"  # Coverage tracking
enabled = true
```

### Setup (One-time)

1. **Connect GitHub repo to DeepSource:**
   - Go to [app.deepsource.com](https://app.deepsource.com)
   - Link your GitHub account
   - Add `sshimek42/britecore_sdk`

2. **Add `DEEPSOURCE_DSN` secret to GitHub:**
   - In DeepSource → **Settings → Integrations → Reporting**
   - Copy the **DSN** value
   - In GitHub → **Settings → Secrets → Actions**
   - Create secret: `DEEPSOURCE_DSN` = (paste DSN)

3. **Verify in PR:**
   - Open a PR or push to your branch
   - Check that DeepSource status check appears
   - All analyzers should be green

### Understanding DeepSource Results

**PR Check Status:**

- ✅ **All checks passed** — No new issues, coverage acceptable
- ⚠️ **Analysis warnings** — New static-analysis or documentation/style findings were reported
- 🔴 **Analysis failed** — Issues found (security, type errors, etc.)

**Coverage Interpretation:**

- **Lines covered** — Code paths executed by tests
- **Uncovered lines** — Code paths not tested
- **Covered %** — Percentage of total lines with test coverage

**Common findings:**

- `PYL-W0404` — Duplicate import (low severity, often defer)
- `PTC-W0062` — Mergeable `with` blocks (cosmetic, safe to ignore)
- `PYL-E0401` — Import errors (fix immediately)

### Workflow

1. **Push feature branch** → DeepSource runs analysis
2. **Review PR checks** → DeepSource shows issues (if any)
3. **Fix issues** (or suppress if false positive) → Commit
4. **Checks pass** → Ready to merge

## Coverage Reports

### Codecov

**Purpose:** Long-term coverage tracking and trend analysis

**What's uploaded:** `coverage.xml` from pytest-cov

**Access:**

- GitHub PR → Codecov check → "View report on Codecov"
- Or: `https://app.codecov.io/gh/sshimek42/britecore_sdk`

**Useful for:**

- Tracking coverage over time
- Comparing coverage across branches
- Setting coverage gates (e.g., fail if coverage drops below 75%)

### DeepSource Coverage

**Purpose:** Integrated coverage analysis (alongside static analysis)

**What's uploaded:** `coverage.deepsource.xml` (a path-rewritten copy of `coverage.xml`) via `deepsourcelabs/test-coverage-action`

**Why a separate file?**

pytest-cov with `--cov=src/britecore_sdk` produces `coverage.xml` with package-relative paths
(e.g., `__init__.py`, `api/britecore_api_client.py`). DeepSource requires repo-relative paths
(e.g., `src/britecore_sdk/__init__.py`) to map files back to VCS. The CI step
"Rewrite coverage paths for DeepSource" patches all `filename` attributes before upload.

**Access:**

- GitHub PR → DeepSource check → Link to run
- Or: `https://app.deepsource.com/gh/sshimek42/britecore_sdk`

**Useful for:**

- Flagging uncovered code paths in PRs
- Setting baseline coverage requirements
- Visualizing coverage + issues together

**Troubleshooting "files not present in VCS" warning:**

If DeepSource reports coverage files not found in VCS, check that:

1. The "Rewrite coverage paths for DeepSource" CI step ran (only on `python-version == '3.11' && randomized == false`).
2. `coverage.deepsource.xml` was generated — if not, the DeepSource step falls back to an empty report.
3. `coverage.xml` exists in the repo root after the pytest step.

### Local Coverage Reports

After running tests locally:

```powershell
pytest tests/ --cov=src/britecore_sdk --cov-report=html
open htmlcov/index.html
```

This creates a **local HTML report** showing line-by-line coverage.

## Test Coverage Targets

From `pytest.ini`:

```ini
[pytest]
addopts = --cov=src/britecore_sdk --cov-report=html --cov-report=term-missing --strict-markers
```

**Coverage gate:**

From `.github/workflows/tests.yml`:

```yaml
- name: Generate coverage report
  run: coverage report --fail-under=75
  continue-on-error: true
```

**Current target:** 75% coverage

**Modules with higher expectations:**

- `src/britecore_sdk/settings/` — 90%+
- `src/britecore_sdk/api/britecore_api_client.py` — 80%+
- Core validators — 85%+

## Local Testing and Coverage

### Install Dev Dependencies

```powershell
pip install -e ".[dev]"
```

### Run All Tests

```powershell
pytest tests/ -v --cov=src/britecore_sdk --cov-report=html
```

### Run Specific Test Category

```powershell
# Unit tests only
pytest tests/unit -m unit -v

# Integration tests only
pytest tests/integration -m integration -v

# Slow tests (sandbox)
pytest tests/ -m slow -v
```

### Check Coverage for Specific Module

```powershell
coverage report src/britecore_sdk/api/britecore_api_client.py
```

### Run Linters Locally

```powershell
# Ruff
ruff check src/britecore_sdk

# Black (check only)
black --check src/britecore_sdk

# MyPy
mypy src/britecore_sdk
```

## Troubleshooting CI

### "DeepSource: Python" or "test-coverage" check is failing

**Common causes:**

1. **Missing `DEEPSOURCE_DSN` secret**
   - Check GitHub → Settings → Secrets
   - Confirm secret is named exactly `DEEPSOURCE_DSN`
   - Regenerate if unsure (DeepSource → Settings → Integrations → Reporting)

2. **Python analyzer misconfiguration**
   - Check `.deepsource.toml` has:

     ```toml
     [[analyzers]]
     name = "python"
     enabled = true
     ```

   - Verify `runtime_version = "3.x.x"` in meta section

3. **Test-coverage analyzer not enabled**
   - Check `.deepsource.toml` has:

     ```toml
     [[analyzers]]
     name = "test-coverage"
     enabled = true
     ```

4. **Coverage.xml not generated**
   - Ensure `pytest` command includes `--cov-report=xml`
   - Check `coverage.xml` exists in repo root after local test run

**Debug steps:**

```powershell
# Run tests locally and verify coverage.xml
pytest tests/ --cov=src/britecore_sdk --cov-report=xml
ls coverage.xml  # Should exist

# Check DeepSource config syntax
python -c "import tomllib; tomllib.loads(open('.deepsource.toml').read())"
```

### Coverage drop between PRs

1. **Check if coverage gate is enforced:**

   ```powershell
   coverage report --fail-under=75
   ```

2. **Add tests for uncovered code:**
   - Run locally: `pytest --cov --cov-report=html`
   - Open `htmlcov/index.html`
   - Find red (uncovered) lines
   - Add tests for those paths

3. **View coverage per file:**

   ```powershell
   coverage report -m  # Shows uncovered lines
   ```

## Best Practices

### Before Pushing

1. **Run tests locally:**

   ```powershell
   pytest tests/ --cov=src/britecore_sdk
   ```

2. **Check coverage:**

   ```powershell
   coverage report --fail-under=75
   ```

3. **Lint:**

   ```powershell
   black --check src/
   ruff check src/
   mypy src/britecore_sdk/api/britecore_api_client.py
   ```

4. **Verify no uncommitted secrets:**

   ```powershell
   git status  # Should not show .secrets.toml modified
   ```

### In PRs

1. **Address DeepSource issues** — don't suppress unless false positive
2. **Maintain or improve coverage** — don't let it drop
3. **Keep formatting consistent** — let black/isort auto-fix
4. **Type-check critical paths** — mypy helps catch bugs early

### Merging

- All CI checks must pass (tests, lint, DeepSource)
- Coverage must be >= 75%
- At least one approval from maintainer
- Commits should be squashed or well-organized

## See Also

- [tests/README.md](../tests/README.md) — Test suite guide
- [.github/workflows/tests.yml](../.github/workflows/tests.yml) — Workflow definition
- [.deepsource.toml](../.deepsource.toml) — DeepSource configuration
- [pytest.ini](../pytest.ini) — pytest defaults (test discovery, markers, coverage addopts)
- [pyproject.toml](../pyproject.toml) — coverage, lint, formatter, and mypy settings

## Bash Equivalents (Common Local Commands)

```bash
pip install -e ".[dev]"
pytest tests/ -v --cov=src/britecore_sdk --cov-report=html
pytest tests/unit -m unit -v
pytest tests/integration -m integration -v
coverage report --fail-under=75
coverage report -m
ruff check src/britecore_sdk
black --check src/britecore_sdk
mypy src/britecore_sdk
python -c "import tomllib; tomllib.loads(open('.deepsource.toml').read())"
git status
```
