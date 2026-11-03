from typing import Optional, List
import sys
from pathlib import Path

# Поднимаемся на 2 уровня вверх от текущего файла до корня проекта
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.er import get_connection
from src.models.Rankings import Rankings

def _map(row) -> Rankings:
    return Rankings(*row)

def save_result(participant_id: int, competition_id: int, result: float) -> int:
    """Сохраняет результат. Возвращает result_id."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Вставляем только данные, место не вставляем!
        cur.execute(
            "INSERT INTO Results (participant_id, competition_id, result) VALUES (?, ?, ?)",
            (participant_id, competition_id, result)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_tournament_table(competition_id: int | None = None):
    conn = get_connection()
    cur = conn.cursor()

    if competition_id is not None:
        sql = """
            SELECT
                p.full_name,
                r.result
            FROM Results r
            JOIN Participants p ON r.participant_id = p.participant_id
            WHERE r.competition_id = ?
            ORDER BY r.result DESC
        """
        cur.execute(sql, (competition_id,))
    else:
        sql = """
            SELECT
                c.name AS competition_name,
                p.full_name,
                r.result
            FROM Results r
            JOIN Participants p ON r.participant_id = p.participant_id
            JOIN Competitions c ON r.competition_id = c.competition_id
            ORDER BY c.name, r.result DESC
        """
        cur.execute(sql)

    rows = cur.fetchall()
    conn.close()
    return rows