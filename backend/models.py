"""Domain models — plain dataclasses, no Qt dependency."""
from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    created_at: str
    password_hash: str = ""
    salt: str = ""
