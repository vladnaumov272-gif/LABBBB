import sqlite3
from typing import List, Optional, Any
import sys
from pathlib import Path

# Поднимаемся на 2 уровня вверх от текущего файла до корня проекта
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.er import get_connection
from src.models.Competitions import Competition

def _map(row) -> Competition:
    return Competition(*row)

def create(name: str, date: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Competitions (name, date)
            VALUES (?, ?)
            """,
            (name, date),
        )
        conn.commit()
        return cur.lastrowid  # <-- обязательно: возвращает ID новой строки
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Ошибка при создании соревнования: {e}") from e
    finally:
        conn.close()

def get_by_rid(competition_id: int) -> Competition | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT competition_id, name, date
        FROM Competitions
        WHERE competition_id = ?
    """, (competition_id,))

    row = cur.fetchone()
    conn.close()

    return _map(row) if row else None

def get_all() -> list[Competition]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT competition_id, name, date
        FROM Competitions
        ORDER BY name
    """)

    rows = cur.fetchall()
    conn.close()

    return [_map(r) for r in rows]

def competition_update(competition_id: int, name: Optional[str], date: Optional[str], sport: Optional[str]) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        fields = []
        values = [] 
        if name is not None:
            fields.append("name = ?")
            values.append(name)
        if date is not None:
            fields.append("date = ?")
            values.append(date)
        if not fields:
            return False
        values.append(competition_id)
        cur.execute(f"UPDATE Competitions SET {', '.join(fields)} WHERE competition_id = ?", values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def competition_delete(competition_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Competitions WHERE competition_id = ?", (competition_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()