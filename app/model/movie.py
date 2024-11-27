from dataclasses import dataclass


@dataclass
class Movie:
    id: int
    type: str = 'Movie'
    is_free: bool = False
