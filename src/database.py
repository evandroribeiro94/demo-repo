import sqlite3
from typing import Optional, Tuple, Any
from src.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_db_connection(db_path: str = "app.db") -> sqlite3.Connection:
    """Establish and return an SQLite database connection."""
    return sqlite3.connect(db_path)

def get_user_by_id(user_id: Any, db_path: str = "app.db") -> Optional[Tuple]:
    """Retrieve user record by ID using safe parameterized queries (CWE-89 mitigation).

    Parameters are passed via SQLite parameter placeholders (?) rather than string
    interpolation to guarantee protection against SQL injection attacks.
    Database connections are safely closed in a finally block.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()
