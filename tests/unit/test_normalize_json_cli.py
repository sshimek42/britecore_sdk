"""Unit tests for the JSON normalization CLI."""

import json

import pytest

from britecore_sdk.cli.normalize_json import main


@pytest.mark.unit
def test_normalize_json_cli_contact_stdout(tmp_path, capsys):
    """CLI prints normalized contact payload to stdout."""
    input_path = tmp_path / "contact.json"
    input_path.write_text(
        json.dumps(
            {
                "name": "acme llc",
                "address": {
                    "address_line1": "123 Main St",
                    "address_city": "Madison",
                    "address_state": "WI",
                    "address_zip": "53703",
                },
                "phone_numbers": [{"phone": "(920) 555-1234", "type": "mobile"}],
                "emails": [{"email": "TEAM@ACME.COM", "type": "work"}],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["--kind", "contact", "--input", str(input_path)])

    assert exit_code == 0
    stdout = capsys.readouterr().out
    normalized = json.loads(stdout)
    assert normalized["name"] == "acme LLC"
    assert normalized["phones"] == [{"phone": "1-920-555-1234", "type": "Cell"}]


@pytest.mark.unit
def test_normalize_json_cli_quote_to_output_file(tmp_path):
    """CLI writes normalized quote payload to an output file."""
    input_path = tmp_path / "quote.json"
    output_path = tmp_path / "quote.normalized.json"
    input_path.write_text(
        json.dumps(
            {
                "number": "Q-001",
                "policy_type_id": "pt-123",
                "agency_id": "agency-1",
                "named_insureds": ["ni-1"],
                "risks": ["risk-1"],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--kind",
            "quote",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--pretty",
        ]
    )

    assert exit_code == 0
    normalized = json.loads(output_path.read_text(encoding="utf-8"))
    assert normalized["number"] == "Q-001"
    assert normalized["policy_type_id"] == "pt-123"


@pytest.mark.unit
def test_normalize_json_cli_invalid_json_returns_error(tmp_path, capsys):
    """CLI returns non-zero and prints a message for invalid JSON input."""
    input_path = tmp_path / "broken.json"
    input_path.write_text("{not-valid-json}", encoding="utf-8")

    exit_code = main(["--kind", "contact", "--input", str(input_path)])

    assert exit_code == 1
    stderr = capsys.readouterr().err
    assert "Invalid JSON" in stderr


@pytest.mark.unit
def test_normalize_json_cli_schema_all_kinds(capsys):
    """Schema mode prints required/optional keys for all payload kinds."""
    exit_code = main(["--schema"])

    assert exit_code == 0
    stdout = capsys.readouterr().out
    schema = json.loads(stdout)
    assert set(schema.keys()) == {"contact", "policy", "quote"}
    assert "required" in schema["contact"]
    assert "optional" in schema["contact"]


@pytest.mark.unit
def test_normalize_json_cli_schema_single_kind(capsys):
    """Schema mode can scope output to one kind."""
    exit_code = main(["--schema", "--kind", "policy"])

    assert exit_code == 0
    stdout = capsys.readouterr().out
    schema = json.loads(stdout)
    assert set(schema.keys()) == {"policy"}
    assert "policy_number" in schema["policy"]["required"]
