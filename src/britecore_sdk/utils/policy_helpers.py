"""Deprecated helpers for policy retrieval.

.. deprecated::
    Import ``get_policies`` from
    ``britecore_sdk.api.api_calls.v2.policies`` instead.
    This module will be removed in a future release.
"""

import warnings
from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters


def get_policies(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve policies using the v2 API endpoint.

    .. deprecated::
        Use ``britecore_sdk.api.api_calls.v2.policies.get_policies`` instead.
        This shim will be removed in a future release.

    Parameters:
        **kwargs: Optional filters and request parameters forwarded to
            ``britecore_sdk.api.api_calls.v2.policies.get_policies``.

    Returns:
        Normalized ``process_result(...)`` payload with pagination metadata
        and a ``policies`` list of policy objects.
    """
    warnings.warn(
        "britecore_sdk.utils.policy_helpers.get_policies is deprecated. "
        "Use britecore_sdk.api.api_calls.v2.policies.get_policies instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from britecore_sdk.api.api_calls.v2.policies import (
        get_policies as _get_policies,
    )

    return _get_policies(**kwargs)
