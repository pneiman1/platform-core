# platform-core

Shared infrastructure for vertical analytics products (DermIQ, BrewIQ, FitIQ, etc.).

This repo is a Python library + reusable assets. It is **not** a deployable application on its own. Each vertical product (e.g. [DermIQ](https://github.com/pneiman1/dermiq)) imports from this library and adds vertical-specific dbt models, Airflow DAGs, seed data, and branding.

## What's inside

- **`platform_core/`** — the Python package
  - `api/` — FastAPI scaffolding (auth, audit, tenant routing)
  - `ml/` — generic ML libraries (clustering, classification, forecasting, LTV regression)
  - `rag/` — generic RAG pipeline (chunking, embedding, retrieval, generation, guardrails)
  - `config/` — environment-driven configuration
- **`dbt_macros/`** — reusable dbt macros (tokenization, helpers, tenant filtering)
- **`airflow_operators/`** — custom Airflow operators for Snowflake + dbt + RAG
- **`frontend_components/`** — shared React components (sidebar, KPI card, chat widget)
- **`scripts/`** — setup helpers
- **`docs/`** — architecture, deployment, vertical-onboarding guides

## Getting started

See **[`docs/SETUP.md`](docs/SETUP.md)** for the full step-by-step from a fresh machine to a working development environment.

Quick version, if you already have the prerequisites (WSL2 + Python 3.11+ + git):

```bash
git clone git@github.com:pneiman1/platform-core.git
cd platform-core
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
```

## Design decisions

See [`docs/DECISIONS.md`](docs/DECISIONS.md) for a log of architectural decisions and the reasoning behind each.

## Status

Early development. Not yet versioned for external consumers.

## License

Proprietary. All rights reserved.
