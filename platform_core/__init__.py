"""platform-core: shared infrastructure for vertical analytics products.

Each vertical product (DermIQ, BrewIQ, FitIQ) imports from this package
and adds its own dbt models, Airflow DAGs, seed data, and branding.
"""

__version__ = "0.1.0"