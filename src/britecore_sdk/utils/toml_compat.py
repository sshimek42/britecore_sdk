"""Small TOML compatibility wrapper built on Python 3.11+ tomllib.

This keeps a tiny ``toml``-like API (``load``/``dump``/``loads``/``dumps``)
used by SDK utilities while relying on stdlib parsing and ``tomli-w`` for writing.
"""

from __future__ import annotations

from io import BufferedIOBase, TextIOBase, TextIOWrapper
from pathlib import Path
from typing import Any, cast


class _TomlCompat:
    """Expose a minimal ``toml`` module compatible surface."""

    @staticmethod
    def loads(data: str | bytes) -> dict[str, Any]:
        """Parse TOML from a string or UTF-8 bytes payload."""
        import tomllib

        if isinstance(data, bytes):
            return tomllib.loads(data.decode("utf-8"))
        return tomllib.loads(data)

    @staticmethod
    def dumps(data: dict[str, Any]) -> str:
        """Serialize a dictionary to TOML text."""
        try:
            import tomli_w
        except ImportError:
            try:
                import toml as legacy_toml  # type: ignore[import-untyped]
            except ImportError as import_error:
                raise RuntimeError(
                    "TOML writing support is unavailable. Install britecore_sdk dependencies "
                    "(tomli-w) or legacy toml."
                ) from import_error
            return legacy_toml.dumps(data)

        return tomli_w.dumps(data)

    @classmethod
    def load(cls, source: str | Path | TextIOBase | BufferedIOBase) -> dict[str, Any]:
        """Parse TOML from a path or file object."""
        import tomllib

        if isinstance(source, (str, Path)):
            with open(source, "rb") as handle:
                return tomllib.load(handle)

        # tomllib.load requires bytes-mode file objects.
        if isinstance(source, TextIOBase):
            return cls.loads(source.read())
        return tomllib.load(source)

    @classmethod
    def dump(
        cls,
        data: dict[str, Any],
        destination: TextIOBase | BufferedIOBase,
    ) -> None:
        """Write TOML to a file-like object."""
        try:
            import tomli_w

            if isinstance(destination, BufferedIOBase):
                cast(Any, tomli_w).dump(data, destination)
                destination.flush()
                return

            binary_buffer = getattr(destination, "buffer", None)
            if binary_buffer is not None:
                cast(Any, tomli_w).dump(data, binary_buffer)
                destination.flush()
                return

            # Some text streams (for example StringIO) do not expose .buffer.
            # Defer to legacy text-mode writer in the fallback block below.
            raise TypeError("Text stream destination must provide a binary buffer")
        except (ImportError, TypeError):
            try:
                import toml as legacy_toml  # type: ignore[import-untyped]
            except ImportError as import_error:
                raise RuntimeError(
                    "TOML writing support is unavailable. Install britecore_sdk dependencies "
                    "(tomli-w) or legacy toml."
                ) from import_error

            if isinstance(destination, BufferedIOBase):
                wrapped = TextIOWrapper(
                    cast(Any, destination), encoding="utf-8", write_through=True
                )
                try:
                    legacy_toml.dump(data, wrapped)
                    wrapped.flush()
                finally:
                    wrapped.detach()
                return

            legacy_toml.dump(data, destination)


toml = _TomlCompat()

__all__ = ["toml"]
