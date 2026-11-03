import sys
from pathlib import Path


root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from typing import Optional, List
from src.repositories.Rankings_res import save_result, get_tournament_table
from src.models.Rankings import Rankings


MIN_SCORE = 0.0
MAX_SCORE = 100.0

class RankingsBusinessError(Exception):
    pass

def _validate_score(score: float) -> float:
    if not isinstance(score, (float)):
        raise RankingsBusinessError("Результат (score) должен быть числом (float).")
    score = float(score)
    if score < MIN_SCORE or score > MAX_SCORE:
        raise RankingsBusinessError(
            f"Результат {score} выходит за допустимые границы: [{MIN_SCORE}, {MAX_SCORE}]."
        )
    return score

def record_participant_result(
    participant_id: int,
    competition_id: int,
    score: float
) -> int:
    
    validated_score = _validate_score(score)
    result_id = save_result(participant_id, competition_id, validated_score)
    return result_id

def get_rankings_table(competition_id: Optional[int] = None) -> List[Rankings]:
    
    return get_tournament_table(competition_id)
