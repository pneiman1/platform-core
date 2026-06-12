"""Medallion schema provisioning for the warehouse.

Each tenant's data is organized into the standard medallion layers:

    raw  -> faithful, untransformed copy of the source system
    stg  -> cleaned/typed staging models (one per source table)
    int  -> intermediate business-logic models
    mart -> analytics-ready facts and dimensions

Schemas are named ``<LAYER>_<TENANT>`` within a single Snowflake database,
e.g. ``RAW_DEL_MAR``. The vertical is already implied by the database name
(``DERMIQ_DEV`` / ``DERMIQ_PROD``), so the tenant id carries only the clinic,
not the vertical. Keeping all layers in one database (rather than a database per
tenant) keeps cross-layer dbt refs and grants simple at this scale; tenant
isolation comes from the schema split plus row access policies.

This naming convention is the single source of truth for where data lives, so
both ingestion (Python) and transformation (dbt) derive schema names from
``schema_name`` rather than hard-coding strings.
"""
from __future__ import annotations

from snowflake.connector import SnowflakeConnection

from platform_core.config import get_settings
from platform_core.utils.logging import get_logger

log = get_logger(__name__)

# Medallion layers, ordered from source-of-truth to analytics-ready.
LAYERS: tuple[str, ...] = ("raw", "stg", "int", "mart")


def schema_name(layer: str, tenant_id: str) -> str:
    """Return the Snowflake schema name for a (layer, tenant) pair.

    >>> schema_name("raw", "del_mar")
    'RAW_DEL_MAR'
    """
    layer = layer.lower()
    if layer not in LAYERS:
        raise ValueError(f"Unknown layer {layer!r}; expected one of {LAYERS}")
    return f"{layer}_{tenant_id}".upper()


def provision_tenant_schemas(
    conn: SnowflakeConnection,
    tenant_id: str,
    *,
    database: str | None = None,
    layers: tuple[str, ...] = LAYERS,
) -> list[str]:
    """Create the database (if needed) and all medallion schemas for a tenant.

    Idempotent: uses ``CREATE ... IF NOT EXISTS`` throughout, so it is safe to
    call on every pipeline run. Returns the list of fully-qualified schema names
    that now exist for this tenant.
    """
    db = database or get_settings().snowflake_database
    cur = conn.cursor()

    cur.execute(f'CREATE DATABASE IF NOT EXISTS "{db}"')
    cur.execute(f'USE DATABASE "{db}"')

    created: list[str] = []
    for layer in layers:
        schema = schema_name(layer, tenant_id)
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{db}"."{schema}"')
        created.append(f"{db}.{schema}")

    log.info("provision_tenant_schemas", tenant_id=tenant_id, database=db, schemas=created)
    return created
