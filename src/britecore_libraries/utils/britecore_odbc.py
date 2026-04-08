"""Wrapper for pyodbc"""

from typing import Any

import pyodbc

from britecore_libraries import logger
from britecore_libraries.config.config import load_database_config
from britecore_libraries.exceptions import BritecoreError


def __getattr__(name: str):
    return getattr(pyodbc, name)


def _resolve_db_config(target_site: str) -> tuple[str, dict[str, Any]]:
    """Resolve DB config for the explicitly provided site."""
    return load_database_config(target_site=target_site)


def get_cursor(
    conn_string: str | None = None,
    conn_options: dict[str, Any] | None = None,
    *,
    target_site: str | None = None,
) -> pyodbc.Cursor:
    """Gets a cursor using default setting in config.

    Can be overridden with parameters.
    :param conn_string: Connection string
    :type conn_string: Str
    :param conn_options: Connection options
    :type conn_options: Dict
    :param target_site: Keyword-only site/environment name used to resolve DB settings
        from ``.secrets.toml`` when ``conn_string``/``conn_options`` are omitted.
    :type target_site: Str | None
    :return: Cursor
    :rtype: pyodbc.Cursor
    """
    if conn_string is None or conn_options is None:
        if not target_site or not target_site.strip():
            raise BritecoreError.ConfigurationError(
                "target_site is required when loading ODBC settings from config"
            )
        resolved_conn_string, resolved_conn_options = _resolve_db_config(target_site)
        conn_string = conn_string or resolved_conn_string
        conn_options = conn_options or resolved_conn_options

    if conn_string is None or conn_options is None:
        raise BritecoreError.ConfigurationError("Database connection settings are required")

    try:
        conn1 = pyodbc.connect(conn_string, **conn_options)
    except pyodbc.DatabaseError as err:
        logger.error(str(err))
        raise BritecoreError.DatabaseConnectionError(str(err)) from err
    logger.debug("Database connection succeeded")

    with conn1.cursor() as cursor:
        logger.debug("Cursor returned")
        return cursor


def close_cursor(cursor: pyodbc.Cursor) -> None:
    """Close cursor and connection
    :param cursor: Cursor to close
    :type cursor: pyodbc.Cursor
    :return: None
    :rtype: None
    """
    try:
        conn1 = cursor.connection
    except AttributeError:
        logger.error("Cursor already closed")
        return None

    cursor.close()
    logger.debug("Cursor closed")
    conn1.close()
    logger.debug("Connection closed")
    return None
