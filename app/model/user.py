from dataclasses import dataclass
from typing import List

@dataclass
class User:
    id: int
    type: str = 'User'

    def get_actor(self) -> str:
        """
        Returns a string representation of the user as required by Oso Cloud (e.g., 'user:<id>').
        """
        return f"user:{self.id}"
