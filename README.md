# platform-core

platform-core is a reusable data-platform toolkit — the primitives that vertical
analytics SaaS products share, so each vertical only has to build its own domain
models, dashboards, and branding. It provides configuration, a Snowflake
connection helper, a RAG toolkit, and an LLM client. It is a **Python library, not
a deployable app**: verticals import from it and add their own dbt models, Airflow
DAGs, seed data, and UI.

First (and current) consumer: [DermIQ](https://github.com/pneiman1/dermiq), analytics
for cosmetic dermatology practices. The design is tenant-agnostic so additional
verticals (BrewIQ, FitIQ, …) can reuse the same core.

## What lives here

```
platform_core/
├── config/       Pydantic Settings — one env-driven Settings object (.env → typed config)
├── warehouse/    Snowflake connection helper (key-pair JWT or password) + schema naming
├── llm/          Anthropic Claude client (single-turn completion)
├── rag/          RAG toolkit: embedder, document/store interface, corpus write/read
└── utils/        structlog-based JSON logging
```

`llm/` and `rag/` arrived with DermIQ's RAG feature (chunk-10).

Ingestion utilities are **not** here — landing a source into the warehouse is
vertical-specific (schemas, types, source shape), so DermIQ owns
`dermiq/ingestion/`. platform-core provides the connection + schema-naming
primitives it builds on.

## Design principles

- **Tenant-agnostic.** No vertical or tenant is hard-coded. Schema names derive
  from `(layer, tenant)`; the connection and config carry no domain knowledge.
- **Env-driven config.** Everything flows through one `Settings` object read from
  environment / `.env` (`platform_core.config.get_settings`). In production the
  same vars come from a secrets manager.
- **Key-pair-first Snowflake auth.** The connection helper prefers key-pair (JWT)
  auth and falls back to password. Snowflake enforces MFA, which password auth
  can't satisfy headless — key-pair is the default for all unattended access.
- **Cross-platform.** macOS (Intel & Apple Silicon), Linux, and Windows/WSL2.

## How DermIQ consumes it

- **Editable install.** DermIQ installs platform-core editable (`pip install -e`)
  from a sibling checkout, so changes to the core are picked up immediately.
- **Shared config surface.** Both repos read the same env var names, so one `.env`
  convention drives platform-core's `Settings`, DermIQ's ingestion, and dbt's
  `profiles.yml` (all pointed at the same Snowflake account/warehouse via key-pair).
- **Imports, not forks.** DermIQ calls `platform_core.config`,
  `platform_core.warehouse.connection`, `platform_core.rag`, `platform_core.llm`.

## Getting started (using platform-core in a new vertical)

```bash
git clone git@github.com:pneiman1/platform-core.git
cd platform-core
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[all]"
cp .env.example .env
# Fill in SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and either
#   SNOWFLAKE_PRIVATE_KEY_PATH + SNOWFLAKE_PRIVATE_KEY_PASSPHRASE  (preferred), or
#   SNOWFLAKE_PASSWORD                                             (non-MFA fallback)
python scripts/hello_snowflake.py    # smoke-test laptop → Python → Snowflake
```

In a new vertical package, install platform-core editable alongside it and import:

```python
from platform_core.config import get_settings
from platform_core.warehouse.connection import get_snowflake_connection
from platform_core.warehouse.schemas import schema_name   # -> "<LAYER>_<TENANT>"
```

Supported platforms and full setup: [`docs/SETUP.md`](docs/SETUP.md).
Architecture decisions: [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Status

Early development; not yet versioned for external consumers. Proprietary — all
rights reserved.
