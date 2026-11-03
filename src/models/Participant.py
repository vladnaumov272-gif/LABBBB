from dataclasses import dataclass

@dataclass
class Participant:
    participant_id: int
    user_id: int
    full_name: str
    date_of_birth: str