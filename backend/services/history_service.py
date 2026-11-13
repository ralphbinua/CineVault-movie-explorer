"""HistoryService — watch history + favorites queries."""
from typing import Optional
from backend.database import Database
from backend.models import Movie, WatchRecord
from backend.api.tmdb_client import TMDbClient


def _tmdb_to_movie(data: dict) -> Movie:
    return Movie(
        id=data["id"],
        title=data["title"],
        genre=", ".join([g["name"] for g in data.get("genres", [])]) or "Unknown",
        year=int(data["release_date"][:4]) if data.get("release_date") else 0,
        rating=data.get("vote_average", 0),
        duration="N/A",
        description=data.get("overview", ""),
        poster_url=TMDbClient().poster_url(data.get("poster_path")),
        trailer_url="",
        poster_color="#1a1a22",
    )


class HistoryService:
    def __init__(self, db: Database, tmdb: Optional[TMDbClient] = None):
        self.db = db
        self.tmdb = tmdb or TMDbClient()

    def get_history(self, user_id: int) -> list[WatchRecord]:
        rows = self.db.get_history(user_id)
        out = []
        for r in rows:
            data = self.tmdb.movie_details(r.movie_id)
            movie = _tmdb_to_movie(data) if data else None
            out.append(WatchRecord(id=r.id, user_id=r.user_id, movie_id=r.movie_id, watched_at=r.watched_at, movie=movie))
        return out

    def get_favorites(self, user_id: int) -> list[Movie]:
        movie_ids = self.db.list_favorites(user_id)
        movies = []
        for mid in movie_ids:
            data = self.tmdb.movie_details(mid)
            if data:
                movies.append(_tmdb_to_movie(data))
        return movies

    def log_watch(self, user_id: int, movie_id: int):
        self.db.log_watch(user_id, movie_id)

    def toggle_favorite(self, user_id: int, movie_id: int) -> bool:
        return self.db.toggle_favorite(user_id, movie_id)

    def is_favorite(self, user_id: int, movie_id: int) -> bool:
        return self.db.is_favorite(user_id, movie_id)
