"""Shared request-cache primitives for API clients."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from json import dumps
from threading import RLock
from typing import Any

_EXCLUDED_HEADER_KEYS = {"authorization"}


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def _canonicalize(value: Any) -> Any:
    """Return a JSON-serializable structure with stable ordering."""
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value.keys())}
    if isinstance(value, list | tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, set):
        return sorted(_canonicalize(item) for item in value)
    return value


def build_cache_key(
    *,
    target_site: str | None,
    method: str,
    path: str,
    json_payload: Mapping[str, Any] | None = None,
    request_headers: Mapping[str, Any] | None = None,
    cache_namespace: str | None = None,
    cache_key_parts: Iterable[str] | None = None,
) -> str:
    """Build a stable cache key for a request."""
    filtered_headers = {
        str(key).lower(): value
        for key, value in (request_headers or {}).items()
        if str(key).lower() not in _EXCLUDED_HEADER_KEYS
    }
    key_payload = {
        "target_site": target_site or "",
        "method": method.upper(),
        "path": path,
        "json": _canonicalize(json_payload or {}),
        "headers": _canonicalize(filtered_headers),
        "namespace": cache_namespace or "",
        "parts": [str(part) for part in (cache_key_parts or ())],
    }
    return dumps(key_payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(slots=True)
class CacheEntry:
    """Single cached response value with expiration metadata."""

    value: Any
    expires_at: datetime
    namespace: str = ""
    created_at: datetime = field(default_factory=_utc_now)

    def is_expired(self, now: datetime | None = None) -> bool:
        """Return True when the cache entry is expired."""
        return self.expires_at <= (now or _utc_now())


class RequestCache:
    """Thread-safe in-memory TTL cache for API responses."""

    def __init__(self) -> None:
        """Initialize an empty in-memory cache guarded by a re-entrant lock."""
        self._entries: dict[str, CacheEntry] = {}
        self._lock = RLock()

    def get(self, key: str) -> Any | None:
        """Return a cached value when present and unexpired."""
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                self._entries.pop(key, None)
                return None
            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int,
        namespace: str = "",
    ) -> None:
        """Store a value in the cache when the TTL is positive."""
        if ttl_seconds <= 0:
            return
        with self._lock:
            self._entries[key] = CacheEntry(
                value=value,
                expires_at=_utc_now() + timedelta(seconds=ttl_seconds),
                namespace=namespace,
            )

    def invalidate_namespace(self, namespace: str) -> int:
        """Remove all entries belonging to the given namespace."""
        if not namespace:
            return 0
        with self._lock:
            keys_to_remove = [
                key
                for key, entry in self._entries.items()
                if entry.namespace == namespace
            ]
            for key in keys_to_remove:
                self._entries.pop(key, None)
            return len(keys_to_remove)

    def invalidate_namespaces(self, namespaces: Iterable[str]) -> int:
        """Remove all entries for the provided namespaces."""
        total_removed = 0
        for namespace in namespaces:
            total_removed += self.invalidate_namespace(namespace)
        return total_removed

    def clear(self) -> None:
        """Remove all cache entries."""
        with self._lock:
            self._entries.clear()

    def prune_expired(self) -> int:
        """Remove expired entries and return the number removed."""
        now = _utc_now()
        with self._lock:
            keys_to_remove = [
                key for key, entry in self._entries.items() if entry.is_expired(now)
            ]
            for key in keys_to_remove:
                self._entries.pop(key, None)
            return len(keys_to_remove)

    def __len__(self) -> int:
        """Return the number of currently stored entries."""
        self.prune_expired()
        with self._lock:
            return len(self._entries)
