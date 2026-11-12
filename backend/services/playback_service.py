"""PlaybackService — resolves trailer URLs (TMDB YouTube key + local MP4 fallback)."""
from backend.database import Database
from backend.api.tmdb_client import TMDbClient
from typing import Optional


class PlaybackService:
    def __init__(self, db: Database, tmdb: Optional[TMDbClient] = None):
        self.db = db
        self.tmdb = tmdb or TMDbClient()

    def get_trailer_url(self, movie_id: int, tmdb_id: Optional[int] = None) -> str:
        # First choice: TMDB YouTube trailer key
        if tmdb_id:
            videos = self.tmdb.movie_videos(tmdb_id)
            if videos:
                key = videos[0]["key"]
                return f"https://www.youtube.com/watch?v={key}"

        # Fallback: seeded SQLite trailer URL (direct MP4 or local file)
        movie = self.db.get_movie(movie_id)
        if movie and movie.trailer_url:
            return movie.trailer_url

        return ""
