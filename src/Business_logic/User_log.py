import sys
from pathlib import Path

# Поднимаемся на 2 уровня вверх от текущего файла до корня проекта
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from typing import Optional
from src.repositories.user_rep import create, get_by_id, user_delete
from src.models.User import User

ALLOWED_ROLES = {"sudia", "user"}
MIN_USERNAME_LENGTH = 2

class UserBusinessError(Exception):
    
    pass

def _validate_role(role: str) -> None:
    if role not in ALLOWED_ROLES:
        raise UserBusinessError(
            f"Недопустимая роль '{role}'. Разрешены: {', '.join(ALLOWED_ROLES)}"
        )

def _validate_username(username: str) -> str:
    clean = (username or "").strip()
    if not clean:
        raise UserBusinessError("Имя пользователя не может быть пустым.")
    if len(clean) < MIN_USERNAME_LENGTH:
        raise UserBusinessError(f"Имя должно содержать минимум {MIN_USERNAME_LENGTH} символов.")
    return clean

def _username_exists(username: str) -> bool:
    from src.repositories.user_rep import get_all
    users = get_all()
    return any(u.username == username for u in users)

def register_user(username: str, password_hash: str, role: str) -> User:
    clean_username = _validate_username(username)
    _validate_role(role)

    if _username_exists(clean_username):
        raise UserBusinessError(f"Пользователь с именем '{clean_username}' уже существует.")

    user_id = create(username=clean_username, password_hash=password_hash, role=role)
    user = get_by_id(user_id)
    

def remove_user(user_id: int, current_user_role: str = "") -> bool:
    target = get_by_id(user_id)
    if not target:
        return False

    if target.role == "sudia":
        raise UserBusinessError("Нельзя удалять пользователя с ролью 'sudia'.")

    if current_user_role not in {"sudia"}:
        raise UserBusinessError("У вас недостаточно прав для удаления пользователей.")

    return user_delete(user_id=user_id)