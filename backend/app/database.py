"""SQLite 연결 및 초기화 유틸리티.

파일 기반 SQLite를 사용한다. 환경변수 FITNOTE_DB_PATH로 경로를 바꿀 수 있고,
기본값은 backend/ 상위(repo root)의 fitnote_trainer.db 이다.
"""

import os
import sqlite3
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
SCHEMA_PATH = APP_DIR / "schema.sql"

DB_PATH = os.environ.get("FITNOTE_DB_PATH", str(BACKEND_DIR.parent / "fitnote_trainer.db"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """schema.sql을 실행해 없는 테이블을 생성한다.

    모든 CREATE TABLE 문이 IF NOT EXISTS로 되어 있어, 기존 DB에 새 테이블이
    추가된 경우(예: trainer_daily_tasks)에도 재실행 시 안전하게 반영된다.
    """
    conn = get_connection()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


def db_session():
    """FastAPI Depends용 커넥션 제너레이터."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
