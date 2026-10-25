import os
import sqlite3
import pytest
from src.database import get_db_connection, get_user_by_id

@pytest.fixture
def setup_test_db(tmp_path):
    db_file = str(tmp_path / "test_app.db")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com')")
    cursor.execute("INSERT INTO users (username, email) VALUES ('bob', 'bob@example.com')")
    cursor.execute("INSERT INTO users (username, email) VALUES ('charlie', 'charlie@example.com')")
    conn.commit()
    conn.close()
    return db_file

def test_get_user_by_id_valid(setup_test_db):
    user = get_user_by_id(1, db_path=setup_test_db)
    assert user is not None
    assert user[0] == 1
    assert user[1] == "alice"
    assert user[2] == "alice@example.com"

def test_get_user_by_id_nonexistent(setup_test_db):
    user = get_user_by_id(999, db_path=setup_test_db)
    assert user is None

def test_sql_injection_payload_is_neutralized(setup_test_db):
    """Verify that SQL injection strings are safely treated as literal parameter values."""
    # Attempt tautology injection which would return user #1 with unescaped string formatting
    sql_injection_payload = "1 OR 1=1"
    user = get_user_by_id(sql_injection_payload, db_path=setup_test_db)
    # Under parameterized queries, no user has an ID equal to the string '1 OR 1=1', so returns None
    assert user is None

    # Attempt stacked query injection which would destroy the table if executed as raw SQL
    stacked_payload = "1; DROP TABLE users; --"
    user = get_user_by_id(stacked_payload, db_path=setup_test_db)
    assert user is None

    # Verify that the users table remains intact and uncorrupted
    conn = sqlite3.connect(setup_test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 3
