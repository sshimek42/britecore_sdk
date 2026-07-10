"""Check local API spec freshness and detect newer upstream spec versions."""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[3]
SPEC_PATH = REPO_ROOT / "api_specs" / "current" / "britecore.json"
SPEC_SOURCE_URL = (
    "https://api.britecore.com/specifications/BriteCore/2.0.0/openapi.json"
)
MAX_SPEC_AGE_DAYS = 30


def check_spec_exists_and_fresh() -> bool:
    """Return True when the canonical API spec exists and is <= MAX_SPEC_AGE_DAYS old."""
    if not SPEC_PATH.exists():
        print(f"WARNING: API spec file missing: {SPEC_PATH}")
        return False
    mtime = SPEC_PATH.stat().st_mtime
    dt = datetime.fromtimestamp(mtime)
    age_days = (datetime.now() - dt).days
    if age_days > MAX_SPEC_AGE_DAYS:
        print(
            f"WARNING: API spec file is older than {MAX_SPEC_AGE_DAYS} days"
            f" (last modified {dt.date()})"
        )
        return False
    return True


def _extract_version_components(version: str) -> tuple[int, ...]:
    """Extract numeric version components from a version string."""
    return tuple(int(match) for match in re.findall(r"\d+", version))


def is_newer_version(current_version: str, candidate_version: str) -> bool:
    """Return True if ``candidate_version`` is newer than ``current_version``."""
    current_parts = _extract_version_components(current_version)
    candidate_parts = _extract_version_components(candidate_version)
    if not current_parts or not candidate_parts:
        return False

    width = max(len(current_parts), len(candidate_parts))
    current_padded = current_parts + (0,) * (width - len(current_parts))
    candidate_padded = candidate_parts + (0,) * (width - len(candidate_parts))
    return candidate_padded > current_padded


def get_local_spec_version(spec_path: Path = SPEC_PATH) -> str | None:
    """Read the local spec file version from ``info.version``."""
    if not spec_path.exists():
        return None
    try:
        with spec_path.open("r", encoding="utf-8") as f:
            spec_data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    return spec_data.get("info", {}).get("version")


def get_remote_spec_version(
    spec_url: str = SPEC_SOURCE_URL, timeout_seconds: float = 10.0
) -> str | None:
    """Fetch the remote spec and return ``info.version`` when available."""
    parsed = urlparse(spec_url)
    if parsed.scheme not in ("http", "https"):
        return None
    try:
        with urlopen(spec_url, timeout=timeout_seconds) as response:  # noqa: S310
            spec_data = json.loads(response.read().decode("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return spec_data.get("info", {}).get("version")


def has_newer_remote_spec(
    spec_path: Path = SPEC_PATH, spec_url: str = SPEC_SOURCE_URL
) -> tuple[bool, str | None, str | None]:
    """Return whether a newer remote spec exists plus local/remote versions."""
    local_version = get_local_spec_version(spec_path=spec_path)
    remote_version = get_remote_spec_version(spec_url=spec_url)
    if local_version is None or remote_version is None:
        return False, local_version, remote_version
    return (
        is_newer_version(local_version, remote_version),
        local_version,
        remote_version,
    )


def main() -> None:
    """Run the API spec freshness check and exit non-zero on failure."""
    print("Checking API spec sync...")
    is_fresh = check_spec_exists_and_fresh()
    has_newer, local_version, remote_version = has_newer_remote_spec()

    if has_newer and local_version and remote_version:
        print(
            "WARNING: A newer upstream API spec is available "
            f"({local_version} -> {remote_version})."
        )
        print(f"Source URL: {SPEC_SOURCE_URL}")
    elif remote_version is None:
        print("WARNING: Could not fetch upstream API spec version for comparison.")

    if not is_fresh or has_newer:
        print("Please update api_specs/current/britecore.json!")
        sys.exit(1)
    print("API spec file exists, is recent, and matches upstream version.")


if __name__ == "__main__":
    main()
