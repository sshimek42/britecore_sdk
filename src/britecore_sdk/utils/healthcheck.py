"""SDK healthcheck utility for configuration/auth/readiness validation."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import utils as v2_utils
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.exceptions import BritecoreError
from britecore_sdk.settings import get_target_site

PING_PATH = "/api/v2/utils/get_release_info"


@dataclass
class HealthcheckResult:
    """Structured healthcheck result for CLI and programmatic use."""

    ok: bool
    site: str
    auth_mode: str
    config_ok: bool
    api_ok: bool
    message: str

    def __bool__(self) -> bool:
        """Allow ``if result:`` / ``if not result:`` idiom based on :attr:`ok`."""
        return self.ok


def _detect_auth_mode(client: BritecoreAPIClient) -> str:
    """Return selected authentication mode from initialized client state."""
    return "api_key" if client.use_api_key else "oauth"


def run_healthcheck(
    target_site: str | None = None, ping: bool = True
) -> HealthcheckResult:
    """Run configuration/auth checks and optional safe API ping.

    Args:
        target_site: Configured site section to validate. If omitted, resolves from
            settings/env using ``get_target_site()``.
        ping: Whether to call a safe read-only endpoint.

    Returns:
        HealthcheckResult: Structured validation status.
    """
    resolved_site = target_site or get_target_site()
    if not resolved_site:
        return HealthcheckResult(
            ok=False,
            site="<unset>",
            auth_mode="unknown",
            config_ok=False,
            api_ok=False,
            message=(
                "No target site was provided and none was resolved from settings/env. "
                "Pass --site or set target_site in settings.toml."
            ),
        )

    try:
        client = init_api_client(target_site=resolved_site)
    except BritecoreError.Base as exc:
        return HealthcheckResult(
            ok=False,
            site=resolved_site,
            auth_mode="unknown",
            config_ok=False,
            api_ok=False,
            message=str(exc),
        )

    auth_mode = _detect_auth_mode(client)

    if not ping:
        return HealthcheckResult(
            ok=True,
            site=resolved_site,
            auth_mode=auth_mode,
            config_ok=True,
            api_ok=True,
            message="Configuration validated (API ping skipped).",
        )

    try:
        v2_utils.get_release_info()
    except BritecoreError.Base as exc:
        return HealthcheckResult(
            ok=False,
            site=resolved_site,
            auth_mode=auth_mode,
            config_ok=True,
            api_ok=False,
            message=str(exc),
        )

    return HealthcheckResult(
        ok=True,
        site=resolved_site,
        auth_mode=auth_mode,
        config_ok=True,
        api_ok=True,
        message="Configuration and API ping succeeded.",
    )


def _format_result(result: HealthcheckResult) -> str:
    """Format result for CLI output."""
    status = "OK" if result.ok else "FAILED"
    lines = [
        f"Healthcheck: {status}",
        f"Site: {result.site}",
        f"Auth mode: {result.auth_mode}",
        f"Config: {'OK' if result.config_ok else 'FAILED'}",
        f"API ping: {'OK' if result.api_ok else 'FAILED'}",
        f"Message: {result.message}",
    ]
    return "\n".join(lines)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for healthcheck runner."""
    parser = argparse.ArgumentParser(
        description="Run SDK configuration/API healthcheck"
    )
    parser.add_argument(
        "--site",
        required=False,
        help="Configured target site name (optional if target_site is set in settings)",
    )
    parser.add_argument(
        "--skip-ping",
        action="store_true",
        help="Only validate configuration/auth setup without API call",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for `python -m britecore_sdk.utils.healthcheck`."""
    args = _parse_args(argv)
    result = run_healthcheck(target_site=args.site, ping=not args.skip_ping)
    print(_format_result(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
