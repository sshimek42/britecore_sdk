# britecore_sdk documentation

This site hosts generated API docs and key project guides.


## Quick Navigation

This site is the canonical technical documentation for the SDK itself. If you need repo boundaries, ecosystem architecture, or cross-project workflow context, use the [`britecore_docs`](https://github.com/sshimek42/britecore_docs) hub instead.

**New to the SDK?** Start here:
1. [Getting Started](../../GETTING_STARTED.md) — Installation and first API call (5 min)
2. [Examples Overview](examples) — Runnable code examples
3. [Common Patterns](COMMON_PATTERNS) — Practical code patterns and recipes
4. [Configuration](../../CONFIG_MANAGEMENT.md) — Setting up credentials and environments
5. [Script-only data layer](SCRIPT_ONLY_DATA_LAYER) — Use models/normalizers without API calls

**Looking for specific help?**
- **"How do I...?"** → [Common Patterns](COMMON_PATTERNS)
- **"How do I configure...?"** → [Configuration](../../CONFIG_MANAGEMENT.md)
- **"Something broke"** → [Troubleshooting](../../TROUBLESHOOTING.md)
- **"I'm upgrading from v1"** → [Migration Guide](MIGRATION_v1_to_v2)
- **"I need an endpoint reference"** → [API Reference](api_reference)
- **"How does this fit in the wider BriteCore stack?"** → [britecore_docs](https://github.com/sshimek42/britecore_docs)

## Project Links

- GitHub repository: <https://github.com/sshimek42/britecore_sdk>
- Issue tracker: <https://github.com/sshimek42/britecore_sdk/issues>
- Releases: <https://github.com/sshimek42/britecore_sdk/releases>
- Changelog source: <https://github.com/sshimek42/britecore_sdk/blob/master/CHANGELOG.md>

---

```{toctree}
:maxdepth: 2
:caption: Getting Started

Project overview <project_overview>
examples
```

```{toctree}
:maxdepth: 2
:caption: Learn by Doing

Common patterns <COMMON_PATTERNS>
CONFIGURATION
Architecture roadmap <ARCHITECTURE_ROADMAP>
CACHING_STRATEGY
ASYNC_CACHING
Optional extras <OPTIONAL_EXTRAS>
Script-only data layer <SCRIPT_ONLY_DATA_LAYER>
```

```{toctree}
:maxdepth: 2
:caption: How-To Guides

Batch quote creation <BATCH_QUOTE_CREATION>
Rate limiting <RATE_LIMITING>
Events and webhooks <EVENTS_AND_WEBHOOKS>
Multi-tenancy <MULTI_TENANCY>
Staged workflows <STAGED_WORKFLOWS>
Line extract stitching <LINE_EXTRACT_STITCHING>
Implementation example <examples/FIRST_IMPLEMENTATION_EXAMPLE>
Observability <OBSERVABILITY>
```

```{toctree}
:maxdepth: 2
:caption: API Reference

Overview <api_reference>
API Domains <api_domains>
```

```{toctree}
:maxdepth: 2
:caption: Deployment & Operations

MAP_FILES
DEPLOYMENT
RTD_VERSIONING
CI_AND_COVERAGE
DOCUMENTATION_BUILD_TROUBLESHOOTING
DOCUMENTATION_RELEASE_CHECKLIST
RELEASE_OPERATIONS_CHECKLIST
RELEASE_HOTFIX_TEMPLATE
SOLO_MAINTAINER_MERGE_PROCEDURE
```

```{toctree}
:maxdepth: 2
:caption: Contributing & Policies

Implementation checklist <IMPLEMENTATION_CHECKLIST>
Developer workflow <AGENTS>
```

```{toctree}
:maxdepth: 1
:caption: Reference & Migration

MIGRATION_v1_to_v2
POST_PROBING
ENDPOINT_VERIFICATION_2026-04-28
REFERENCE_PROJECTS
```

---

```{note}
**Documentation metadata**

- **Version:** {{ docs_version }} | **Built:** {{ docs_build_date }} (UTC) | **Commit:** {{ docs_commit }} ({{ docs_commit_date }})
```
