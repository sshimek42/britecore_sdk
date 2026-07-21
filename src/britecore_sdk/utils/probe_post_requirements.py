"""Probe POST endpoints to discover validation requirements from API errors.

The probe runner intentionally sends invalid payloads to collect structured 4xx
responses in a sandbox environment. Results are saved as JSON and optional
Markdown for endpoint wrapper/docs follow-up.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.exceptions import BritecoreError

LOGGER = logging.getLogger("britecore_sdk")

_ALLOWED_RISKS = {"low", "medium", "high"}
_SPEC_PATH = (
    Path(__file__).resolve().parents[3] / "api_specs" / "current" / "britecore.json"
)
_HIGH_RISK_HINTS = (
    "bind",
    "issue",
    "submit",
    "cancel",
    "approve",
    "finalize",
    "void",
    "refund",
    "charge",
    "delete",
)


@dataclass(frozen=True)
class ProbeDefinition:
    """Single POST probe definition loaded from the plan file."""

    name: str
    path: str
    payload: dict[str, Any]
    risk: str = "medium"
    headers: dict[str, str] | None = None
    notes: str | None = None
    enabled: bool = True


@dataclass(frozen=True)
class ProbeResult:
    """Normalized probe outcome for reporting and downstream review."""

    name: str
    path: str
    risk: str
    outcome: str
    status_code: int | None
    request_id: str | None
    messages: list[str]
    inferred_required_fields: list[str]
    notes: str | None


class _SupportsDoRequest(Protocol):
    """Minimal protocol for probe execution clients."""

    def do_request(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        request_timeout: Any = None,
        request_retries: Any = None,
        request_headers: dict[str, Any] | None = None,
        method: str = "POST",
        cache_enabled: bool = False,
        cache_ttl_seconds: int | None = None,
        cache_namespace: str | None = None,
        cache_key_parts: list[str] | tuple[str, ...] | None = None,
        cache_bypass: bool = False,
        cache_invalidate_on_success: list[str] | tuple[str, ...] | None = None,
        dedupe_in_flight: bool = False,
        dry_run: bool | None = None,
        dry_run_include_sensitive_headers: bool = False,
        rate_limiter_bypass: bool = False,
    ) -> Any: ...


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the POST probe runner."""
    parser = argparse.ArgumentParser(
        description=(
            "Probe POST endpoints with intentionally invalid payloads to discover "
            "missing required fields from 4xx responses."
        )
    )
    preview_group = parser.add_mutually_exclusive_group()
    parser.add_argument("--plan", required=False, help="Path to probe plan JSON file.")
    parser.add_argument(
        "--use-spec-no-args",
        action="store_true",
        help=(
            "Autogenerate probes from api_specs/current/britecore.json for POST "
            "operations that document no arguments."
        ),
    )
    parser.add_argument(
        "--use-spec-empty-properties",
        action="store_true",
        help=(
            "Autogenerate probes from api_specs/current/britecore.json for POST "
            "operations whose JSON request schema has no properties/required fields."
        ),
    )
    parser.add_argument(
        "--spec-path",
        default=str(_SPEC_PATH),
        help="OpenAPI spec path used with --use-spec-no-args.",
    )
    parser.add_argument(
        "--include-path-regex",
        required=False,
        help="Optional regex filter for generated probe paths.",
    )
    parser.add_argument(
        "--max-probes",
        required=False,
        type=int,
        help="Optional max number of probes to run after loading/generation.",
    )
    parser.add_argument(
        "--write-generated-plan",
        required=False,
        help="Optional JSON file path to write the resolved probe plan before execution.",
    )
    preview_group.add_argument(
        "--print-selected-paths",
        action="store_true",
        help=(
            "Print resolved probe paths and exit without executing requests. "
            "Useful for previewing selector output."
        ),
    )
    preview_group.add_argument(
        "--export-selected-paths",
        required=False,
        help="Write resolved probe preview rows to JSON or CSV and exit.",
    )
    parser.add_argument(
        "--site",
        required=False,
        help="Configured target site name (optional when --base-url is used).",
    )
    parser.add_argument(
        "--base-url",
        required=False,
        help="Optional explicit base URL to bypass file-based config lookup.",
    )
    parser.add_argument(
        "--api-key",
        required=False,
        help="Optional explicit API key (used with --base-url).",
    )
    parser.add_argument(
        "--client-id",
        required=False,
        help="Optional explicit OAuth client ID (used with --base-url).",
    )
    parser.add_argument(
        "--client-secret",
        required=False,
        help="Optional explicit OAuth client secret (used with --base-url).",
    )
    parser.add_argument(
        "--allow-high-risk",
        action="store_true",
        help="Allow probes marked risk=high. High-risk probes are skipped by default.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use SDK dry-run mode (request envelope only, no network call).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--output-json",
        default="post_probe_report.json",
        help="Output path for JSON report.",
    )
    parser.add_argument(
        "--output-markdown",
        default="post_probe_report.md",
        help="Output path for Markdown report.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level for progress output (default: INFO).",
    )
    args = parser.parse_args(argv)
    if (
        not args.plan
        and not args.use_spec_no_args
        and not args.use_spec_empty_properties
    ):
        parser.error(
            "Pass --plan, --use-spec-no-args, and/or --use-spec-empty-properties."
        )
    if args.max_probes is not None and args.max_probes <= 0:
        parser.error("--max-probes must be greater than 0 when provided.")
    return args


def _has_documented_parameters(
    path_item: dict[str, Any], operation: dict[str, Any]
) -> bool:
    """Return True when a path or operation declares any explicit parameters."""
    path_parameters = path_item.get("parameters", [])
    op_parameters = operation.get("parameters", [])
    return bool(
        isinstance(path_parameters, list)
        and path_parameters
        or isinstance(op_parameters, list)
        and op_parameters
    )


def _resolve_local_schema_ref(
    schema: dict[str, Any], components: dict[str, Any]
) -> dict[str, Any]:
    """Resolve local #/components/schemas refs, returning original schema on miss."""
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/components/schemas/"):
        return schema
    schema_name = ref.rsplit("/", 1)[-1]
    schemas = components.get("schemas", {})
    if not isinstance(schemas, dict):
        return schema
    resolved = schemas.get(schema_name)
    if not isinstance(resolved, dict):
        return schema
    return resolved


def _operation_schema(
    operation: dict[str, Any],
    components: dict[str, Any],
) -> dict[str, Any]:
    """Return resolved application/json request schema for an operation when present."""
    request_body = operation.get("requestBody", {})
    if not isinstance(request_body, dict):
        return {}
    content = request_body.get("content", {})
    if not isinstance(content, dict):
        return {}
    app_json = content.get("application/json", {})
    if not isinstance(app_json, dict):
        return {}
    schema = app_json.get("schema", {})
    if not isinstance(schema, dict):
        return {}
    return _resolve_local_schema_ref(schema, components)


def _schema_has_documented_fields(schema: dict[str, Any]) -> bool:
    """Return True when schema declares any usable request fields/variants."""
    properties = schema.get("properties", {})
    if isinstance(properties, dict) and properties:
        return True

    required = schema.get("required", [])
    if isinstance(required, list) and required:
        return True

    for key in ("oneOf", "anyOf", "allOf"):
        group = schema.get(key, [])
        if isinstance(group, list) and group:
            return True

    return False


def _operation_has_documented_arguments(
    path_item: dict[str, Any],
    operation: dict[str, Any],
    components: dict[str, Any],
) -> bool:
    """Return True when a POST operation documents request parameters/body fields."""
    if _has_documented_parameters(path_item, operation):
        return True

    schema = _operation_schema(operation, components)
    return _schema_has_documented_fields(schema)


def _operation_has_empty_json_schema(
    path_item: dict[str, Any],
    operation: dict[str, Any],
    components: dict[str, Any],
) -> bool:
    """Return True when POST has no path/query/header params and empty JSON schema."""
    if _has_documented_parameters(path_item, operation):
        return False

    schema = _operation_schema(operation, components)
    if not schema:
        return False
    return not _schema_has_documented_fields(schema)


def _risk_from_path(path: str) -> str:
    """Assign a cautious default risk level from action-style endpoint path hints."""
    lowered = path.lower()
    if any(hint in lowered for hint in _HIGH_RISK_HINTS):
        return "high"
    return "medium"


def _autogenerated_probe_name(path: str) -> str:
    """Build a stable probe name from an API path."""
    text = re.sub(r"[^a-zA-Z0-9]+", "_", path.strip("/")).strip("_").lower()
    return f"spec_no_args_{text or 'endpoint'}"


def _load_no_arg_post_probes_from_spec(
    spec_path: str | Path,
    include_path_regex: str | None = None,
) -> list[ProbeDefinition]:
    """Generate probes from spec for POST operations that declare no arguments."""
    payload = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Spec payload is not a JSON object.")
    paths = payload.get("paths", {})
    if not isinstance(paths, dict):
        raise ValueError("Spec payload is missing a valid 'paths' object.")

    components = payload.get("components", {})
    components_dict = components if isinstance(components, dict) else {}
    path_pattern = re.compile(include_path_regex) if include_path_regex else None

    probes: list[ProbeDefinition] = []
    for path, path_item in sorted(paths.items()):
        if not isinstance(path, str) or not isinstance(path_item, dict):
            continue
        if path_pattern and not path_pattern.search(path):
            continue

        operation = path_item.get("post")
        if not isinstance(operation, dict):
            continue
        if _operation_has_documented_arguments(path_item, operation, components_dict):
            continue

        probes.append(
            ProbeDefinition(
                name=_autogenerated_probe_name(path),
                path=path,
                payload={},
                risk=_risk_from_path(path),
                notes="Autogenerated from spec: POST endpoint with no documented arguments.",
            )
        )

    return probes


def _load_empty_property_post_probes_from_spec(
    spec_path: str | Path,
    include_path_regex: str | None = None,
) -> list[ProbeDefinition]:
    """Generate probes from spec for POST operations with empty JSON request schemas."""
    payload = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Spec payload is not a JSON object.")
    paths = payload.get("paths", {})
    if not isinstance(paths, dict):
        raise ValueError("Spec payload is missing a valid 'paths' object.")

    components = payload.get("components", {})
    components_dict = components if isinstance(components, dict) else {}
    path_pattern = re.compile(include_path_regex) if include_path_regex else None

    probes: list[ProbeDefinition] = []
    for path, path_item in sorted(paths.items()):
        if not isinstance(path, str) or not isinstance(path_item, dict):
            continue
        if path_pattern and not path_pattern.search(path):
            continue

        operation = path_item.get("post")
        if not isinstance(operation, dict):
            continue
        if not _operation_has_empty_json_schema(path_item, operation, components_dict):
            continue

        probes.append(
            ProbeDefinition(
                name=_autogenerated_probe_name(path),
                path=path,
                payload={},
                risk=_risk_from_path(path),
                notes=(
                    "Autogenerated from spec: POST endpoint has application/json schema "
                    "with no properties/required fields."
                ),
            )
        )

    return probes


def _dedupe_probes(probes: list[ProbeDefinition]) -> list[ProbeDefinition]:
    """Deduplicate probes by (name, path), preserving first-seen ordering."""
    seen: set[tuple[str, str]] = set()
    deduped: list[ProbeDefinition] = []
    for probe in probes:
        key = (probe.name, probe.path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(probe)
    return deduped


def _selected_probe_preview(probes: list[ProbeDefinition]) -> list[dict[str, Any]]:
    """Return compact preview rows for selected probes."""
    return [
        {
            "name": probe.name,
            "path": probe.path,
            "risk": probe.risk,
            "enabled": probe.enabled,
            "notes": probe.notes,
        }
        for probe in probes
    ]


def _export_selected_probes(
    output_path: str | Path,
    probes: list[ProbeDefinition],
) -> None:
    """Write selected probe preview rows to JSON or CSV based on the file suffix."""
    path = Path(output_path)
    preview_rows = _selected_probe_preview(probes)

    if path.suffix.lower() == ".csv":
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["name", "path", "risk", "enabled", "notes"],
            )
            writer.writeheader()
            writer.writerows(preview_rows)
        return

    payload = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "count": len(preview_rows),
        "probes": preview_rows,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _load_probe_plan(
    plan_path: str | Path,
) -> tuple[list[ProbeDefinition], dict[str, str]]:
    """Load and validate probe plan JSON into typed probe definitions."""
    path = Path(plan_path)
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, dict):
        raise ValueError("Probe plan root must be a JSON object.")

    raw_probes = raw.get("probes")
    if not isinstance(raw_probes, list):
        raise ValueError("Probe plan must include a 'probes' list.")

    default_headers_raw = raw.get("default_headers", {})
    if not isinstance(default_headers_raw, dict):
        raise ValueError("default_headers must be an object when provided.")
    default_headers = {str(k): str(v) for k, v in default_headers_raw.items()}

    probes: list[ProbeDefinition] = []
    for idx, probe in enumerate(raw_probes):
        if not isinstance(probe, dict):
            raise ValueError(f"Probe #{idx + 1} must be an object.")

        name = str(probe.get("name", "")).strip()
        path_value = str(probe.get("path", "")).strip()
        if not name:
            raise ValueError(f"Probe #{idx + 1} is missing 'name'.")
        if not path_value.startswith("/"):
            raise ValueError(f"Probe '{name}' must have a '/'-prefixed path.")

        payload_raw = probe.get("payload", {})
        if not isinstance(payload_raw, dict):
            raise ValueError(f"Probe '{name}' payload must be an object.")

        risk = str(probe.get("risk", "medium")).strip().lower()
        if risk not in _ALLOWED_RISKS:
            raise ValueError(
                f"Probe '{name}' has invalid risk '{risk}'. Expected one of {_ALLOWED_RISKS}."
            )

        headers_raw = probe.get("headers")
        headers: dict[str, str] | None = None
        if headers_raw is not None:
            if not isinstance(headers_raw, dict):
                raise ValueError(f"Probe '{name}' headers must be an object.")
            headers = {str(k): str(v) for k, v in headers_raw.items()}

        probes.append(
            ProbeDefinition(
                name=name,
                path=path_value,
                payload=payload_raw,
                risk=risk,
                headers=headers,
                notes=(str(probe.get("notes")) if probe.get("notes") else None),
                enabled=bool(probe.get("enabled", True)),
            )
        )

    return probes, default_headers


def _extract_messages(response_payload: Any) -> list[str]:
    """Extract readable API error messages from varied response payload shapes."""
    if response_payload is None:
        return []

    if isinstance(response_payload, str):
        text = response_payload.strip()
        return [text] if text else []

    if isinstance(response_payload, list):
        output: list[str] = []
        for item in response_payload:
            output.extend(_extract_messages(item))
        return output

    if isinstance(response_payload, dict):
        output = []
        for key in ("message", "messages", "error", "errors", "detail", "title"):
            if key in response_payload:
                output.extend(_extract_messages(response_payload.get(key)))
        if not output:
            output.append(str(response_payload))
        return output

    return [str(response_payload)]


def _infer_required_fields(messages: list[str]) -> list[str]:
    """Infer required field names from common API validation message patterns."""
    patterns = [
        re.compile(
            r"(?:field|parameter)\s+'?([a-zA-Z0-9_.-]+)'?\s+is\s+required", re.I
        ),
        re.compile(
            r"missing\s+required\s+(?:field|parameter)s?\s*:?\s*([a-zA-Z0-9_,\s.-]+)",
            re.I,
        ),
        re.compile(r"'([a-zA-Z0-9_.-]+)'\s+must\s+be\s+provided", re.I),
        re.compile(r"'([a-zA-Z0-9_.-]+)'\s+cannot\s+be\s+null", re.I),
    ]

    fields: set[str] = set()
    for message in messages:
        for pattern in patterns:
            for match in pattern.findall(message):
                if isinstance(match, tuple):
                    token = " ".join(part for part in match if part)
                else:
                    token = match
                for candidate in re.split(r"\s*,\s*", token.strip()):
                    cleaned = candidate.strip(" .")
                    if cleaned:
                        fields.add(cleaned)

    return sorted(fields)


def _classify_outcome(
    status_code: int | None,
    json_payload: Any = None,
    dry_run: bool = False,
) -> str:
    """Classify probe result status into review-friendly outcome buckets.

    BriteCore APIs return HTTP 200 for both genuine success and business-logic
    failures (``{"success": false, "message": "..."}``) so we must inspect the
    body when available to distinguish the two cases.

    Outcomes:
        genuine_success     — 200 + success:true (endpoint truly needs no args)
        informative_error   — 200 + success:false (API reports required fields)
                              or 400/404/409/422 (standard HTTP validation error)
        unexpected_success  — 200 but body has unknown or non-BriteCore shape
        auth_error          — 401/403
        rate_limited        — 429
        server_error        — 5xx
        transport_error     — network/timeout
        dry_run_success     — SDK dry-run response (not a real API call)
    """
    if status_code is None:
        return "transport_error"

    if 200 <= status_code < 300:
        if dry_run:
            return "dry_run_success"
        if isinstance(json_payload, dict):
            success_flag = json_payload.get("success")
            if success_flag is True:
                return "genuine_success"
            if success_flag is False:
                return "informative_error"
        return "unexpected_success"

    if status_code in {400, 404, 409, 422}:
        return "informative_error"
    if status_code in {401, 403}:
        return "auth_error"
    if status_code == 429:
        return "rate_limited"
    if status_code >= 500:
        return "server_error"
    return "other_error"


def _decode_json_response(data: bytes | None) -> Any:
    """Decode JSON response body when available; otherwise return None."""
    if not data:
        return None
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _run_probe(
    client: _SupportsDoRequest,
    probe: ProbeDefinition,
    default_headers: dict[str, str],
    timeout_seconds: float,
    dry_run: bool,
) -> ProbeResult:
    """Execute one probe request and normalize the response into a result object."""
    merged_headers = dict(default_headers)
    if probe.headers:
        merged_headers.update(probe.headers)

    try:
        response = client.do_request(
            path=probe.path,
            json=probe.payload,
            method="POST",
            request_headers=merged_headers,
            request_timeout=timeout_seconds,
            dry_run=dry_run,
        )
    except BritecoreError.Base as exc:
        return ProbeResult(
            name=probe.name,
            path=probe.path,
            risk=probe.risk,
            outcome="transport_error",
            status_code=None,
            request_id=getattr(exc, "request_id", None),
            messages=[str(exc)],
            inferred_required_fields=[],
            notes=probe.notes,
        )

    if response is None:
        return ProbeResult(
            name=probe.name,
            path=probe.path,
            risk=probe.risk,
            outcome="transport_error",
            status_code=None,
            request_id=None,
            messages=["No response object returned by do_request()."],
            inferred_required_fields=[],
            notes=probe.notes,
        )

    payload = _decode_json_response(response.data)
    messages = _extract_messages(payload)
    request_id = response.headers.get("X-SDK-Request-ID") if response.headers else None
    outcome = _classify_outcome(response.status, json_payload=payload, dry_run=dry_run)
    return ProbeResult(
        name=probe.name,
        path=probe.path,
        risk=probe.risk,
        outcome=outcome,
        status_code=response.status,
        request_id=request_id,
        messages=messages,
        inferred_required_fields=_infer_required_fields(messages),
        notes=probe.notes,
    )


def _build_client(args: argparse.Namespace) -> BritecoreAPIClient:
    """Initialize an API client from site config or explicit credentials."""
    if args.base_url:
        return init_api_client(
            target_site=args.site,
            base_url=args.base_url,
            api_key=args.api_key,
            client_id=args.client_id,
            client_secret=args.client_secret,
        )

    if not args.site:
        raise ValueError("--site is required unless --base-url is provided.")
    return init_api_client(target_site=args.site)


def _render_markdown(report: dict[str, Any]) -> str:
    """Render a compact markdown report for manual endpoint contract review."""
    lines = [
        "# POST Probe Report",
        "",
        f"- Generated: {report['generated_at_utc']}",
        f"- Site: {report['site']}",
        f"- Dry run: {report['dry_run']}",
        f"- Probes total: {report['counts']['total']}",
        f"- Genuine success (no args needed): {report['counts']['genuine_success']}",
        f"- Informative errors (args discovered): {report['counts']['informative_error']}",
        f"- Unexpected success (unknown body): {report['counts']['unexpected_success']}",
        f"- Dry-run responses: {report['counts']['dry_run_success']}",
        f"- Auth errors: {report['counts']['auth_error']}",
        f"- Server errors: {report['counts']['server_error']}",
        f"- Transport errors (timeout/network): {report['counts']['transport_error']}",
        f"- Skipped (risk): {report['counts']['skipped_risk']}",
        "",
        "## Results",
        "",
    ]

    for result in report["results"]:
        lines.extend(
            [
                f"### {result['name']}",
                f"- Path: `{result['path']}`",
                f"- Outcome: `{result['outcome']}`",
                f"- Status: `{result['status_code']}`",
                f"- Request ID: `{result['request_id']}`",
                f"- Inferred required fields: {', '.join(result['inferred_required_fields']) or '(none)'}",
            ]
        )
        if result["notes"]:
            lines.append(f"- Notes: {result['notes']}")
        if result["messages"]:
            lines.append("- Messages:")
            for message in result["messages"]:
                lines.append(f"  - {message}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """Run POST probes from a plan file and emit JSON/Markdown reports."""
    args = _parse_args(argv)

    # Always attach a console handler for the CLI tool so progress is visible.
    # We skip this only when the caller already has a non-NullHandler set up.
    _real_handlers = [
        h for h in LOGGER.handlers if not isinstance(h, logging.NullHandler)
    ]
    _root_real_handlers = [
        h
        for h in logging.getLogger().handlers
        if not isinstance(h, logging.NullHandler)
    ]
    if not _real_handlers and not _root_real_handlers:
        _cli_handler = logging.StreamHandler()
        _cli_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        LOGGER.addHandler(_cli_handler)
    LOGGER.setLevel(getattr(logging, args.log_level, logging.INFO))
    probes: list[ProbeDefinition] = []
    default_headers: dict[str, str] = {}

    if args.plan:
        LOGGER.info("Loading probe plan from: %s", args.plan)
        plan_probes, plan_headers = _load_probe_plan(args.plan)
        probes.extend(plan_probes)
        default_headers.update(plan_headers)
        LOGGER.info("Loaded %d probe(s) from plan.", len(plan_probes))

    if args.use_spec_no_args:
        LOGGER.info(
            "Scanning spec for POST operations with no documented arguments: %s",
            args.spec_path,
        )
        spec_probes = _load_no_arg_post_probes_from_spec(
            spec_path=args.spec_path,
            include_path_regex=args.include_path_regex,
        )
        probes.extend(spec_probes)
        LOGGER.info("Selected %d probe(s) via --use-spec-no-args.", len(spec_probes))

    if args.use_spec_empty_properties:
        LOGGER.info(
            "Scanning spec for POST operations with empty JSON schema: %s",
            args.spec_path,
        )
        spec_probes = _load_empty_property_post_probes_from_spec(
            spec_path=args.spec_path,
            include_path_regex=args.include_path_regex,
        )
        probes.extend(spec_probes)
        LOGGER.info(
            "Selected %d probe(s) via --use-spec-empty-properties.", len(spec_probes)
        )

    probes = _dedupe_probes(probes)
    if args.max_probes is not None:
        probes = probes[: args.max_probes]

    LOGGER.info("Total resolved probes after dedup/limit: %d", len(probes))

    if args.write_generated_plan:
        generated_plan = {
            "default_headers": default_headers,
            "probes": [asdict(probe) for probe in probes],
        }
        Path(args.write_generated_plan).write_text(
            json.dumps(generated_plan, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        LOGGER.info("Wrote generated probe plan: %s", args.write_generated_plan)

    if args.export_selected_paths:
        _export_selected_probes(args.export_selected_paths, probes)
        LOGGER.info(
            "Wrote selected probe preview (%d): %s",
            len(probes),
            args.export_selected_paths,
        )
        print(f"Wrote selected probe preview: {args.export_selected_paths}")
        return 0

    if args.print_selected_paths:
        print("Resolved probes:")
        for probe in probes:
            enabled = "enabled" if probe.enabled else "disabled"
            print(f"- {probe.path} [{probe.risk}, {enabled}] ({probe.name})")
        print(f"Total resolved probes: {len(probes)}")
        return 0

    results: list[ProbeResult] = []
    if probes:
        LOGGER.info("Initializing API client for site: %s", args.site or "explicit")
        client = _build_client(args)
        total = len(probes)
        for idx, probe in enumerate(probes, start=1):
            if not probe.enabled:
                LOGGER.debug(
                    "[%d/%d] Skipping disabled probe: %s", idx, total, probe.path
                )
                continue
            if probe.risk == "high" and not args.allow_high_risk:
                LOGGER.info(
                    "[%d/%d] SKIPPED (high-risk, --allow-high-risk not set): %s",
                    idx,
                    total,
                    probe.path,
                )
                results.append(
                    ProbeResult(
                        name=probe.name,
                        path=probe.path,
                        risk=probe.risk,
                        outcome="skipped_risk",
                        status_code=None,
                        request_id=None,
                        messages=[
                            "Probe skipped because risk=high and --allow-high-risk was not set."
                        ],
                        inferred_required_fields=[],
                        notes=probe.notes,
                    )
                )
                continue

            LOGGER.info(
                "[%d/%d] Probing POST %s (risk=%s)%s",
                idx,
                total,
                probe.path,
                probe.risk,
                " [dry-run]" if args.dry_run else "",
            )
            result = _run_probe(
                client=client,
                probe=probe,
                default_headers=default_headers,
                timeout_seconds=args.timeout_seconds,
                dry_run=args.dry_run,
            )
            _outcome_log = (
                LOGGER.warning
                if result.outcome in {"unexpected_success", "server_error"}
                else LOGGER.info
            )
            _outcome_log(
                "[%d/%d] -> %s  status=%s  outcome=%s",
                idx,
                total,
                probe.path,
                result.status_code,
                result.outcome
                + (
                    "  inferred_fields=" + str(result.inferred_required_fields)
                    if result.inferred_required_fields
                    else ""
                ),
            )
            results.append(result)

    counts = {
        "total": len(results),
        "genuine_success": sum(1 for r in results if r.outcome == "genuine_success"),
        "dry_run_success": sum(1 for r in results if r.outcome == "dry_run_success"),
        "informative_error": sum(
            1 for r in results if r.outcome == "informative_error"
        ),
        "unexpected_success": sum(
            1 for r in results if r.outcome == "unexpected_success"
        ),
        "auth_error": sum(1 for r in results if r.outcome == "auth_error"),
        "rate_limited": sum(1 for r in results if r.outcome == "rate_limited"),
        "server_error": sum(1 for r in results if r.outcome == "server_error"),
        "transport_error": sum(1 for r in results if r.outcome == "transport_error"),
        "skipped_risk": sum(1 for r in results if r.outcome == "skipped_risk"),
    }

    report: dict[str, Any] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "site": args.site or "explicit",
        "dry_run": bool(args.dry_run),
        "plan": str(Path(args.plan).resolve()) if args.plan else None,
        "spec_path": (
            str(Path(args.spec_path).resolve())
            if (args.use_spec_no_args or args.use_spec_empty_properties)
            else None
        ),
        "generated_from_spec_no_args": bool(args.use_spec_no_args),
        "generated_from_spec_empty_properties": bool(args.use_spec_empty_properties),
        "counts": counts,
        "results": [asdict(item) for item in results],
    }

    output_json = Path(args.output_json)
    output_json.write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    LOGGER.info("Wrote JSON report: %s", output_json)

    output_markdown = Path(args.output_markdown)
    output_markdown.write_text(_render_markdown(report), encoding="utf-8")
    LOGGER.info("Wrote Markdown report: %s", output_markdown)

    print(f"Wrote JSON report: {output_json}")
    print(f"Wrote Markdown report: {output_markdown}")
    if not probes:
        print("No probes resolved from plan/spec filters.")
        return 0
    print(
        "Summary: "
        f"genuine_success={counts['genuine_success']} "
        f"informative={counts['informative_error']} "
        f"unexpected={counts['unexpected_success']} "
        f"auth_error={counts['auth_error']} "
        f"server_error={counts['server_error']} "
        f"timeout={counts['transport_error']} "
        f"skipped={counts['skipped_risk']}"
    )

    blocking_outcomes = {"unexpected_success", "server_error"}
    has_blocking = any(result.outcome in blocking_outcomes for result in results)
    if has_blocking:
        LOGGER.warning(
            "Run completed with blocking outcomes — review report: %s", output_json
        )
    else:
        LOGGER.info("Run completed cleanly.")
    return 1 if has_blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
