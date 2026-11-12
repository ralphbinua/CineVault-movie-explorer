"""PlaybackService — resolves trailer URLs (TMDB YouTube via yt-dlp + local MP4 fallback)."""
import yt_dlp
from backend.database import Database
from backend.api.tmdb_client import TMDbClient
from typing import Optional


class PlaybackService:
    def __init__(self, db: Database, tmdb: Optional[TMDbClient] = None):
        self.db = db
        self.tmdb = tmdb or TMDbClient()
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }

    def _extract_direct_url(self, info: dict) -> str:
        """Extract a direct playable URL from yt-dlp info dict."""
        # Single format with direct URL
        if info.get('url'):
            return info['url']
        # Multi-format (DASH): pick video-only URL from requested_formats
        for f in info.get('requested_formats', []):
            if f.get('vcodec') != 'none' and f.get('url'):
                return f['url']
        return ""

    def get_trailer_url(self, movie_id: int, tmdb_id: Optional[int] = None) -> str:
        # First choice: TMDB YouTube trailer key → resolve to direct MP4 via yt-dlp
        if tmdb_id:
            videos = self.tmdb.movie_videos(tmdb_id)
            if videos:
                key = videos[0]["key"]
                youtube_url = f"https://www.youtube.com/watch?v={key}"
                try:
                    with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=False)
                        direct_url = self._extract_direct_url(info)
                        if direct_url:
                            return direct_url
                except Exception:
                    pass  # Fall through to SQLite fallback

        # Fallback: seeded SQLite trailer URL (direct MP4 or local file)
        movie = self.db.get_movie(movie_id)
        if movie and movie.trailer_url:
            return movie.trailer_url

        return ""
