"""CatalogService — GET /catalog*"""
from backend.database import Database
from backend.models import Movie


class CatalogService:
    def __init__(self, db: Database):
        self.db = db

    def list_all(self) -> list[Movie]:
        return self.db.list_movies()

    def filter_by_genre(self, genre: str) -> list[Movie]:
        return self.db.list_movies(genre=genre)

    def search(self, query: str, genre: str = "All") -> list[Movie]:
        return self.db.list_movies(genre=genre, query=query.strip())

    def get_by_id(self, movie_id: int) -> Movie | None:
        return self.db.get_movie(movie_id)

    def genres(self) -> list[str]:
        return self.db.list_genres()
