"""CineVault entry point — login gate then main vault (loops after logout)."""
import sys
from PyQt6.QtWidgets import QApplication, QDialog

from backend.database import Database
from backend.services.auth_service import AuthService
from ui.styles import DARK_THEME
from ui.login_dialog import LoginDialog
from ui.vault_movie_dashboard import VaultMovieDashboard


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CineVault")
    app.setStyleSheet(DARK_THEME)

    db = Database()
    auth = AuthService(db)

    while True:
        dialog = LoginDialog(auth)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            break

        window = VaultMovieDashboard(dialog.username_input)
        window.show()
        app.exec()
        if not window.logged_out:
            break

    db.close()
    return 0


if __name__ == "__main__":
    main()
