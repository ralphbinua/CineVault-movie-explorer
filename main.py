"""CineVault - STEP 3: Login Screen (UI only, no database yet)."""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout,
    QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

DARK_THEME = """
QMainWindow, QDialog { background: #0f0f14; color: #e4e4e7; font-family: Segoe UI, sans-serif; }
QLabel { color: #e4e4e7; }
QLineEdit { background: #1c1c24; border: 1px solid #2d2d3a; border-radius: 6px; padding: 8px; color: #fff; }
QLineEdit:focus { border: 1px solid #e50914; }
QPushButton { background: #e50914; color: white; border: none; border-radius: 6px; padding: 10px; font-weight: bold; }
QPushButton:hover { background: #f6121d; }
QPushButton.secondary { background: #26262f; border: 1px solid #3a3a48; }
QPushButton.secondary:hover { background: #33333f; }
"""


class LoginDialog(QDialog):
    """Step 3: Login screen UI. Stores username, no validation yet."""

    def __init__(self):
        super().__init__()
        self.username_input = ""
        self.setWindowTitle("CineVault — Sign In")
        self.setFixedSize(380, 480)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addStretch()

        # Logo
        logo = QLabel("🎬 CINEVAULT")
        logo.setStyleSheet("font-size: 28px; font-weight: 800; color: #e50914;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Subtitle
        sub = QLabel("Your personal trailer vault")
        sub.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        # Username + Password form
        form = QFormLayout()
        layout.addLayout(form)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Username")
        form.addRow("Username", self.user_edit)

        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Password")
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Password", self.pass_edit)

        # Log In button
        login_btn = QPushButton("Log In")
        login_btn.clicked.connect(self._on_login_click)
        layout.addWidget(login_btn)

        # Create Account button (secondary)
        reg_btn = QPushButton("Create New Account")
        reg_btn.setProperty("class", "secondary")
        reg_btn.setStyleSheet("background: #26262f; border: 1px solid #3a3a48;")
        reg_btn.clicked.connect(self._on_register_click)
        layout.addWidget(reg_btn)

        hint = QLabel("UI only — no database yet • Step 3")
        hint.setStyleSheet("color: #71717a; font-size: 11px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        layout.addStretch()
        self.pass_edit.returnPressed.connect(self._on_login_click)

    def _on_login_click(self):
        self.username_input = self.user_edit.text().strip()
        if not self.username_input:
            QMessageBox.warning(self, "Empty", "Enter a username (UI demo).")
            return
        self.accept()

    def _on_register_click(self):
        self.username_input = self.user_edit.text().strip()
        if not self.username_input:
            QMessageBox.warning(self, "Empty", "Enter a username first (UI demo).")
            return
        self.accept()


class VaultWindow(QMainWindow):
    """Step 3 placeholder: vault shown after login. Real catalog comes next."""

    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"CineVault — Welcome, {username}")
        self.resize(900, 600)
        label = QLabel(f"🎬 Welcome, {username}!\n\nStep 3 done: Login UI works.\nNext: Movie catalog grid.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px;")
        self.setCentralWidget(label)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CineVault")
    app.setStyleSheet(DARK_THEME)

    dialog = LoginDialog()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return 0

    window = VaultWindow(dialog.username_input)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
