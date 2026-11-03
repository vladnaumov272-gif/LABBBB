import sys
from pathlib import Path


root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from typing import Optional
from src.repositories.Participant_rep import (
    create,
    get_by_rid,
    participant_update,
    participant_delete,
)
from src.models.Participant import Participant
from datetime import datetime


MIN_FULL_NAME_LENGTH = 3
DATE_FORMAT = "%Y-%m-%d"  

class ParticipantBusinessError(Exception):
    pass

def _validate_full_name(name: str) -> str:
    if not name or not isinstance(name, str):
        raise ParticipantBusinessError("ФИО участника обязательно и должно быть строкой.")
    clean = name.strip()
    if len(clean) < MIN_FULL_NAME_LENGTH:
        raise ParticipantBusinessError(f"ФИО должно содержать минимум {MIN_FULL_NAME_LENGTH} символов.")
    return clean

def _validate_date(date_str: str) -> str:
    if not date_str or not isinstance(date_str, str):
        raise ParticipantBusinessError("Дата рождения обязательна и должна быть строкой в формате YYYY-MM-DD.")
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return date_str
    except ValueError:
        raise ParticipantBusinessError(f"Некорректный формат даты: '{date_str}'. Ожидался формат {DATE_FORMAT}.")

def add_participant(full_name: str, date_of_birth: str) -> Participant:
   
    valid_name = _validate_full_name(full_name)
    valid_date = _validate_date(date_of_birth)

    pid = create(valid_name, valid_date)


def update_participant(
    participant_id: int,
    full_name: Optional[str] = None,
    birth_date: Optional[str] = None,
    sport: Optional[str] = None
) -> bool:
    
    existing = get_by_rid(participant_id)
    if existing is None:
        raise ParticipantBusinessError(f"Участник с ID={participant_id} не найден.")

    
    if full_name is not None:
        _validate_full_name(full_name)

    
    if birth_date is not None:
        _validate_date(birth_date)

    
    return participant_update(participant_id, full_name, birth_date, sport)

def delete_participant(participant_id: int) -> bool:
    
    existing = get_by_rid(participant_id)
    if existing is None:
        raise ParticipantBusinessError(f"Участник с ID={participant_id} не найден, удалять нечего.")

    return participant_delete(participant_id)