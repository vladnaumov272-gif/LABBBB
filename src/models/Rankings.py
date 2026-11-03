from dataclasses import dataclass
@dataclass
class Rankings:
    participant_name: str
    score: float
    position: int 

    @classmethod
    def from_db(cls, row):
        # row приходит из SQL как кортеж: (name, score, place)
        return cls(
            participant_name=row[0],
            score=row[1],
            position=row[2]
        )
