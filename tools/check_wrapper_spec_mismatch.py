"""Compare OpenAPI request schemas to wrapper request_json/build_payload keys.

Usage:
    python tools/check_wrapper_spec_mismatch.py

This script prints a concise list of endpoints where the wrapper's request keys
don't match the spec-declared JSON request schema properties. It attempts to
handle common wrapper patterns: inline `request_json` dict literals and
`build_payload(...)` helper calls.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]  # this repository's britecore_sdk root
SRC_ROOT = REPO_ROOT / "src"
SPEC_PATH = REPO_ROOT / "api_specs" / "current" / "britecore.json"

VERSION_MAP = {"v1": "britecore_sdk.api.api_calls.v1", "v2": "britecore_sdk.api.api_calls.v2"}


def _resolve_local_schema_ref(schema: dict[str, Any], components: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/components/schemas/"):
        return schema
    schema_name = ref.rsplit("/", 1)[-1]
    schemas = components.get("schemas", {})
    if not isinstance(schemas, dict):
        return schema
    resolved = schemas.get(schema_name)
    return resolved if isinstance(resolved, dict) else schema


def _operation_schema(operation: dict[str, Any], components: dict[str, Any]) -> dict[str, Any]:
    request_body = operation.get("requestBody", {})
    if not isinstance(request_body, dict):
        return {}
    content = request_body.get("content", {})
    app_json = content.get("application/json", {}) if isinstance(content, dict) else {}
    schema = app_json.get("schema", {}) if isinstance(app_json, dict) else {}
    if not isinstance(schema, dict):
        return {}
    return _resolve_local_schema_ref(schema, components)


def path_to_module_func(api_path: str) -> tuple[str, str] | None:
    parts = api_path.strip("/").split("/")
    if len(parts) < 4:
        return None
    version = parts[1]
    module_segment = parts[2]
    func_name = parts[3]
    pkg = VERSION_MAP.get(version)
    if pkg is None:
        return None
    if version == "v1":
        func_name = func_name.lower()
    return f"{pkg}.{module_segment}", func_name


def extract_wrapper_keys(src_path: Path, func_name: str) -> dict[str, Any]:
    """Return a dict describing how the wrapper builds its request keys.

    Returns a dict with keys:
      - kind: 'request_json'|'build_payload'|'unknown'
      - keys: set of keys the wrapper includes (strings)
    """
    text = src_path.read_text(encoding="utf-8")
    idx = text.find(f"def {func_name}(")
    if idx == -1:
        return {"kind": "missing", "keys": set()}

    # Capture function body roughly by finding the next top-level 'def ' or end of file
    func_body = text[idx:]
    m_next_def = re.search(r"\ndef\s+\w+\s*\(|\n__all__", func_body)
    if m_next_def:
        func_body = func_body[: m_next_def.start()]

    # Try request_json literal
    m = re.search(r"request_json\s*:\s*dict\[.*?\]\s*=\s*\{", func_body)
    if m:
        start = m.end() - 1
        # find matching closing brace
        depth = 0
        keys = set()
        i = start
        while i < len(func_body):
            ch = func_body[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        literal = func_body[start:i+1]
        # extract quoted keys
        for key in re.findall(r"['\"]([A-Za-z0-9_ \-]+)['\"]\s*:\s*", literal):
            keys.add(key)
        return {"kind": "request_json", "keys": keys}

    # Try build_payload(...) usage
    m2 = re.search(r"build_payload\((.*?)\)", func_body, re.S)
    if m2:
        args_text = m2.group(1)
        # capture keyword names
        keys = set(k.strip() for k in re.findall(r"([A-Za-z0-9_]+)\s*=", args_text))
        return {"kind": "build_payload", "keys": keys}

    return {"kind": "unknown", "keys": set()}


def collect_spec_properties(spec_path: Path) -> dict[str, set[str]]:
    payload = json.loads(spec_path.read_text(encoding="utf-8"))
    components = payload.get("components", {}) if isinstance(payload, dict) else {}
    paths = payload.get("paths", {}) if isinstance(payload, dict) else {}
    mapping: dict[str, set[str]] = {}
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        op = path_item.get("post")
        if not isinstance(op, dict):
            continue
        schema = _operation_schema(op, components)
        props = set()
        if isinstance(schema, dict):
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                props.update(properties.keys())
            # include required fields also (they may not be in properties)
            required = schema.get("required", [])
            if isinstance(required, list):
                props.update(required)
        mapping[path] = props
    return mapping


def main() -> int:
    spec_props = collect_spec_properties(SPEC_PATH)
    mismatches: list[tuple[str, str, set[str], set[str], str]] = []

    for path, props in spec_props.items():
        mapping = path_to_module_func(path)
        if mapping is None:
            continue
        module_dotpath, func_name = mapping
        # derive source file path
        rel = module_dotpath.replace("britecore_sdk.", "")
        src_path = SRC_ROOT / "britecore_sdk" / Path(*rel.split("."))
        src_path = src_path.with_suffix(".py")
        if not src_path.exists():
            continue
        info = extract_wrapper_keys(src_path, func_name)
        wrapper_keys = set()
        if info["kind"] == "request_json" or info["kind"] == "build_payload":
            wrapper_keys = info["keys"]

        if wrapper_keys != props:
            mismatches.append((path, f"{module_dotpath}.{func_name}", props, wrapper_keys, info["kind"]))

    if not mismatches:
        print("No mismatches detected between spec request properties and wrapper keys (limited check).")
        return 0

    print("Detected mismatches (path, function, spec_props, wrapper_keys, wrapper_kind):\n")
    for path, func, spec_keys, wrapper_keys, kind in sorted(mismatches):
        print(f"- {path} -> {func}")
        print(f"    spec properties ({len(spec_keys)}): {sorted(spec_keys)}")
        print(f"    wrapper keys  ({len(wrapper_keys)}): {sorted(wrapper_keys)}  [kind={kind}]")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

