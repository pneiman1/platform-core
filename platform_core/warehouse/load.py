"""Load pandas DataFrames into Snowflake tables.

A thin wrapper over ``snowflake.connector.pandas_tools.write_pandas`` that
applies our conventions: uppercase column identifiers (so columns are queryable
unquoted, the Snowflake norm) and full-refresh (overwrite) semantics suitable
for raw-layer ingestion, where each run replaces the table with the current
source snapshot.
"""
from __future__ import annotations

import pandas as pd
from snowflake.connector import SnowflakeConnection
from snowflake.connector.pandas_tools import write_pandas

from platform_core.config import get_settings
from platform_core.utils.logging import get_logger

log = get_logger(__name__)


def load_dataframe(
    conn: SnowflakeConnection,
    df: pd.DataFrame,
    *,
    table: str,
    schema: str,
    database: str | None = None,
    overwrite: bool = True,
) -> int:
    """Write ``df`` into ``<database>.<schema>.<table>``, creating it if needed.

    Column names are uppercased before load. The target table is auto-created to
    match the DataFrame; with ``overwrite=True`` (the default) it is replaced
    each run — full-refresh semantics appropriate for raw ingestion. Returns the
    number of rows written.
    """
    db = database or get_settings().snowflake_database
    table = table.upper()
    schema = schema.upper()

    df = df.copy()
    df.columns = [str(c).upper() for c in df.columns]

    success, n_chunks, n_rows, _ = write_pandas(
        conn,
        df,
        table_name=table,
        database=db,
        schema=schema,
        auto_create_table=True,
        overwrite=overwrite,
        # Map tz-aware datetimes to Snowflake TIMESTAMP_TZ (preserving timezone)
        # instead of the legacy path that silently drops tz info / can shift times.
        use_logical_type=True,
    )
    if not success:
        raise RuntimeError(f"write_pandas failed for {db}.{schema}.{table}")

    log.info(
        "load_dataframe",
        target=f"{db}.{schema}.{table}",
        rows=n_rows,
        chunks=n_chunks,
        overwrite=overwrite,
    )
    return n_rows
