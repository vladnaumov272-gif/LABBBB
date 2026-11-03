import sqlite3
from typing import List, Optional, Any
import sys
from pathlib import Path

# Поднимаемся на 2 уровня вверх от текущего файла до корня проекта
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.er import get_connection
from src.models.Results import Result

def _map(row) -> Result:
    return Result(*row)

def create(result):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO Results(result)
    VALUES(?)
    """,(result,))
    conn.commit()
    conn.close()

def get_by_rid(result_id: int) -> Result | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT result_id, participant_id, competition_id, result
        FROM Results
        WHERE result_id = ?
    """, (result_id,))

    row = cur.fetchone()
    conn.close()

    return _map(row) if row else None


def get_all() -> list[Result]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT result_id, participant_id, competition_id, result
        FROM Results
        ORDER BY result
    """)

    rows = cur.fetchall()
    conn.close()

    return [_map(r) for r in rows]

def result_update(result_id: int, result: float) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE Results SET result = ? WHERE result_id = ?", (result, result_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def result_delete(result_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Results WHERE result_id = ?", (result_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()