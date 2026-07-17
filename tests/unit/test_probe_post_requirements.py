"""Unit tests for utils/probe_post_requirements.py."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest

from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.exceptions import BritecoreError
from britecore_sdk.utils import probe_post_requirements as probe


@pytest.mark.unit
def test_load_probe_plan_validates_required_fields(tmp_path: Path) -> None:
    """Plan loader raises clear errors when required fields are missing."""
    bad_plan = tmp_path / "bad_plan.json"
    bad_plan.write_text(json.dumps({"probes": [{"path": "/api/v2/test"}]}), encoding="utf-8")

    with pytest.raises(ValueError, match="missing 'name'"):
        probe._load_probe_plan(bad_plan)


@pytest.mark.unit
def test_load_probe_plan_returns_typed_probes_and_default_headers(tmp_path: Path) -> None:
    """Plan loader returns ProbeDefinition objects and normalized header values."""
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "default_headers": {"X-Probe": "yes", "X-Run": 123},
                "probes": [
                    {
                        "name": "create_quote_invalid",
                        "path": "/api/v2/quotes/create_quote",
                        "payload": {"quote_number": ""},
                        "risk": "medium",
                        "headers": {"X-Endpoint": "quotes"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    probes, default_headers = probe._load_probe_plan(plan)

    assert default_headers == {"X-Probe": "yes", "X-Run": "123"}
    assert len(probes) == 1
    assert probes[0].name == "create_quote_invalid"
    assert probes[0].headers == {"X-Endpoint": "quotes"}


@pytest.mark.unit
def test_infer_required_fields_extracts_common_validation_patterns() -> None:
    """Field inference extracts likely required field names from error messages."""
    messages = [
        "Field 'policy_id' is required",
        "Missing required fields: quote_number, insured_name",
        "'revision_id' must be provided",
    ]

    inferred = probe._infer_required_fields(messages)

    assert inferred == ["insured_name", "policy_id", "quote_number", "revision_id"]


@pytest.mark.unit
def test_run_probe_classifies_validation_error_and_extracts_request_id() -> None:
    """Probe runner classifies 400-style responses as informative errors."""

    class _DummyResponse:
        status = 400
        headers = {"X-SDK-Request-ID": "abc12345"}
        data = b'{"message":"Field \'quote_number\' is required"}'

    class _DummyClient:
        def do_request(self, **kwargs):
            assert kwargs["method"] == "POST"
            return _DummyResponse()

    result = probe._run_probe(
        client=cast(BritecoreAPIClient, _DummyClient()),
        probe=probe.ProbeDefinition(
            name="quote_probe",
            path="/api/v2/quotes/create_quote",
            payload={},
            risk="medium",
        ),
        default_headers={"X-Probe": "yes"},
        timeout_seconds=5.0,
        dry_run=False,
    )

    assert result.outcome == "informative_error"
    assert result.status_code == 400
    assert result.request_id == "abc12345"
    assert result.inferred_required_fields == ["quote_number"]


@pytest.mark.unit
def test_run_probe_classifies_britecore_success_false_as_informative_error() -> None:
    """BriteCore HTTP 200 with success:false body should be informative_error."""

    class _DummyResponse:
        status = 200
        headers = {"X-SDK-Request-ID": "def67890"}
        data = b'{"success": false, "message": "Field \'quote_id\' is required"}'

    class _DummyClient:
        def do_request(self, **kwargs):
            return _DummyResponse()

    result = probe._run_probe(
        client=cast(BritecoreAPIClient, _DummyClient()),
        probe=probe.ProbeDefinition(
            name="get_quote_probe",
            path="/api/v2/quotes/get_quote",
            payload={},
            risk="medium",
        ),
        default_headers={},
        timeout_seconds=5.0,
        dry_run=False,
    )

    assert result.outcome == "informative_error"
    assert result.status_code == 200
    assert result.inferred_required_fields == ["quote_id"]


@pytest.mark.unit
def test_run_probe_classifies_britecore_success_true_as_genuine_success() -> None:
    """BriteCore HTTP 200 with success:true body should be genuine_success."""

    class _DummyResponse:
        status = 200
        headers = {"X-SDK-Request-ID": "aaa11111"}
        data = b'{"success": true, "data": {"release": "1.0.0"}}'

    class _DummyClient:
        def do_request(self, **kwargs):
            return _DummyResponse()

    result = probe._run_probe(
        client=cast(BritecoreAPIClient, _DummyClient()),
        probe=probe.ProbeDefinition(
            name="release_probe",
            path="/api/v2/utils/get_release_info",
            payload={},
            risk="low",
        ),
        default_headers={},
        timeout_seconds=5.0,
        dry_run=False,
    )

    assert result.outcome == "genuine_success"
    assert result.status_code == 200
    assert result.inferred_required_fields == []


@pytest.mark.unit
def test_run_probe_classifies_dry_run_response_as_dry_run_success() -> None:
    """SDK dry-run response (success:true from envelope) is classified separately."""

    class _DummyResponse:
        status = 200
        headers = {"X-SDK-Request-ID": "bbb22222", "X-SDK-Dry-Run": "true"}
        data = b'{"success": true, "data": {"dry_run": true}}'

    class _DummyClient:
        def do_request(self, **kwargs):
            return _DummyResponse()

    result = probe._run_probe(
        client=cast(BritecoreAPIClient, _DummyClient()),
        probe=probe.ProbeDefinition(
            name="dry_probe",
            path="/api/v2/utils/ping",
            payload={},
            risk="low",
        ),
        default_headers={},
        timeout_seconds=5.0,
        dry_run=True,
    )

    assert result.outcome == "dry_run_success"


@pytest.mark.unit
def test_main_skips_high_risk_without_flag_and_writes_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """main() skips high-risk probes by default and writes both report files."""
    plan_path = tmp_path / "plan.json"
    json_path = tmp_path / "report.json"
    md_path = tmp_path / "report.md"

    plan_path.write_text(
        json.dumps(
            {
                "probes": [
                    {
                        "name": "trigger_bind",
                        "path": "/api/v2/policies/bind",
                        "payload": {},
                        "risk": "high",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    class _DummyClient:
        def do_request(self, **kwargs):
            raise AssertionError("High-risk probe should be skipped before do_request")

    monkeypatch.setattr(probe, "init_api_client", lambda **kwargs: _DummyClient())

    exit_code = probe.main(
        [
            "--plan",
            str(plan_path),
            "--site",
            "dev",
            "--output-json",
            str(json_path),
            "--output-markdown",
            str(md_path),
        ]
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["counts"]["skipped_risk"] == 1
    assert payload["results"][0]["outcome"] == "skipped_risk"
    assert "trigger_bind" in markdown


@pytest.mark.unit
def test_main_returns_nonzero_for_unexpected_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """main() returns non-zero when a probe gets 200 with unknown (non-BriteCore) body."""
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "probes": [
                    {
                        "name": "unknown_endpoint",
                        "path": "/api/v2/contacts/create_contact",
                        "payload": {},
                        "risk": "low",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    class _DummyResponse:
        status = 200
        headers = {"X-SDK-Request-ID": "ok123456"}
        # No "success" key → unknown shape → unexpected_success
        data = b'{"result": "ok"}'

    class _DummyClient:
        def do_request(self, **kwargs):
            return _DummyResponse()

    monkeypatch.setattr(probe, "init_api_client", lambda **kwargs: _DummyClient())

    exit_code = probe.main(["--plan", str(plan_path), "--site", "dev"])

    assert exit_code == 1


@pytest.mark.unit
def test_load_no_arg_post_probes_from_spec_detects_only_no_arg_posts(
    tmp_path: Path,
) -> None:
    """Spec loader returns only POST operations with no documented request args."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "paths": {
                    "/api/v2/utils/ping": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {}}
                                    }
                                }
                            }
                        }
                    },
                    "/api/v2/quotes/create_quote": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {"quote_number": {"type": "string"}},
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "/api/v2/contacts/{contact_id}/noop": {
                        "parameters": [
                            {
                                "name": "contact_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "post": {},
                    },
                    "/api/v2/test/ref_no_args": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/EmptyPayload"}
                                    }
                                }
                            }
                        }
                    },
                },
                "components": {
                    "schemas": {
                        "EmptyPayload": {"type": "object", "properties": {}}
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    probes = probe._load_no_arg_post_probes_from_spec(spec_path)
    paths = sorted(item.path for item in probes)

    assert paths == ["/api/v2/test/ref_no_args", "/api/v2/utils/ping"]


@pytest.mark.unit
def test_main_can_run_in_spec_no_args_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """main() supports --use-spec-no-args and writes the resolved generated plan."""
    spec_path = tmp_path / "spec.json"
    generated_plan = tmp_path / "generated_plan.json"
    output_json = tmp_path / "report.json"
    output_markdown = tmp_path / "report.md"

    spec_path.write_text(
        json.dumps(
            {
                "paths": {
                    "/api/v2/utils/ping": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {}}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    class _DummyResponse:
        status = 400
        headers = {"X-SDK-Request-ID": "probe123"}
        data = b'{"message":"Field \'foo\' is required"}'

    class _DummyClient:
        def do_request(self, **kwargs):
            return _DummyResponse()

    monkeypatch.setattr(probe, "init_api_client", lambda **kwargs: _DummyClient())

    exit_code = probe.main(
        [
            "--use-spec-no-args",
            "--spec-path",
            str(spec_path),
            "--site",
            "dev",
            "--write-generated-plan",
            str(generated_plan),
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
        ]
    )

    report_payload = json.loads(output_json.read_text(encoding="utf-8"))
    generated_payload = json.loads(generated_plan.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert report_payload["generated_from_spec_no_args"] is True
    assert report_payload["counts"]["informative_error"] == 1
    assert generated_payload["probes"][0]["path"] == "/api/v2/utils/ping"


@pytest.mark.unit
def test_main_handles_no_resolved_spec_probes_gracefully(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """main() writes empty reports when spec filters produce zero probes."""
    spec_path = tmp_path / "spec.json"
    output_json = tmp_path / "report.json"
    output_markdown = tmp_path / "report.md"

    spec_path.write_text(json.dumps({"paths": {"/api/v2/x": {"post": {"parameters": [{}]}}}}), encoding="utf-8")

    monkeypatch.setattr(
        probe,
        "init_api_client",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("client should not initialize")),
    )

    exit_code = probe.main(
        [
            "--use-spec-no-args",
            "--spec-path",
            str(spec_path),
            "--site",
            "dev",
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
        ]
    )

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["counts"]["total"] == 0
    assert payload["results"] == []


@pytest.mark.unit
def test_load_empty_property_post_probes_from_spec_detects_required_empty_body(
    tmp_path: Path,
) -> None:
    """Empty-properties mode includes required-but-empty JSON body contracts."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "paths": {
                    "/api/v2/utils/no_fields": {
                        "post": {
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {}}
                                    }
                                },
                            }
                        }
                    },
                    "/api/v2/utils/has_fields": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {"x": {"type": "string"}},
                                        }
                                    }
                                }
                            }
                        }
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    probes = probe._load_empty_property_post_probes_from_spec(spec_path)
    assert [item.path for item in probes] == ["/api/v2/utils/no_fields"]


@pytest.mark.unit
def test_main_spec_empty_properties_mode_sets_report_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Report includes generated_from_spec_empty_properties when that mode is used."""
    spec_path = tmp_path / "spec.json"
    output_json = tmp_path / "report.json"
    output_markdown = tmp_path / "report.md"

    spec_path.write_text(
        json.dumps(
            {
                "paths": {
                    "/api/v2/utils/no_fields": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {}}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    class _DummyResponse:
        status = 400
        headers = {"X-SDK-Request-ID": "probe-empty"}
        data = b'{"message":"missing required fields: something"}'

    class _DummyClient:
        def do_request(self, **kwargs):
            return _DummyResponse()

    monkeypatch.setattr(probe, "init_api_client", lambda **kwargs: _DummyClient())

    exit_code = probe.main(
        [
            "--use-spec-empty-properties",
            "--spec-path",
            str(spec_path),
            "--site",
            "dev",
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
        ]
    )

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["generated_from_spec_empty_properties"] is True


@pytest.mark.unit
def test_main_print_selected_paths_exits_before_client_init(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Preview mode prints resolved probes and exits before any request execution."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "paths": {
                    "/api/v2/utils/no_fields": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {}}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        probe,
        "init_api_client",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("client should not initialize")),
    )

    exit_code = probe.main(
        [
            "--use-spec-empty-properties",
            "--spec-path",
            str(spec_path),
            "--site",
            "dev",
            "--print-selected-paths",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Resolved probes:" in output
    assert "/api/v2/utils/no_fields" in output


@pytest.mark.unit
def test_export_selected_probes_writes_json_and_csv(tmp_path: Path) -> None:
    """Preview export writes either JSON or CSV depending on file suffix."""
    probes = [
        probe.ProbeDefinition(
            name="probe_one",
            path="/api/v2/utils/no_fields",
            payload={},
            risk="low",
            notes="example",
        )
    ]

    json_path = tmp_path / "selected.json"
    csv_path = tmp_path / "selected.csv"

    probe._export_selected_probes(json_path, probes)
    probe._export_selected_probes(csv_path, probes)

    json_payload = json.loads(json_path.read_text(encoding="utf-8"))
    csv_payload = csv_path.read_text(encoding="utf-8").splitlines()

    assert json_payload["count"] == 1
    assert json_payload["probes"][0]["path"] == "/api/v2/utils/no_fields"
    assert csv_payload[0] == "name,path,risk,enabled,notes"
    assert "/api/v2/utils/no_fields" in csv_payload[1]


@pytest.mark.unit
def test_main_export_selected_paths_exits_before_client_init(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI export mode writes the preview file and skips client setup."""
    spec_path = tmp_path / "spec.json"
    export_path = tmp_path / "selected.csv"

    spec_path.write_text(
        json.dumps(
            {
                "paths": {
                    "/api/v2/utils/no_fields": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {}}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        probe,
        "init_api_client",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("client should not initialize")),
    )

    exit_code = probe.main(
        [
            "--use-spec-empty-properties",
            "--spec-path",
            str(spec_path),
            "--site",
            "dev",
            "--export-selected-paths",
            str(export_path),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Wrote selected probe preview:" in output
    assert export_path.exists()


@pytest.mark.unit
def test_load_no_arg_post_probes_ignores_malformed_request_body(tmp_path: Path) -> None:
    """Selector should safely ignore malformed requestBody values without crashing."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "paths": {
                    "/api/v2/utils/bad_body": {
                        "post": {"requestBody": "invalid"}
                    },
                    "/api/v2/utils/ok_body": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {}}
                                    }
                                }
                            }
                        }
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    probes = probe._load_empty_property_post_probes_from_spec(spec_path)

    assert [item.path for item in probes] == ["/api/v2/utils/ok_body"]


@pytest.mark.unit
def test_main_transport_error_does_not_block_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """transport_error (e.g. timeout) is recorded but does not cause a non-zero exit."""
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "probes": [
                    {
                        "name": "broken_probe",
                        "path": "/api/v2/utils/broken",
                        "payload": {},
                        "risk": "low",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    class _BrokenClient:
        def do_request(self, **kwargs):
            raise BritecoreError.ConfigurationError("boom")

    monkeypatch.setattr(probe, "init_api_client", lambda **kwargs: _BrokenClient())

    exit_code = probe.main(["--plan", str(plan_path), "--site", "dev"])

    # transport_error is informational only — timeouts should not block
    assert exit_code == 0


@pytest.mark.unit
def test_parse_args_rejects_both_preview_modes() -> None:
    """Preview-only modes should be mutually exclusive."""
    with pytest.raises(SystemExit):
        probe._parse_args(
            [
                "--plan",
                "plan.json",
                "--print-selected-paths",
                "--export-selected-paths",
                "selected.json",
            ]
        )


