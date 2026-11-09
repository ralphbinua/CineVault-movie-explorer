"""CineVault entry point — login gate then main vault."""
import sys
from PyQt6.QtWidgets import QApplication, QDialog

from ui.styles import DARK_THEME
from ui.login_dialog import LoginDialog
from ui.vault_movie_dashboard import VaultMovieDashboard


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CineVault")
    app.setStyleSheet(DARK_THEME)

    dialog = LoginDialog()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return 0

    window = VaultMovieDashboard(dialog.username_input)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
