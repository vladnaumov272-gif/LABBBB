from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    username: int
    password_hash: str
    role: str