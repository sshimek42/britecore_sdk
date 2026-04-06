# Sensitive Map Files

Use this guide when maintaining private mapping data under `src/britecore_libraries/maps/`.

## Policy

- Files matching `*_map.py` under `src/britecore_libraries/maps/` are treated as sensitive.
- Do not commit real map content to GitHub.
- Keep private map files only in local or internal deployment environments.

## Sample file formats

The examples below show expected structures only. Use placeholder values in committed examples and real values only in private copies.

### Agency map sample

```python
# Example structure only
agency: dict[str, str] = {
    "example agency llc": "11111111-1111-1111-1111-111111111111",
    "example agency": "11111111-1111-1111-1111-111111111111",
    "another agency": "22222222-2222-2222-2222-222222222222",
}
```

### Field map sample

```python
# Example structure only
field_map: dict[str, str] = {
    "external_field_name": "britecore_field_name",
    "agent_code": "agency_id",
    "policy_no": "policy_number",
}
```

### Policy map sample

```python
# Example structure only
policy: dict[str, str] = {
    "homeowners": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "dwelling_fire": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
}
```

### Policy name regex map sample

```python
import re

# Example structure only
REGEX_MAPS: dict[str, dict[str, re.Pattern[str]]] = {
    "example_system": {
        "reg_zip": re.compile(r"[^0-9]"),
        "reg_city_state": re.compile(r"\s{2,}"),
    }
}


def load_regexes(system: str) -> dict[str, re.Pattern[str]]:
    return REGEX_MAPS.get(system, {})
```

## Deployment checklist for private maps

- Keep real `*_map.py` files in private environments only.
- Validate imports in your runtime image before deployment.
- Do not store map payloads in public CI logs or artifacts.
- Rotate sensitive IDs if a private map file is ever exposed.

## Notes for existing repositories

If sensitive `*_map.py` files were already tracked, add the ignore rules and remove them from Git index history in your remediation workflow.
