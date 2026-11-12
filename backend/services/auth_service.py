"""AuthService — register, login, logout, current user session."""
from typing import Optional
from backend.database import Database
from backend.auth import PasswordHasher
from backend.models import User


class AuthError(Exception):
    pass


class AuthService:
    def __init__(self, db: Database):
        self.db = db
        self._current: Optional[User] = None

    def register(self, username: str, password: str) -> User:
        username = (username or "").strip()
        password = (password or "")
        if len(username) < 3:
            raise AuthError("Username must be at least 3 characters.")
        if len(password) < 6:
            raise AuthError("Password must be at least 6 characters.")
        if self.db.get_user_by_username(username):
            raise AuthError("Username already taken.")
        salt = PasswordHasher.generate_salt()
        pw_hash = PasswordHasher.hash_password(password, salt)
        user = self.db.create_user(username, pw_hash, salt)
        self._current = user
        return user

    def authenticate(self, username: str, password: str) -> User:
        user = self.db.get_user_by_username((username or "").strip())
        if not user or not PasswordHasher.verify(password, user.password_hash, user.salt):
            raise AuthError("Invalid username or password.")
        self._current = user
        return user

    def logout(self):
        self._current = None

    @property
    def current_user(self) -> Optional[User]:
        return self._current
