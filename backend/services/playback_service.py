"""PlaybackService — resolves trailer URLs (TMDB YouTube via yt-dlp + ffmpeg merge + local MP4 fallback)."""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
import yt_dlp
from backend.database import Database
from backend.api.tmdb_client import TMDbClient
from typing import Optional


def _find_ffmpeg() -> Optional[str]:
    """Find ffmpeg binary: try imageio-ffmpeg (pip) first, then system ffmpeg."""
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.exists(path):
            return path
    except Exception:
        pass
    system = shutil.which("ffmpeg")
    if system:
        return system
    return None


def _cleanup_old_trailes(cache_dir: Path, days: int = 30):
    """Remove trailer MP4 files older than `days` days."""
    if not cache_dir.exists():
        return
    cutoff = time.time() - (days * 86400)
    for f in cache_dir.glob("*.mp4"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except Exception:
            pass


class PlaybackService:
    def __init__(self, db: Database, tmdb: Optional[TMDbClient] = None):
        self.db = db
        self.tmdb = tmdb or TMDbClient()
        # Use app-relative cache instead of OS temp dir (persists across restarts)
        self.cache_dir = Path("trailers_cache")
        self.cache_dir.mkdir(exist_ok=True)
        _cleanup_old_trailes(self.cache_dir, days=30)
        self.ffmpeg_path = _find_ffmpeg()

    def _cache_path(self, video_id: str) -> str:
        return str(self.cache_dir / f"{video_id}.mp4")

    def _download_trailer(self, youtube_url: str, video_id: str) -> str:
        """Download YouTube trailer, merge video+audio with ffmpeg if available."""
        cache_path = self._cache_path(video_id)
        if os.path.exists(cache_path):
            return cache_path

        tmp_dir = tempfile.mkdtemp(prefix="cinevault_dl_")
        try:
            # Try to download merged format first (works if ffmpeg present)
            if self.ffmpeg_path:
                opts = {
                    'format': 'bestvideo[vcodec^=avc1]+bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                    'merge_output_format': 'mp4',
                    'outtmpl': os.path.join(tmp_dir, "%(id)s.%(ext)s"),
                    'ffmpeg_location': self.ffmpeg_path,
                }
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=True)
                        downloaded_id = info.get('id', video_id)
                        for f in os.listdir(tmp_dir):
                            if f.startswith(downloaded_id) and f.endswith('.mp4'):
                                src = os.path.join(tmp_dir, f)
                                shutil.move(src, cache_path)
                                return cache_path
                except Exception:
                    pass  # Fall through to separate downloads

            # Download video and audio separately
            video_opts = {
                'format': 'bestvideo[vcodec^=avc1]/best[vcodec!=none]',
                'quiet': True,
                'no_warnings': True,
                'outtmpl': os.path.join(tmp_dir, "video.%(ext)s"),
            }
            audio_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'outtmpl': os.path.join(tmp_dir, "audio.%(ext)s"),
            }

            video_file = None
            audio_file = None

            try:
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    ydl.extract_info(youtube_url, download=True)
                    for f in os.listdir(tmp_dir):
                        if f.startswith("video."):
                            video_file = os.path.join(tmp_dir, f)
                            break
            except Exception:
                pass

            try:
                with yt_dlp.YoutubeDL(audio_opts) as ydl:
                    ydl.extract_info(youtube_url, download=True)
                    for f in os.listdir(tmp_dir):
                        if f.startswith("audio."):
                            audio_file = os.path.join(tmp_dir, f)
                            break
            except Exception:
                pass

            # Merge with ffmpeg if available
            if video_file and audio_file and self.ffmpeg_path:
                try:
                    subprocess.run(
                        [self.ffmpeg_path, "-y", "-i", video_file, "-i", audio_file,
                         "-c", "copy", cache_path],
                        capture_output=True, check=True,
                    )
                    return cache_path
                except Exception:
                    pass

            # Fallback: just use video file (no sound)
            if video_file:
                shutil.move(video_file, cache_path)
                return cache_path

            return ""
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def get_trailer_url(self, movie_id: int, tmdb_id: Optional[int] = None) -> str:
        # First choice: TMDB YouTube trailer key → download+merge via yt-dlp + ffmpeg
        if tmdb_id:
            videos = self.tmdb.movie_videos(tmdb_id)
            if videos:
                key = videos[0]["key"]
                youtube_url = f"https://www.youtube.com/watch?v={key}"
                try:
                    local_path = self._download_trailer(youtube_url, key)
                    if local_path and os.path.exists(local_path):
                        return local_path
                except Exception:
                    pass  # Fall through to empty result

        # No SQLite fallback — all movie data comes from TMDB API
        # If no TMDB key or download failed, return empty string
        return ""