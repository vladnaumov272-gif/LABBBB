import sys
from pathlib import Path


root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from typing import Optional
from src.repositories.Results_rep import create, get_by_rid, result_update, result_delete
from src.models.Results import Result


MIN_RESULT = 0.0
MAX_RESULT = 100.0  

class ResultBusinessError(Exception):
    pass

def _validate_result_value(value: float) -> float:
    if not isinstance(value,  float):
        raise ResultBusinessError("Результат должен быть числом ( float).")
    value = float(value)
    if value < MIN_RESULT or value > MAX_RESULT:
        raise ResultBusinessError(
            f"Результат {value} выходит за допустимые границы: [{MIN_RESULT}, {MAX_RESULT}]."
        )
    return value

def add_result(result: float) -> Result:
    
    validated = _validate_result_value(result)
    rid = create(validated) 
    obj = get_by_rid(rid)  
    

def update_result(result_id: int, new_value: float) -> bool:
    
    _validate_result_value(new_value)

    existing = get_by_rid(result_id)
    if existing is None:
        raise ResultBusinessError(f"Результат с ID={result_id} не найден.")

    return result_update(result_id, new_value)  # твой метод

def delete_result(result_id: int) -> bool:
    
    existing = get_by_rid(result_id)
    if existing is None:
        raise ResultBusinessError(f"Результат с ID={result_id} не найден, удалять нечего.")

    return result_delete(result_id)  