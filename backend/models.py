"""Domain models — plain dataclasses, no Qt dependency."""
from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    created_at: str
    password_hash: str = ""
    salt: str = ""


@dataclass
class Movie:
    id: int
    title: str
    genre: str
    year: int
    rating: float
    duration: str
    description: str
    poster_url: str
    trailer_url: str
    poster_color: str

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "genre": self.genre,
            "year": self.year,
            "rating": self.rating,
            "duration": self.duration,
            "desc": self.description,
            "color": self.poster_color,
            "poster_url": self.poster_url,
            "trailer_url": self.trailer_url,
        }


@dataclass
class WatchRecord:
    id: int
    user_id: int
    movie_id: int
    watched_at: str
    movie: Movie | None = None
