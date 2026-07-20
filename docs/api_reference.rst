API Reference
=============

*Last updated: July 20, 2026*

This section provides symbol-level API documentation grouped by business domain.
For narrative usage guidance and broader endpoint notes, see ``API.md``.

Notable v1.1 additions
----------------------

- ``BritecoreAPIClient`` - context manager (``__enter__``/``__exit__``), ``__repr__``, ``init_client()`` returns ``Self``
- ``do_request(..., dry_run=True)`` - synthetic dry-run response with redacted headers by default
- ``init_api_client(client_dry_run=True)`` / ``init_client(client_dry_run=True)`` - client-level dry-run defaults
- ``init_async_api_client(client_dry_run=True)`` / ``AsyncBritecoreAPIClient.ado_request(..., dry_run=True)`` - async dry-run parity with cache bypass
- ``reset_api_client()`` - clears module-level client (test isolation)
- ``HealthcheckResult.__bool__`` - truthiness from ``.ok``
- Flat exception aliases in ``britecore_sdk.exceptions`` and top-level package

Package exports
---------------

.. automodule:: britecore_sdk

Top-level convenience exports (for example ``BritecoreError``, ``NotFoundError``,
``get_api_client``) are documented in their source modules below to avoid duplicate
symbol definitions.

API clients
-----------

.. automodule:: britecore_sdk.api.britecore_api_client
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: britecore_sdk.api.britecore_async_api_client
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: britecore_sdk.api.request_cache
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. automodule:: britecore_sdk.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
---------

.. automodule:: britecore_sdk.utils.healthcheck
   :members:
   :undoc-members:
   :show-inheritance:

V2 package exports
------------------

.. automodule:: britecore_sdk.api.api_calls.v2
   :members:
   :undoc-members:
   :exclude-members: RequestParameters
   :show-inheritance:

Workflow package exports
------------------------

.. automodule:: britecore_sdk.api.workflows
   :members:
   :undoc-members:
   :show-inheritance:

API Domains
-----------

Browse grouped endpoint docs from the dedicated domains page:

- :doc:`api_domains`
