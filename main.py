"""CineVault entry point — login gate then main vault (loops after logout)."""
import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog

from backend.database import Database
from backend.services.auth_service import AuthService
from backend.services.catalog_service import CatalogService
from backend.services.history_service import HistoryService
from backend.services.playback_service import PlaybackService
from backend.api.tmdb_client import TMDbClient
from ui.styles import DARK_THEME
from ui.login_dialog import LoginDialog
from ui.vault_movie_dashboard import VaultMovieDashboard


def load_env():
    """Load TMDB_API_KEY from .env if python-dotenv is not installed."""
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def main():
    load_env()
    app = QApplication(sys.argv)
    app.setApplicationName("CineVault")
    app.setStyleSheet(DARK_THEME)

    db = Database()
    auth = AuthService(db)
    catalog = CatalogService(db)
    history = HistoryService(db)
    tmdb = TMDbClient()
    playback = PlaybackService(db, tmdb)

    while True:
        dialog = LoginDialog(auth)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            break

        user = auth.current_user
        window = VaultMovieDashboard(dialog.username_input, user.id, catalog, history, playback)
        window.show()
        app.exec()
        if not window.logged_out:
            break

    db.close()
    return 0


if __name__ == "__main__":
    main()
