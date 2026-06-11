"""Hello, Snowflake — verify the full pipe works."""
from platform_core.utils.logging import configure_logging, get_logger
from platform_core.warehouse.connection import get_snowflake_connection, test_connection

configure_logging()
log = get_logger(__name__)

if __name__ == "__main__":
    # Create the database if it doesn't exist
    with get_snowflake_connection(database=None) as conn:
        conn.cursor().execute("CREATE DATABASE IF NOT EXISTS DERMIQ_DEV")

    # Now run the connection test
    info = test_connection()
    print("\n=== Snowflake says hello ===")
    for k, v in info.items():
        print(f"  {k}: {v}")
    print()
