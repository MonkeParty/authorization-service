from dataclasses import dataclass
from typing import List


@dataclass
class Movie:
    id: int
    type: str = 'Movie'
    is_free: bool = False
