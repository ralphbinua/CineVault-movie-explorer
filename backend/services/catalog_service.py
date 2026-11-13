"""CatalogService — TMDB API exclusively for movie data."""
from typing import Optional, List
import random

from backend.database import Database
from backend.models import Movie
from backend.api.tmdb_client import TMDbClient


class CatalogService:
    def __init__(self, db: Database, tmdb: Optional[TMDbClient] = None):
        self.db = db
        self.tmdb = tmdb or TMDbClient()

    def list_all(self) -> List[Movie]:
        all_movies = []
        for page in range(1, 4):  # pages 1, 2, 3 (TMDB returns 20 per page)
            movies = self.tmdb.popular_movies(page=page)
            all_movies.extend(movies)

        random.shuffle(all_movies)
        return [self._tmdb_to_movie(m) for m in all_movies[:12]]

    def search(self, query: str, genre: str = "All") -> List[Movie]:
        if query:
            results = self.tmdb.search_movies(query)
            return [self._tmdb_to_movie(m) for m in results[:12]]
        return self.list_all()

    def get_by_id(self, movie_id: int) -> Movie | None:
        data = self.tmdb.movie_details(movie_id)
        if not data:
            return None
        return self._tmdb_to_movie(data)

    def genres(self) -> List[str]:
        return self.tmdb.genres()

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