# services/db.py
import os
import mysql.connector
from contextlib import contextmanager


def get_connection():
    """
    支持两种模式：

    1）Cloud Run + Cloud SQL（通过 unix socket）：
        DB_HOST = /cloudsql/<INSTANCE_CONNECTION_NAME>
        DB_USER, DB_PASSWORD, DB_NAME 正常配置即可
        不需要 host/port

    2）本地开发（连接本地 MySQL 或 Cloud SQL 公网 IP）：
        DB_HOST = 127.0.0.1（或 Cloud SQL 公网 IP）
        DB_PORT = 3306
    """
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST", "")
    db_port = int(os.getenv("DB_PORT", "3306"))

    # Cloud Run 场景：DB_HOST 形如 /cloudsql/spry-sensor-474917-n7:us-east1:cloudsql1
    if db_host.startswith("/cloudsql/"):
        return mysql.connector.connect(
            user=db_user,
            password=db_password,
            database=db_name,
            unix_socket=db_host,
        )
    else:
        # 本地开发 / 直接 TCP 方式
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
    你所有 services 里用的 db_cursor() 都走这里：
    with db_cursor() as cur:
        cur.execute(...)
        rows = cur.fetchall()
    """
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)  # 返回 dict，方便 **row → Pydantic
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
