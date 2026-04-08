# Python Compatibility Matrix

Canonical source: this file. `docs/python_compatibility.md` includes this content.

*Last updated: April 7, 2026*
*Document type: Living compatibility policy*

**BriteCore Libraries** — supported Python versions and compatibility commitments.

---

## Supported Python Versions

| Python Version | Status | Notes |
| --- | --- | --- |
| 3.11 | ✅ Supported | Minimum supported version |
| 3.12 | ✅ Supported | Recommended for most production deployments |
| 3.13 | ✅ Supported | — |
| 3.14 | ✅ Supported | Original development target; fully tested |
| 3.10 and below | ❌ Unsupported | Uses `X \| Y` union types (PEP 604); will not parse |

### Why ≥3.11?

The codebase uses several Python 3.10+ features:

- **`X | Y` union type syntax** (PEP 604) — e.g. `str | None` in signatures
- **`match`/`case`** is not used but structural pattern matching is available
- **`TypedDict` with `NotRequired`** (PEP 655) — requires 3.11 for full runtime
  support

Syntax compatibility with 3.10 is marginal; 3.11 is the safe floor because
`tomllib` (used by tooling), `Self`, and `LiteralString` are stdlib on 3.11.

---

## BriteCore API Version Compatibility

| Library Version | BriteCore API | Notes |
| --- | --- | --- |
| 1.0.0+ | current API | Endpoint wrappers and specs track the current contract |
| 0.x | pre-release API surface | Pre-release; no stability guarantee |

---

## Stability Commitment (≥1.0.0)

Starting from `1.0.0` the library follows **semantic versioning**:

| Change Type | Version Bump | Example |
| --- | --- | --- |
| Bug fixes, doc updates | Patch (x.x.**Z**) | 1.0.0 → 1.0.1 |
| New backwards-compatible features | Minor (x.**Y**.0) | 1.0.0 → 1.1.0 |
| Breaking public API changes | Major (**X**.0.0) | 1.0.0 → 2.0.0 |

### What counts as "public API"?

- All symbols exported in `britecore_libraries.__all__`
- All functions in `api/api_calls/v2/` with documented signatures
- `BritecoreAPIClient.do_request()`, `.process_result()`, `.init_client()`
- `BritecoreError` exception hierarchy
- `RequestParameters` TypedDict

### Breaking-change policy

1. Public API removals and signature changes occur only in a **major** release.
2. Breaking changes are documented in `CHANGELOG.md`.
3. Minor and patch releases maintain the documented public API contract.

---

## Dependency Version Policy

Runtime dependencies are pinned with `~=` (compatible-release) constraints:

```toml

urllib3~=2.6          # HTTP transport
dynaconf~=3.2         # Configuration management

```

This means patch-level updates are picked up automatically; minor upgrades
require an explicit update to `pyproject.toml`.

---

## Testing Matrix

The CI pipeline validates the following matrix:

| Python | OS | Auth mode |
| --- | --- | --- |
| 3.11 | Ubuntu latest | API key |
| 3.12 | Ubuntu latest | API key |
| 3.13 | Ubuntu latest | API key |
| 3.14 | Ubuntu latest | API key |

---

## Known Limitations by Python Version

### Python 3.11

- `tomllib` is stdlib; no `tomli` backport needed.
- `Self` type (`typing.Self`) available.
- `LiteralString` available.

### Python 3.12+

- `@override` decorator available (`typing.override`) — not yet adopted in this
  codebase but safe to use.
- `sys.monitoring` instrumentation available for deeper tracing.

### Python 3.14

- Original development target. All type annotations validated.
- `annotationlib` changes do not affect runtime behaviour of this library.

---
