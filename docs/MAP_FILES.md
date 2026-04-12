# Map Files

> **Architecture note:** As of the April 2026 refactor, all client-specific
> mapping data (agency, field, policy type) has been **removed from
> `britecore_sdk`**. Only generic/common mapping utilities remain in this package.
> If your deployment requires custom mapping data, it should be managed by your own
> downstream tools or configuration outside of the SDK.

## What `britecore_sdk/maps/` now provides

Only two public functions remain:

| Function | Purpose |
|---|---|
| `get_common_regexes()` | Carrier-agnostic compiled regex patterns used by validators (address, email, name, phone). No env vars required. |
| `load_regexes(system, overrides, naming_groups)` | Merges common patterns with caller-supplied carrier overrides. Carrier data should be injected by your own mapping logic. |

## Where mapping data now lives

Mapping data (such as agency, field, or policy type mappings) is no longer included in `britecore_sdk`.
You are expected to provide and manage these mappings in your own deployment or integration layer as needed.

## Security policy (unchanged)

- If you manage mapping files (such as TOML files with UUIDs or agency names), treat them as sensitive — do not commit real UUIDs or agency names to public repos.
- Keep private map files only in local or internal deployment environments.
- Do not store map payloads in public CI logs or artifacts.
- Rotate sensitive IDs if a private map file is ever exposed.

## Adding a new carrier system

To support a new carrier system, add or update your own mapping files and logic in your deployment or integration layer. Use the public functions in `britecore_sdk/maps/` to assist with regex and validation needs.
