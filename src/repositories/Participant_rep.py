import sqlite3
from typing import List, Optional, Any
import sys
from pathlib import Path


root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.er import get_connection
from src.models.Participant import Participant

def _map(row) -> Participant:
    return Participant(*row)

def create(user_id: int, full_name: str, date_of_birth: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Сначала проверяем, есть ли уже участник для этого user_id
        cur.execute(
            "SELECT participant_id FROM Participants WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        
        if row is not None:
            # Участник уже есть — возвращаем его ID
            return row[0]

        # 2. Если нет — делаем INSERT
        cur.execute("""
            INSERT INTO Participants(user_id, full_name, date_of_birth)
            VALUES(?, ?, ?)
        """, (user_id, full_name, date_of_birth))
        conn.commit()
        return cur.lastrowid

    except sqlite3.IntegrityError:
        # Крайний случай (гонка данных): между SELECT и INSERT кто-то успел вставить
        conn.rollback()
        cur.execute(
            "SELECT participant_id FROM Participants WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        if row:
            return row[0]
        raise
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_by_rid(participant_id: int) -> Participant | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT participant_id, user_id, full_name, date_of_birth
        FROM Participants
        WHERE participant_id = ?
    """, (participant_id,))

    row = cur.fetchone()
    conn.close()

    return _map(row) if row else None


def get_all() -> list[Participant]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT participant_id, user_id, full_name, date_of_birth
        FROM Participants
        ORDER BY full_name
    """)

    rows = cur.fetchall()
    conn.close()

    return [_map(r) for r in rows]

def participant_update(participant_id: int, full_name: Optional[str], birth_date: Optional[str], sport: Optional[str]) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        fields = []
        values = []
        if full_name is not None:
            fields.append("full_name = ?")
            values.append(full_name)
        if birth_date is not None:
            fields.append("date_of_birth = ?")
            values.append(birth_date)
        if not fields:
            return False
        values.append(participant_id)
        cur.execute(f"UPDATE Participants SET {', '.join(fields)} WHERE participant_id = ?", values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def participant_delete(participant_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Participants WHERE participant_id = ?", (participant_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()