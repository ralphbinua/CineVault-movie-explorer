"""TMDB API client — movie metadata and trailer keys."""
import os
import requests
from typing import Optional


class TMDbClient:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        self.session = requests.Session()
        self.session.params = {"api_key": self.api_key, "language": "en-US"}

    def popular_movies(self, page: int = 1) -> list[dict]:
        if not self.api_key:
            return []
        try:
            resp = self.session.get(f"{self.BASE_URL}/movie/popular", params={"page": page}, timeout=10)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception:
            return []

    def movie_videos(self, movie_id: int) -> list[dict]:
        """Return YouTube trailer info from TMDB."""
        if not self.api_key:
            return []
        try:
            resp = self.session.get(f"{self.BASE_URL}/movie/{movie_id}/videos", timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            return [v for v in results if v.get("site") == "YouTube" and v.get("type") == "Trailer"]
        except Exception:
            return []

    def poster_url(self, poster_path: Optional[str]) -> str:
        if not poster_path:
            return ""
        return f"{self.IMAGE_BASE}{poster_path}"

    def search_movies(self, query: str) -> list[dict]:
        if not self.api_key:
            return []
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/search/movie",
                params={"query": query, "page": 1},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception:
            return []

    def genres(self) -> list[str]:
        if not self.api_key:
            return []
        try:
            resp = self.session.get(f"{self.BASE_URL}/genre/movie/list", timeout=10)
            resp.raise_for_status()
            return [g["name"] for g in resp.json().get("genres", [])]
        except Exception:
            return []

    def movie_details(self, movie_id: int) -> dict | None:
        if not self.api_key:
            return None
        try:
            resp = self.session.get(f"{self.BASE_URL}/movie/{movie_id}", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
