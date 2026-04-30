"""Unit tests for stitched line file extract helpers (sync + async)."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest


_LINES = [
    ("EFF-001", "ST-001", "LN-001"),
    ("EFF-002", "ST-002", "LN-002"),
    ("EFF-003", "ST-003", "LN-003"),
]


class TestStitchedLineExtractSync:
    """Tests for get_export_line_files_stitched (sync)."""

    @pytest.mark.unit
    def test_stitched_all_succeed(self):
        """All line extracts succeed and are present in results."""
        from britecore_sdk.api.api_calls.v2 import lines

        def _mock_extract(line, include_custom_sequences=False, **kwargs):
            return {"line_data": line[2], "items": []}

        with patch.object(lines, "get_export_line_file", side_effect=_mock_extract):
            result = lines.get_export_line_files_stitched(
                _LINES, max_workers=2
            )

        assert result["total"] == 3
        assert result["succeeded"] == 3
        assert result["failed"] == 0
        for item in result["results"]:
            assert item["success"] is True
            assert item["data"] is not None
            assert item["error"] is None

    @pytest.mark.unit
    def test_stitched_partial_failure(self):
        """A single-line failure is captured without aborting others."""
        from britecore_sdk.api.api_calls.v2 import lines

        call_count = {"n": 0}

        def _mock_extract(line, include_custom_sequences=False, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise RuntimeError("extract timeout")
            return {"line_data": line[2]}

        with patch.object(lines, "get_export_line_file", side_effect=_mock_extract):
            result = lines.get_export_line_files_stitched(
                _LINES, max_workers=1  # serial to make call_count predictable
            )

        assert result["total"] == 3
        assert result["succeeded"] == 2
        assert result["failed"] == 1
        failed = next(i for i in result["results"] if not i["success"])
        assert "extract timeout" in failed["error"]

    @pytest.mark.unit
    def test_stitched_invalid_inputs(self):
        """Raises on missing or empty lines list."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.api_calls.v2 import lines

        with pytest.raises(BritecoreError.MissingParameter):
            lines.get_export_line_files_stitched([])

        with pytest.raises(ValueError):
            lines.get_export_line_files_stitched(_LINES, max_workers=0)

    @pytest.mark.unit
    def test_stitched_results_include_line_tuple(self):
        """Each result item carries the original line tuple for traceability."""
        from britecore_sdk.api.api_calls.v2 import lines

        def _mock_extract(line, **kwargs):
            return {"data": True}

        with patch.object(lines, "get_export_line_file", side_effect=_mock_extract):
            result = lines.get_export_line_files_stitched(
                _LINES[:1], max_workers=1
            )

        assert result["results"][0]["line"] == _LINES[0]


class TestStitchedLineExtractAsync:
    """Tests for aget_export_line_files_stitched (async)."""

    @pytest.mark.unit
    def test_async_stitched_all_succeed(self):
        """Async stitching returns all line extracts on success."""
        from britecore_sdk.api.api_calls.v2 import async_lines

        async def _mock_extract(line, include_custom_sequences=False, **kwargs):
            return {"line_data": line[2]}

        async def _run():
            with patch.object(
                async_lines,
                "aget_export_line_file",
                new_callable=AsyncMock,
                side_effect=_mock_extract,
            ):
                result = await async_lines.aget_export_line_files_stitched(
                    _LINES, max_concurrent=2
                )

            assert result["total"] == 3
            assert result["succeeded"] == 3
            assert result["failed"] == 0

        asyncio.run(_run())

    @pytest.mark.unit
    def test_async_stitched_partial_failure(self):
        """Async stitching captures single-line failures without aborting others."""
        from britecore_sdk.api.api_calls.v2 import async_lines

        call_count = {"n": 0}

        async def _mock_extract(line, include_custom_sequences=False, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("async extract timeout")
            return {"line_data": line[2]}

        async def _run():
            with patch.object(
                async_lines,
                "aget_export_line_file",
                new_callable=AsyncMock,
                side_effect=_mock_extract,
            ):
                result = await async_lines.aget_export_line_files_stitched(
                    _LINES, max_concurrent=3
                )

            assert result["total"] == 3
            assert result["failed"] >= 1
            failed = [i for i in result["results"] if not i["success"]]
            assert len(failed) >= 1
            assert "async extract timeout" in failed[0]["error"]

        asyncio.run(_run())

    @pytest.mark.unit
    def test_async_stitched_invalid_inputs(self):
        """Async helper raises on missing or empty lines list."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.api_calls.v2 import async_lines

        async def _run():
            with pytest.raises(BritecoreError.MissingParameter):
                await async_lines.aget_export_line_files_stitched([])
            with pytest.raises(ValueError):
                await async_lines.aget_export_line_files_stitched(
                    _LINES, max_concurrent=0
                )

        asyncio.run(_run())
