"""HistoryService — watch history + favorites queries."""
from backend.database import Database
from backend.models import Movie, WatchRecord


class HistoryService:
    def __init__(self, db: Database):
        self.db = db

    def get_history(self, user_id: int) -> list[WatchRecord]:
        return self.db.get_history(user_id)

    def get_favorites(self, user_id: int) -> list[Movie]:
        return self.db.list_favorites(user_id)

    def log_watch(self, user_id: int, movie_id: int):
        self.db.log_watch(user_id, movie_id)

    def toggle_favorite(self, user_id: int, movie_id: int) -> bool:
        return self.db.toggle_favorite(user_id, movie_id)

    def is_favorite(self, user_id: int, movie_id: int) -> bool:
        return self.db.is_favorite(user_id, movie_id)
