import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor

def _get_conn():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    import urllib.parse
    parsed = urllib.parse.urlparse(supabase_url)
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database="postgres",
        user="postgres",
        password=supabase_key,
        cursor_factory=RealDictCursor,
        connect_timeout=5,
    )

def execute_query(query: str, params=None) -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def execute_one(query: str, params=None) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
