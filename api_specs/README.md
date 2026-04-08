# API Specs

This directory contains checked-in API specification files used to document,
validate, and plan the SDK surface.

## Directory layout

```text
api_specs/
├── current/
│   └── britecore.json
└── legacy/
    ├── britecore/
    └── third_party/
```

## Source of truth policy

- `api_specs/current/britecore.json` is the canonical API contract for this SDK.
- Wrapper docstrings, wrapper/spec alignment tests, and future code-generation or
  drift-detection tooling should use `api_specs/current/britecore.json`.
- `tests/unit/test_api_spec_alignment.py` validates wrapper paths against the
  current spec only.

## Legacy specs

Files under `api_specs/legacy/` are archival reference material.

Use them for:

- researching older or alternate BriteCore API surfaces
- identifying potential future SDK wrappers
- creating backlog entries and implementation stubs
- comparing historical contract changes

Do not use them as the default enforcement target for:

- wrapper/spec alignment CI
- endpoint coverage claims
- public SDK support statements

## Legacy scope split

- `api_specs/legacy/britecore/` contains archived BriteCore-related specs.
- `api_specs/legacy/third_party/` contains archived third-party integration
  specs that may have been used alongside BriteCore workflows.

## Naming guidance

- Keep directory names lowercase for cross-platform consistency.
- Place the latest supported SDK contract in `current/`.
- Place superseded or research-only specs in `legacy/`.
- Prefer descriptive filenames that match the upstream product or domain.

## Packaging guidance

These files are primarily repository assets for maintenance, documentation, and
quality checks. They should not be treated as runtime configuration files unless
an explicit runtime use case is introduced later.

