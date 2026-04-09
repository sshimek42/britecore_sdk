# Map Files

> **Architecture note:** As of the April 2026 refactor, all client-specific
> mapping data (agency, field, policy type) has been **removed from
> `britecore_libraries`** and is now owned exclusively by `britecore_import`.
> See `britecore_import/data/mappings/` and
> `britecore_import/src/britecore_import/mappings/` for the current
> source of truth.

## What `britecore_libraries/maps/` now provides

Only two public functions remain:

| Function | Purpose |
|---|---|
| `get_common_regexes()` | Carrier-agnostic compiled regex patterns used by validators (address, email, name, phone). No env vars required. |
| `load_regexes(system, overrides, naming_groups)` | Merges common patterns with caller-supplied carrier overrides. Carrier data is injected by `britecore_import.mappings.RegexMappings`. |

## Where mapping data now lives (in `britecore_import`)

| Data | File | Access class |
|---|---|---|
| Agency name → UUID | `data/mappings/agency_mappings.toml` | `AgencyMappings` |
| Carrier field → BriteCore field | `data/mappings/field_mappings.toml` | `FieldMappings` |
| Policy type code → UUID | `data/mappings/policy_type_mappings.toml` | `PolicyTypeMappings` |
| System regex overrides + name groups | `mappings/regex_mappings.py` | `RegexMappings` |

## Security policy (unchanged)

- TOML map files under `data/mappings/` are treated as sensitive — do not commit real UUIDs or agency names to public repos.
- Keep private map files only in local or internal deployment environments.
- Do not store map payloads in public CI logs or artifacts.
- Rotate sensitive IDs if a private map file is ever exposed.

## Adding a new carrier system

1. Add field mappings to `data/mappings/field_mappings.toml` under a new `[system_name]` section.
2. Add agency/policy mappings to the corresponding TOML files.
3. Add regex overrides and naming groups to `mappings/regex_mappings.py` (`_SYSTEM_OVERRIDES` and `_SYSTEM_NAMING_GROUPS`).
4. Register the mutual in `settings/settings.toml` and `Settings._parse_mutuals()`.

