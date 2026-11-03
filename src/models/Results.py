from dataclasses import dataclass

@dataclass
class Result:
    result_id: int
    participant_id: int
    competition_id: int
    result: float