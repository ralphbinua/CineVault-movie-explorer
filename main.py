"""CineVault entry point — login gate then main vault (loops after logout)."""
import sys
from PyQt6.QtWidgets import QApplication, QDialog

from backend.database import Database
from backend.services.auth_service import AuthService
from backend.services.catalog_service import CatalogService
from backend.services.history_service import HistoryService
from ui.styles import DARK_THEME
from ui.login_dialog import LoginDialog
from ui.vault_movie_dashboard import VaultMovieDashboard


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CineVault")
    app.setStyleSheet(DARK_THEME)

    db = Database()
    auth = AuthService(db)
    catalog = CatalogService(db)
    history = HistoryService(db)

    while True:
        dialog = LoginDialog(auth)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            break

        user = auth.current_user
        window = VaultMovieDashboard(dialog.username_input, user.id, catalog, history)
        window.show()
        app.exec()
        if not window.logged_out:
            break

    db.close()
    return 0


if __name__ == "__main__":
    main()
