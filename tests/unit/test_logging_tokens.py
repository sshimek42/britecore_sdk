"""Regression tests to ensure legacy SCLogging tokens are fully removed."""

from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path

from britecore_libraries.api.api_calls.v2 import async_contacts, contacts, deliverables

TOKEN_PATTERN = re.compile(r"%[fbs](?:\.[^%\n]+)?%")


def test_no_legacy_logging_tokens_in_source_tree() -> None:
    """Source files under src should not contain legacy SCLogging token markup."""
    repo_root = Path(__file__).resolve().parents[2]
    source_root = repo_root / "src" / "britecore_libraries"

    offending: list[str] = []
    excluded_parts = {"build", "dist", "env"}

    for path in source_root.rglob("*.py"):
        if excluded_parts.intersection(path.parts):
            continue
        if any(part.endswith(".egg-info") for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if TOKEN_PATTERN.search(text):
            offending.append(str(path.relative_to(repo_root)))

    assert not offending, f"Found legacy logging tokens in: {offending}"


def test_runtime_logs_do_not_emit_legacy_tokens(caplog) -> None:
    """Representative sync and async endpoint logs should emit plain text only."""

    class DummySyncClient:
        def do_request(self, *args, **kwargs):
            return object()

        def process_result(self, *args, **kwargs):
            return {"contact_id": "abc123", "ok": True}

    class DummyAsyncClient:
        async def ado_request(self, *args, **kwargs):
            return object()

        async def aprocess_result(self, *args, **kwargs):
            return {"contact_id": "abc123", "ok": True}

    sync_client_original = contacts.API_CLIENT
    async_client_original = async_contacts.API_CLIENT
    deliverables_client_original = deliverables.API_CLIENT

    contacts.API_CLIENT = DummySyncClient()
    async_contacts.API_CLIENT = DummyAsyncClient()
    deliverables.API_CLIENT = DummySyncClient()

    try:
        with caplog.at_level(logging.DEBUG, logger="britecore_libraries"):
            contacts.new_contact(name="Jane Doe", address=[{"line1": "x"}])
            deliverables.get_attachment("file-1")
            asyncio.run(async_contacts.anew_contact(name="Alex Roe", address=[{"line1": "y"}]))

        messages = [record.getMessage() for record in caplog.records]
        assert messages, "Expected captured log messages but got none"
        assert all(not TOKEN_PATTERN.search(m) for m in messages), messages
    finally:
        contacts.API_CLIENT = sync_client_original
        async_contacts.API_CLIENT = async_client_original
        deliverables.API_CLIENT = deliverables_client_original


