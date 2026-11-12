"""Password hashing with hashlib (lab requirement 2b)."""
import hashlib
import hmac
import os


class PasswordHasher:
    ITERATIONS = 100_000

    @staticmethod
    def generate_salt() -> str:
        return os.urandom(16).hex()

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            PasswordHasher.ITERATIONS,
        ).hex()

    @staticmethod
    def verify(password: str, expected_hash: str, salt: str) -> bool:
        candidate = PasswordHasher.hash_password(password, salt)
        return hmac.compare_digest(candidate, expected_hash)
