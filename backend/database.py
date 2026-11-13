"""SQLite data layer — users, watch_history, favorites only.
Movie data comes exclusively from TMDB API.
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from backend.models import User, WatchRecord
from backend.auth import PasswordHasher


class Database:
    def __init__(self, db_path: Path = Path("cinevault.db")):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()
        self.seed_demo_user()

    def close(self):
        self.conn.close()

    def init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS watch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                movie_id INTEGER NOT NULL,
                watched_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                movie_id INTEGER NOT NULL,
                UNIQUE(user_id, movie_id)
            );
        """)
        self.conn.commit()

    def seed_demo_user(self):
        # Demo guest account
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
        self.conn.commit()

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

    def log_watch(self, user_id: int, movie_id: int):
        self.conn.execute(
            "INSERT INTO watch_history (user_id,movie_id,watched_at) VALUES (?,?,?)",
            (user_id, movie_id, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_history(self, user_id: int) -> list[WatchRecord]:
        rows = self.conn.execute("""
            SELECT id, user_id, movie_id, watched_at FROM watch_history
            WHERE user_id=? ORDER BY watched_at DESC
        """, (user_id,)).fetchall()
        out = []
        for r in rows:
            out.append(WatchRecord(id=r[0], user_id=r[1], movie_id=r[2], watched_at=r[3], movie=None))
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

    def list_favorites(self, user_id: int) -> list[int]:
        rows = self.conn.execute(
            "SELECT movie_id FROM favorites WHERE user_id=? ORDER BY id DESC", (user_id,)
        ).fetchall()
        return [r[0] for r in rows]
