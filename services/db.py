# services/db.py
import os
import mysql.connector
from contextlib import contextmanager


def get_connection():
    """
    Supports two connection modes:

    1）Cloud Run + Cloud SQL (via Unix socket):：
        DB_HOST = /cloudsql/<INSTANCE_CONNECTION_NAME>
        Configure DB_USER, DB_PASSWORD, DB_NAME normally
        No host/port needed

    2）Local development (connecting to local MySQL or Cloud SQL public IP):
        DB_HOST = 127.0.0.1 (or Cloud SQL public IP)
        DB_PORT = 3306
    """
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST", "")
    db_port = int(os.getenv("DB_PORT", "3306"))

    # Cloud Run scenario: DB_HOST looks like /cloudsql/<INSTANCE_CONNECTION_NAME>
    if db_host.startswith("/cloudsql/"):
        return mysql.connector.connect(
            user=db_user,
            password=db_password,
            database=db_name,
            unix_socket=db_host,
        )
    else:
        # Local development / direct TCP connection
        return mysql.connector.connect(
            user=db_user,
            password=db_password,
            database=db_name,
            host=db_host or "127.0.0.1",
            port=db_port,
        )


@contextmanager
def db_cursor():
    """
    Shared context manager used by services via db_cursor():：
    with db_cursor() as cur:
        cur.execute(...)
        rows = cur.fetchall()
    """
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)  # Return dict rows for easy 
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
