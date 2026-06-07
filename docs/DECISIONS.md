# Architecture Decision Log

A running log of significant architectural decisions made during platform-core development.

This document is append-only. Past decisions are never edited or deleted — they are superseded by new entries if direction changes.

## ADR-001: Two-repo architecture (platform-core + per-vertical packages)

**Date:** 2026-06-06
**Status:** Accepted

**Context.** The roadmap calls for multiple vertical analytics SaaS offerings (DermIQ for cosmetic dermatology, BrewIQ for breweries, FitIQ for gyms). Each vertical shares ~80% of its infrastructure but differs in data models, KPIs, branding, and customer copy.

**Decision.** Split the codebase into two types of repository:
- `platform-core` — a versioned Python library containing all shared infrastructure
- One repository per vertical — depending on a specific pinned version of platform-core

**Alternatives considered.**
- Mono-repo: easier to refactor across boundaries; harder to release verticals independently. Overkill for a solo founder.
- Copy-paste-and-diverge: fastest to start, exponential maintenance cost.

**Consequences.**
- (+) Each vertical can pin to a known-good platform-core version and upgrade on its own schedule.
- (+) Bug fixes in platform-core land in every vertical with a one-line version bump.
- (+) Each vertical has its own commit history, issues, stars, and marketing story.
- (+) Future open-sourcing of platform-core is possible without exposing vertical-specific code.
- (–) Cross-cutting refactors require coordinated changes in multiple repos.

## ADR-002: Snowflake as the data warehouse

**Date:** 2026-06-06
**Status:** Accepted

**Context.** Need a cloud data warehouse for per-tenant clinic data, dbt transformations, and analytical queries.

**Decision.** Use Snowflake.

**Alternatives considered.**
- BigQuery: comparable performance, but Snowflake's HIPAA tier is operationally simpler.
- Databricks SQL: better for Spark-heavy workloads; ours is SQL + dbt + light Python.
- Postgres / Redshift: cheaper at small scale but operationally heavy as tenant count grows.

**Consequences.**
- (+) Standard tier is cheap for dev (auto-suspend after 60s).
- (+) Business Critical tier covers HIPAA when needed.
- (+) Per-tenant schemas + row access policies provide tenant isolation.
- (–) Annual contract minimums after free trial.
- (–) Some Snowflake-specific lock-in.

## ADR-003: dbt Core for transformations

**Date:** 2026-06-06
**Status:** Accepted

**Context.** Raw EMR data needs heavy transformation: deduplication, joins, derived metrics, slowly-changing dimensions. Needs to be testable, documentable, version-controlled.

**Decision.** Use dbt Core (open source). Each vertical owns its own dbt project; shared macros live in platform-core.

**Alternatives considered.**
- dbt Cloud: managed dbt + IDE + scheduler. Worth it for teams with analyst onboarding; redundant since we orchestrate with Airflow.
- Custom Python ETL: faster to start, loses testing/documentation/lineage benefits.
- Snowflake stored procedures: powerful but unportable and hard to test.

**Consequences.**
- (+) Free.
- (+) Strong ecosystem (dbt-snowflake, dbt-utils).
- (+) Generated documentation is a sales artifact.
- (+) Native data testing primitives.

## ADR-004: Airflow for orchestration

**Date:** 2026-06-06
**Status:** Accepted

**Context.** Need scheduled execution of nightly ingestion, dbt builds, ML retraining, and weekly brief generation, with retries, dependencies, observability, and per-tenant parameterization.

**Decision.** Apache Airflow, running locally via Astronomer's `astro` CLI in dev; self-hosted on EC2 in production until ops bandwidth justifies managed Astronomer or MWAA.

**Alternatives considered.**
- Dagster: strong asset-based model, but Airflow has broader market recognition.
- Prefect: modern and Pythonic but less mature operator ecosystem.
- Cron + bash: cheap but loses retries, observability, parameterization.

**Consequences.**
- (+) Massive operator ecosystem.
- (+) Astronomer's `astro dev start` makes local development one command.
- (+) Well-known to clinic IT teams' existing ops culture.
- (–) Configuration sprawl requires discipline.

## ADR-005: Anthropic API directly (not Bedrock) during development

**Date:** 2026-06-06
**Status:** Accepted for dev; revisit for production with PHI

**Context.** RAG chatbot and weekly brief both call Claude.

**Decision.** Use the Anthropic API directly during development. Make the LLM client a thin abstraction so we can switch to Bedrock via config flag without touching business logic.

**Alternatives considered.**
- AWS Bedrock from day one: operationally cleaner for HIPAA. Rejected only because it requires AWS setup not needed for demo phase.
- OpenAI: comparable quality; rejected because Claude's long-context analytical reasoning is a differentiator.

**Consequences.**
- (+) Zero AWS dependency for local development.
- (+) Faster iteration.
- (–) Must switch to Bedrock (or sign direct Anthropic BAA) before real PHI.

## ADR-006: pgvector for the RAG vector store

**Date:** 2026-06-06
**Status:** Accepted

**Context.** RAG pipeline needs a vector store for embeddings of clinical notes, treatment plans, and SOPs.

**Decision.** Postgres with `pgvector` extension. Same database stores application metadata (users, tenants, chat history).

**Alternatives considered.**
- Pinecone: managed, scales effortlessly. Rejected because of extra vendor BAA, $70/mo+ minimum, separate-service round trips.
- Weaviate / Qdrant / Chroma: dedicated vector DBs that add ops overhead with no benefit at our scale.
- OpenSearch: strong hybrid search but overkill until millions of documents.

**Consequences.**
- (+) Single database to back up, monitor, secure.
- (+) Joins between vector results and structured metadata happen in SQL.
- (+) pgvector's HNSW index handles 10M+ embeddings per tenant.
- (–) Pure-play vector DBs faster at very large scale; revisit if any single tenant exceeds 50M chunks.

## How to add an ADR

Template:

ADR-N: Short title in present tense
Date: YYYY-MM-DD
Status: Proposed | Accepted | Superseded by ADR-M | Deprecated
Context. What problem? What constraints?
Decision. What did we decide?
Alternatives considered. What else? Why not?
Consequences. Positive and negative effects.

Number ADRs sequentially. Never delete or rewrite a past ADR — supersede it with a new one if direction changes.