"""CineVault entry point — login gate then main vault (loops after logout)."""
import sys
from PyQt6.QtWidgets import QApplication, QDialog

from ui.styles import DARK_THEME
from ui.login_dialog import LoginDialog
from ui.vault_movie_dashboard import VaultMovieDashboard


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CineVault")
    app.setStyleSheet(DARK_THEME)

    while True:
        dialog = LoginDialog()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            break

        window = VaultMovieDashboard(dialog.username_input)
        window.show()
        app.exec()
        # If user clicked Log Out, show login again; else quit
        if not window.logged_out:
            break

    return 0


if __name__ == "__main__":
    main()
