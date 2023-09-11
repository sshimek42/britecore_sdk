"""Wrapper for pyodbc"""
import sys

import pyodbc
import sclogging.sclogging_main as scl

from bclibs import settings


def __getattr__(name: str):
    return getattr(pyodbc, name)


db_conn_string = settings.db_conn_string
db_conn_options = settings.db_conn_options

logger = scl.get_logger(__file__)


def get_cursor(conn_string: str = db_conn_string,
               conn_options: dict = db_conn_options) -> pyodbc.Cursor:
    """Gets a cursor using default setting in config
    Can be overridden with parameters
    :param conn_string: Connection string
    :type conn_string: Str
    :param conn_options: Connection options
    :type conn_options: Dict
    :return: Cursor
    :rtype: pyodbc.Cursor
    """
    global logger  # skipcq: PYL-W0603
    plogger = scl.get_parent_logger()
    if plogger:
        logger = plogger
    try:
        conn1 = pyodbc.connect(conn_string, **conn_options)
    except pyodbc.DatabaseError as err:
        logger.error(err)
        sys.exit(str(err))
    logger.debug("Database connection succeeded")

    with conn1.cursor() as cursor:
        logger.debug("Cursor returned")
        return cursor


def close_cursor(cursor: pyodbc.Cursor):
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
    else:
        cursor.close()
        conn1.close()
        return None
