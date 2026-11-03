import sys
from pathlib import Path


root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from typing import Optional
from src.repositories.Competition_rep import (create,get_by_rid,competition_update,competition_delete)
from src.models.Competitions import Competition


MIN_NAME_LENGTH = 3

class CompetitionBusinessError(Exception):
    pass

def _validate_name(name: str) -> str:
    if not name or not isinstance(name, str):
        raise CompetitionBusinessError("Название соревнования обязательно и должно быть строкой.")
    clean = name.strip()
    if len(clean) < MIN_NAME_LENGTH:
        raise CompetitionBusinessError(f"Название должно содержать минимум {MIN_NAME_LENGTH} символов.")
    return clean

def add_competition(name: str, date: str) -> Competition:
    valid_name = _validate_name(name)
    
    cid = create(valid_name, date)
    

def update_competition(competition_id: int,name: Optional[str] = None, date: Optional[str] = None,sport: Optional[str] = None
) -> bool:
    existing = get_by_rid(competition_id)
    if existing is None:
        raise CompetitionBusinessError(f"Соревнование с ID={competition_id} не найдено.")

    if name is not None:
        _validate_name(name)

    return competition_update(competition_id, name, date, sport)

def delete_competition(competition_id: int) -> bool:
    
    existing = get_by_rid(competition_id)
    if existing is None:
        raise CompetitionBusinessError(f"Соревнование с ID={competition_id} не найдено, удалять нечего.")

    return competition_delete(competition_id)