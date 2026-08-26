"""Unit tests for TOML compatibility helpers."""

from __future__ import annotations

import builtins
from io import BytesIO, StringIO
from types import SimpleNamespace

import pytest

from britecore_sdk.utils.toml_compat import toml


@pytest.fixture()
def import_hook_factory(monkeypatch: pytest.MonkeyPatch):
    """Install a temporary import hook for tomli_w/toml fallback testing."""

    def _install(*, fail_tomli_w: bool, provide_legacy: bool = True) -> None:
        real_import = builtins.__import__

        def legacy_dump(data: dict[str, object], destination: object) -> None:
            destination.write("value = 1\n")

        legacy_module = SimpleNamespace(dump=legacy_dump, dumps=lambda _: "value = 1\n")

        def fake_import(name: str, globals=None, locals=None, fromlist=(), level=0):
            if name == "tomli_w" and fail_tomli_w:
                raise ImportError("mock tomli_w import failure")
            if name == "toml":
                if provide_legacy:
                    return legacy_module
                raise ImportError("mock legacy toml import failure")
            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", fake_import)

    return _install


def test_loads_accepts_text_and_bytes() -> None:
    parsed_text = toml.loads("value = 1")
    parsed_bytes = toml.loads(b"value = 1")

    assert parsed_text["value"] == 1
    assert parsed_bytes["value"] == 1


def test_dumps_with_tomli_w_installed() -> None:
    serialized = toml.dumps({"value": 1})

    assert "value = 1" in serialized


def test_dumps_uses_legacy_fallback_when_tomli_w_missing(
    import_hook_factory,
) -> None:
    import_hook_factory(fail_tomli_w=True)

    serialized = toml.dumps({"value": 1})

    assert serialized == "value = 1\n"


def test_load_from_text_stream() -> None:
    stream = StringIO("value = 1")

    parsed = toml.load(stream)

    assert parsed["value"] == 1


def test_load_from_binary_stream() -> None:
    stream = BytesIO(b"value = 1")

    parsed = toml.load(stream)

    assert parsed["value"] == 1


def test_dump_to_binary_stream_uses_tomli_w_path() -> None:
    stream = BytesIO()

    toml.dump({"value": 1}, stream)

    assert b"value = 1" in stream.getvalue()


def test_dump_to_binary_stream_uses_legacy_fallback(
    import_hook_factory,
) -> None:
    import_hook_factory(fail_tomli_w=True)

    stream = BytesIO()
    toml.dump({"value": 1}, stream)

    assert b"value = 1" in stream.getvalue()


def test_dump_to_text_stream_with_buffer_uses_tomli_w_path(tmp_path) -> None:
    target = tmp_path / "settings.toml"
    with open(target, "w", encoding="utf-8") as handle:
        toml.dump({"value": 1}, handle)

    assert "value = 1" in target.read_text(encoding="utf-8")


def test_dump_falls_back_to_legacy_for_text_stream_without_buffer(
    import_hook_factory,
) -> None:
    import_hook_factory(fail_tomli_w=False, provide_legacy=True)

    stream = StringIO()
    toml.dump({"value": 1}, stream)

    assert stream.getvalue() == "value = 1\n"


def test_dumps_raises_runtime_error_when_no_writer_available(
    import_hook_factory,
) -> None:
    import_hook_factory(fail_tomli_w=True, provide_legacy=False)

    with pytest.raises(RuntimeError, match="TOML writing support is unavailable"):
        toml.dumps({"value": 1})


def test_dump_raises_runtime_error_when_no_writer_available(
    import_hook_factory,
) -> None:
    import_hook_factory(fail_tomli_w=True, provide_legacy=False)

    with pytest.raises(RuntimeError, match="TOML writing support is unavailable"):
        toml.dump({"value": 1}, StringIO())
