import sqlite3
from typing import List, Optional, Any
import sys
from pathlib import Path

# Поднимаемся на 2 уровня вверх от текущего файла до корня проекта
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.er import get_connection
from src.models.User import User

def _map(row) -> User:
    return User(*row)

def create(username, password_hash, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO users(username, password_hash, role)
    VALUES(?,?,?)
    """,(username, password_hash, role))
    conn.commit()
    conn.close()

def get_by_id(user_id: int) -> User | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, password_hash,role
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()

    return _map(row) if row else None


def get_all() -> list[User]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, password_hash, role
        FROM users
        ORDER BY username
    """)

    rows = cur.fetchall()
    conn.close()

    return [_map(r) for r in rows]

def user_delete(user_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()