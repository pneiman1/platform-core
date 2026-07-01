"""Snowflake connection helper."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import snowflake.connector
from snowflake.connector import SnowflakeConnection

from platform_core.config import get_settings
from platform_core.utils.logging import get_logger

log = get_logger(__name__)


@contextmanager
def get_snowflake_connection(
    database: str | None = None,
    schema: str | None = None,
) -> Iterator[SnowflakeConnection]:
    """Return a Snowflake connection as a context manager."""
    settings = get_settings()

    if not settings.snowflake_user or not settings.snowflake_password:
        raise RuntimeError(
            "Snowflake credentials not configured. "
            "Set SNOWFLAKE_USER and SNOWFLAKE_PASSWORD in .env"
        )

    log.info(
        "snowflake_connect_start",
        account=settings.snowflake_account,
        user=settings.snowflake_user,
    )

    conn = snowflake.connector.connect(
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        password=settings.snowflake_password,
        role=settings.snowflake_role,
        warehouse=settings.snowflake_warehouse,
        database=database if database is not None else settings.snowflake_database,
        schema=schema,
        # Heartbeat auto-refreshes the session token so long-lived connections
        # (e.g. the FastAPI app's single app.state connection) don't expire
        # overnight. Harmless for short-lived scripts. See dermiq docs/API.md.
        client_session_keep_alive=True,
    )

    try:
        log.info("snowflake_connect_ok")
        yield conn
    finally:
        conn.close()


def test_connection() -> dict:
    """Verify connectivity."""
    with get_snowflake_connection(database=None) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                CURRENT_VERSION() as version,
                CURRENT_ACCOUNT() as account,
                CURRENT_USER() as user,
                CURRENT_ROLE() as role,
                CURRENT_WAREHOUSE() as warehouse
        """)
        row = cur.fetchone()
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))