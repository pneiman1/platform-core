"""Snowflake connection helper."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import snowflake.connector
from cryptography.hazmat.primitives import serialization
from snowflake.connector import SnowflakeConnection

from platform_core.config import get_settings
from platform_core.utils.logging import get_logger

log = get_logger(__name__)


def _load_private_key(path: str, passphrase: str) -> bytes:
    """Load an encrypted PKCS#8 private key and return it in DER form.

    The Snowflake connector expects the raw DER bytes of the unencrypted key,
    so the passphrase is used here to decrypt in memory and never leaves it.
    """
    key_path = Path(path).expanduser()
    if not key_path.is_file():
        raise RuntimeError(
            f"Snowflake private key not found at {key_path}. "
            "Check SNOWFLAKE_PRIVATE_KEY_PATH in .env"
        )

    try:
        private_key = serialization.load_pem_private_key(
            key_path.read_bytes(),
            password=passphrase.encode() if passphrase else None,
        )
    except (TypeError, ValueError) as exc:
        # Wrong/missing passphrase and malformed PEM both land here. The raw
        # cryptography errors are opaque, so name the likely cause instead.
        raise RuntimeError(
            f"Could not decrypt Snowflake private key at {key_path}: {exc}. "
            "Check SNOWFLAKE_PRIVATE_KEY_PASSPHRASE in .env"
        ) from exc

    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


@contextmanager
def get_snowflake_connection(
    database: str | None = None,
    schema: str | None = None,
) -> Iterator[SnowflakeConnection]:
    """Return a Snowflake connection as a context manager."""
    settings = get_settings()

    if not settings.snowflake_user:
        raise RuntimeError("Snowflake user not configured. Set SNOWFLAKE_USER in .env")

    # Keypair is preferred; password auth is the fallback for accounts that
    # don't enforce MFA. Exactly one of the two paths must be configured.
    auth_kwargs: dict[str, Any]
    if settings.snowflake_private_key_path:
        auth_kwargs = {
            "authenticator": "SNOWFLAKE_JWT",
            "private_key": _load_private_key(
                settings.snowflake_private_key_path,
                settings.snowflake_private_key_passphrase,
            ),
        }
        auth_method = "keypair"
    elif settings.snowflake_password:
        auth_kwargs = {"password": settings.snowflake_password}
        auth_method = "password"
    else:
        raise RuntimeError(
            "Snowflake credentials not configured. Set SNOWFLAKE_PRIVATE_KEY_PATH "
            "(preferred) or SNOWFLAKE_PASSWORD in .env"
        )

    log.info(
        "snowflake_connect_start",
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        auth_method=auth_method,
    )

    conn = snowflake.connector.connect(
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        **auth_kwargs,
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