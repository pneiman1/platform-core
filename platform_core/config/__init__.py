"""Central configuration for platform-core.

Settings are loaded once from environment variables at process startup.
Verticals can override defaults via their own .env files.

In production, secrets come from a secrets manager (AWS Secrets Manager,
Doppler, etc.) which sets the corresponding env vars before the process starts.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Field names map to environment variable names in UPPER_CASE.
    For example, ``snowflake_account`` reads from ``SNOWFLAKE_ACCOUNT``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated env vars (e.g. PATH, HOME)
        case_sensitive=False,
    )

    # === Environment ===
    environment: Literal["dev", "staging", "prod"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # === Snowflake ===
    snowflake_account: str = ""
    snowflake_user: str = ""
    # Keypair auth (preferred). Snowflake enforces MFA on password auth, which
    # cannot complete headless — the initial auth needs a fresh TOTP code even
    # with MFA caching enabled. When snowflake_private_key_path is set, the
    # connection uses authenticator='SNOWFLAKE_JWT'. See dermiq ADR-009.
    snowflake_private_key_path: str = ""
    snowflake_private_key_passphrase: str = ""
    # Password auth remains as a fallback for accounts without MFA enforcement.
    snowflake_password: str = ""
    snowflake_role: str = "ACCOUNTADMIN"
    snowflake_warehouse: str = "COMPUTE_WH"
    snowflake_database: str = "DERMIQ"

    # === LLM provider ===
    # 'anthropic' uses api.anthropic.com directly (simpler, fine for dev)
    # 'bedrock' uses AWS Bedrock (required for HIPAA + AWS BAA)
    llm_provider: Literal["anthropic", "bedrock"] = "anthropic"
    anthropic_api_key: str = ""
    # Verified available + stable on the account 2026-07 (chunk-10); Sonnet-line
    # pricing has held constant across versions. See DECISIONS.md ADR-008.
    anthropic_model_sonnet: str = "claude-sonnet-5"
    anthropic_model_haiku: str = "claude-haiku-4-5-20251001"
    bedrock_region: str = "us-west-2"
    bedrock_model_id_sonnet: str = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    bedrock_model_id_haiku: str = "anthropic.claude-haiku-4-5-20251001-v1:0"

    # === Embeddings ===
    # 'voyage' is higher quality (1024-dim) but requires an API key
    # 'sentence_transformers' is free and runs locally (384-dim)
    embedding_provider: Literal["voyage", "sentence_transformers"] = "sentence_transformers"
    voyage_api_key: str = ""
    voyage_model: str = "voyage-3"
    sentence_transformers_model: str = "all-MiniLM-L6-v2"

    # === Application database (Postgres + pgvector) ===
    database_url: str = "postgresql://dermiq:dermiq@localhost:5432/dermiq"
    pgvector_dimensions: int = 384  # set to 1024 if embedding_provider='voyage'

    # === PHI / tenant security ===
    phi_redaction_mode: Literal["strict", "permissive"] = "strict"
    tokenization_salt: str = "CHANGE-ME-IN-PRODUCTION"

    # === Feature flags ===
    enable_rag: bool = True
    enable_forecasting: bool = True

    # === Default tenant context for local development ===
    # In production, tenant_id is set per-request from the JWT.
    # For local dev, this default lets scripts run without manual setup.
    default_tenant_id: str = "del_mar"

    # === API CORS ===
    # Comma-separated list of allowed origins. Falls back to localhost for dev.
    cors_origins: str = "http://localhost:3000"

    # === Cost controls ===
    # Monthly budget cap for Anthropic API calls (USD). Set to 0 to disable.
    # Estimated from Sonnet 5 pricing: $3/M input, $15/M output tokens.
    anthropic_monthly_budget_usd: float = 20.0


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance.

    Loaded lazily on first call, then cached for the process lifetime.
    Use this everywhere instead of instantiating Settings() directly,
    so behavior stays consistent across the codebase.
    """
    return Settings()