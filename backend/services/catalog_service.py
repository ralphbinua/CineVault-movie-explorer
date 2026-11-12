"""CatalogService — TMDB + SQLite hybrid catalog."""
from typing import Optional
from backend.database import Database
from backend.models import Movie
from backend.api.tmdb_client import TMDbClient


class CatalogService:
    def __init__(self, db: Database, tmdb: Optional[TMDbClient] = None):
        self.db = db
        self.tmdb = tmdb or TMDbClient()

    def list_all(self) -> list[Movie]:
        tmdb_movies = self.tmdb.popular_movies()
        if tmdb_movies:
            return [self._tmdb_to_movie(m) for m in tmdb_movies]
        return self.db.list_movies()

    def search(self, query: str, genre: str = "All") -> list[Movie]:
        if query:
            return self.db.list_movies(genre=genre, query=query)
        return self.list_all()

    def get_by_id(self, movie_id: int) -> Movie | None:
        return self.db.get_movie(movie_id)

    def genres(self) -> list[str]:
        return self.db.list_genres()

    @staticmethod
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
