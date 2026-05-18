import os
import subprocess
import pytest
import psycopg2


TEST_DB_URL = "postgresql://history:history@localhost:5433/history_test"
TEST_DB_URL_ASYNC = "postgresql+asyncpg://history:history@localhost:5433/history_test"


@pytest.fixture(scope="session")
def migrate_test_db():
    env = os.environ.copy()
    env["DATABASE_URL"] = TEST_DB_URL_ASYNC
    result = subprocess.run(
        ["python", "-m", "alembic", "upgrade", "head"],
        cwd="apps/api",
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"Could not migrate test DB: {result.stderr}")


@pytest.fixture(scope="session")
def db_conn(migrate_test_db):
    try:
        conn = psycopg2.connect(TEST_DB_URL)
    except Exception as e:
        pytest.skip(f"Test DB not available: {e}")
    yield conn
    conn.close()
