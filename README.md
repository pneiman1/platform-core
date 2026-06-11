# platform-core

Shared infrastructure for vertical analytics products (DermIQ, BrewIQ, FitIQ, etc.).

This repo is a Python library + reusable assets — **not** a deployable application on its own. Each vertical product (e.g., [DermIQ](https://github.com/pneiman1/dermiq)) imports from this library and adds vertical-specific dbt models, Airflow DAGs, seed data, and branding.

## What's inside

```
platform-core/
├── platform_core/              the Python package
│   ├── __init__.py             package marker, __version__
│   ├── config/
│   │   └── __init__.py         Pydantic Settings, .env loading
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging.py          structlog-based JSON logging
│   └── warehouse/
│       ├── __init__.py
│       └── connection.py       Snowflake connection helper
├── scripts/
│   └── hello_snowflake.py      end-to-end Snowflake smoke test
├── docs/
│   ├── SETUP.md                full setup-from-scratch guide
│   └── DECISIONS.md            architecture decision log
├── .env.example                template for secrets (real .env is gitignored)
├── .gitignore
├── README.md                   you are here
└── pyproject.toml              Python package metadata + dependencies
```

## Getting started

See [`docs/SETUP.md`](docs/SETUP.md) for the full step-by-step from a fresh machine.

Quick version (if you already have WSL2 + Python 3.11+ + git):

```bash
git clone git@github.com:pneiman1/platform-core.git
cd platform-core
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
cp .env.example .env
# Edit .env: fill in SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD
python scripts/hello_snowflake.py
```

If the script prints "Snowflake says hello," everything is wired correctly.

## What's working today

- ✅ Pydantic Settings configuration from environment variables / `.env`
- ✅ Structured JSON logging via structlog
- ✅ Snowflake connection helper (context-managed, auto-closes)
- ✅ End-to-end verified: laptop → Python → Snowflake → result

## What's coming next

- Snowflake schema provisioning helpers (per-tenant `raw_`, `stg_`, `int_`, `mart_` schemas)
- Reusable dbt macros (tokenization, PHI helpers, tenant filtering)
- ML libraries (clustering, classification, forecasting, LTV regression)
- RAG pipeline (chunking, embedding, retrieval, generation, guardrails)
- FastAPI scaffolding (auth, audit, tenant routing)
- Airflow custom operators

## Architecture decisions

See [`docs/DECISIONS.md`](docs/DECISIONS.md) for the running log of architectural decisions and the reasoning behind each.

## Status

Early development. Not yet versioned for external consumers.

## License

Proprietary. All rights reserved.