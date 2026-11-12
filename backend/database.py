"""SQLite data layer — users table."""
import sqlite3
from pathlib import Path
from datetime import datetime
from backend.models import User
from backend.auth import PasswordHasher


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

    def init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def seed_demo(self):
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
