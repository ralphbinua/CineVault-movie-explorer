"""CatalogService — TMDB API exclusively for movie data."""
from typing import Optional, List
import json
import random
from pathlib import Path

from backend.database import Database
from backend.models import Movie
from backend.api.tmdb_client import TMDbClient


class CatalogService:
    def __init__(self, db: Database, tmdb: Optional[TMDbClient] = None):
        self.db = db
        self.tmdb = tmdb or TMDbClient()

    def _cache_path(self) -> Path:
        """Return path to movie selection cache file."""
        return Path("cinevault_selected.json")

    def _load_cached_movies(self) -> List[Movie] | None:
        """Return cached 12 movies if available and not stale, None otherwise."""
        cp = self._cache_path()
        if cp.exists():
            try:
                data = json.loads(cp.read_text())
                movie_ids = data.get("movie_ids", [])
                if movie_ids:
                    movies = [self.get_by_id(mid) for mid in movie_ids]
                    movies = [m for m in movies if m is not None]
                    if movies:
                        return movies[:12]
            except Exception:
                pass
        return None

    def _save_cached_movies(self, movies: List[Movie]):
        """Cache the first 12 movies to disk."""
        cp = self._cache_path()
        cp.parent.mkdir(exist_ok=True)
        cp.write_text(json.dumps({"movie_ids": [m.id for m in movies[:12]]}))
        # Set modification time to "never stale" — keep forever
        cp.touch()

    def list_all(self) -> List[Movie]:
        # Try cache first — skip TMDB API on subsequent launches
        cached = self._load_cached_movies()
        if cached:
            return cached

        # Fallback: fetch from TMDB and cache
        all_movies = []
        for page in range(1, 3):  # pages 1, 2 (TMDB returns 20 per page = 40 total)
            movies = self.tmdb.popular_movies(page=page)
            all_movies.extend(movies)

        random.shuffle(all_movies)
        selected = [self._tmdb_to_movie(m) for m in all_movies[:12]]
        self._save_cached_movies(selected)
        return selected

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