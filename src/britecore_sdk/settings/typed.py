"""Optional typed settings models backed by pydantic-settings.

This layer is additive: Dynaconf remains the runtime source of truth, while these
models provide stronger validation/IDE hints for callers that opt in.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dynaconf.base import LazySettings


def _imports() -> tuple[Any, Any, Any]:
    """Import pydantic modules lazily so base SDK installs stay lightweight."""
    try:
        from pydantic import BaseModel, ValidationError
        from pydantic_settings import BaseSettings
    except ImportError as import_error:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Typed settings require optional extras: pip install britecore_sdk[typed-config]"
        ) from import_error
    return BaseModel, BaseSettings, ValidationError


def build_typed_settings(
    dynaconf_settings: LazySettings,
    *,
    site_names: list[str] | tuple[str, ...] | None = None,
) -> Any:
    """Build a validated typed view of key SDK settings from a Dynaconf instance."""
    BaseModel, BaseSettings, _ValidationError = _imports()

    TypedSiteSettings = type(
        "TypedSiteSettings",
        (BaseModel,),
        {
            "base_url": "",
            "client_id": "",
            "client_secret": "",
            "api_key": "",
            "web_retry": None,
            "web_timeout": None,
            "web_timeout_long": None,
            "__annotations__": {
                "base_url": str,
                "client_id": str,
                "client_secret": str,
                "api_key": str,
                "web_retry": int | None,
                "web_timeout": int | None,
                "web_timeout_long": int | None,
            },
        },
    )

    TypedSDKSettings = type(
        "TypedSDKSettings",
        (BaseSettings,),
        {
            "target_site": None,
            "default_web_retry": None,
            "default_web_timeout": None,
            "default_web_timeout_long": None,
            "sites": {},
            "__annotations__": {
                "target_site": str | None,
                "default_web_retry": int | None,
                "default_web_timeout": int | None,
                "default_web_timeout_long": int | None,
                "sites": dict[str, Any],
            },
        },
    )

    result_sites: dict[str, Any] = {}
    for site_name in site_names or ():
        with dynaconf_settings.using_env(site_name):
            result_sites[str(site_name)] = TypedSiteSettings(
                base_url=dynaconf_settings.get("base_url", default=""),
                client_id=dynaconf_settings.get("client_id", default=""),
                client_secret=dynaconf_settings.get("client_secret", default=""),
                api_key=dynaconf_settings.get("api_key", default=""),
                web_retry=dynaconf_settings.get("web_retry", default=None),
                web_timeout=dynaconf_settings.get("web_timeout", default=None),
                web_timeout_long=dynaconf_settings.get(
                    "web_timeout_long", default=None
                ),
            )

    return TypedSDKSettings(
        target_site=dynaconf_settings.get("target_site", default=None),
        default_web_retry=dynaconf_settings.get("web_retry", default=None),
        default_web_timeout=dynaconf_settings.get("web_timeout", default=None),
        default_web_timeout_long=dynaconf_settings.get(
            "web_timeout_long", default=None
        ),
        sites=result_sites,
    )


__all__ = ["build_typed_settings"]
