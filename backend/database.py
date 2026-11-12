"""SQLite data layer — users, movies, watch_history, favorites."""
import sqlite3
from pathlib import Path
from datetime import datetime
from backend.models import User, Movie, WatchRecord
from backend.auth import PasswordHasher
from backend.seed_data import SEED_MOVIES


class Database:
    def __init__(self, db_path: Path = Path("cinevault.db")):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.init_schema()
        self.seed_demo()

    def close(self):
        self.conn.close()

    # ---------- Schema ----------
    def init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                duration TEXT NOT NULL,
                description TEXT NOT NULL,
                poster_url TEXT NOT NULL,
                trailer_url TEXT NOT NULL,
                poster_color TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS watch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                movie_id INTEGER NOT NULL REFERENCES movies(id),
                watched_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                movie_id INTEGER NOT NULL REFERENCES movies(id),
                UNIQUE(user_id, movie_id)
            );
        """)
        self.conn.commit()

    def seed_demo(self):
        # Demo guest account: guest / guest123
        exists = self.conn.execute(
            "SELECT id FROM users WHERE username=?", ("guest",)
        ).fetchone()
        if not exists:
            salt = PasswordHasher.generate_salt()
            pw_hash = PasswordHasher.hash_password("guest123", salt)
            self.conn.execute(
                "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?,?,?,?)",
                ("guest", pw_hash, salt, datetime.now().isoformat()),
            )
        # Seed movies if empty
        count = self.conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
        if count == 0:
            self.conn.executemany(
                "INSERT OR REPLACE INTO movies (id,title,genre,year,rating,duration,description,poster_url,trailer_url,poster_color) VALUES (?,?,?,?,?,?,?,?,?,?)",
                [(m.id, m.title, m.genre, m.year, m.rating, m.duration, m.description, m.poster_url, m.trailer_url, m.poster_color) for m in SEED_MOVIES],
            )
        self.conn.commit()

    # ---------- Users ----------
    def create_user(self, username: str, password_hash: str, salt: str) -> User:
        created = datetime.now().isoformat()
        cur = self.conn.execute(
            "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?,?,?,?)",
            (username, password_hash, salt, created),
        )
        self.conn.commit()
        uid = cur.lastrowid
        return User(id=uid, username=username, created_at=created, password_hash=password_hash, salt=salt)

    def get_user_by_username(self, username: str):
        row = self.conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        if not row:
            return None
        return User(
            id=row["id"],
            username=row["username"],
            created_at=row["created_at"],
            password_hash=row["password_hash"],
            salt=row["salt"],
        )

    # ---------- Movies ----------
    @staticmethod
    def _row_to_movie(row) -> Movie:
        return Movie(
            id=row["id"], title=row["title"], genre=row["genre"], year=row["year"],
            rating=row["rating"], duration=row["duration"], description=row["description"],
            poster_url=row["poster_url"], trailer_url=row["trailer_url"],
            poster_color=row["poster_color"],
        )

    def list_movies(self, genre: str = "", query: str = "") -> list[Movie]:
        sql = "SELECT * FROM movies WHERE 1=1"
        params: list = []
        if genre and genre != "All":
            sql += " AND genre=?"
            params.append(genre)
        if query:
            sql += " AND (title LIKE ? OR description LIKE ?)"
            q = f"%{query}%"
            params += [q, q]
        sql += " ORDER BY rating DESC, title"
        return [self._row_to_movie(r) for r in self.conn.execute(sql, params).fetchall()]

    def get_movie(self, movie_id: int) -> Movie | None:
        row = self.conn.execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()
        return self._row_to_movie(row) if row else None

    def list_genres(self) -> list[str]:
        rows = self.conn.execute("SELECT DISTINCT genre FROM movies ORDER BY genre").fetchall()
        return [r[0] for r in rows]

    # ---------- History / Favorites ----------
    def log_watch(self, user_id: int, movie_id: int):
        self.conn.execute(
            "INSERT INTO watch_history (user_id,movie_id,watched_at) VALUES (?,?,?)",
            (user_id, movie_id, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_history(self, user_id: int) -> list[WatchRecord]:
        rows = self.conn.execute("""
            SELECT h.id, h.user_id, h.movie_id, h.watched_at, m.* FROM watch_history h
            JOIN movies m ON m.id=h.movie_id WHERE h.user_id=? ORDER BY h.watched_at DESC
        """, (user_id,)).fetchall()
        out = []
        for r in rows:
            movie = Movie(id=r["id"], title=r["title"], genre=r["genre"], year=r["year"],
                          rating=r["rating"], duration=r["duration"], description=r["description"],
                          poster_url=r["poster_url"], trailer_url=r["trailer_url"],
                          poster_color=r["poster_color"])
            out.append(WatchRecord(id=r[0], user_id=r[1], movie_id=r[2], watched_at=r[3], movie=movie))
        return out

    def is_favorite(self, user_id: int, movie_id: int) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM favorites WHERE user_id=? AND movie_id=?", (user_id, movie_id)
        ).fetchone()
        return row is not None

    def toggle_favorite(self, user_id: int, movie_id: int) -> bool:
        if self.is_favorite(user_id, movie_id):
            self.conn.execute(
                "DELETE FROM favorites WHERE user_id=? AND movie_id=?", (user_id, movie_id)
            )
            self.conn.commit()
            return False
        self.conn.execute(
            "INSERT OR IGNORE INTO favorites (user_id,movie_id) VALUES (?,?)", (user_id, movie_id)
        )
        self.conn.commit()
        return True

    def list_favorites(self, user_id: int) -> list[Movie]:
        rows = self.conn.execute("""
            SELECT m.* FROM favorites f JOIN movies m ON m.id=f.movie_id WHERE f.user_id=? ORDER BY m.rating DESC
        """, (user_id,)).fetchall()
        return [self._row_to_movie(r) for r in rows]
