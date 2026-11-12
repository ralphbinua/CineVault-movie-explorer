"""Login screen — wired to backend auth (register + verify hash)."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from backend.services.auth_service import AuthService, AuthError


class LoginDialog(QDialog):
    """Sign-in screen with real SQLite + hashlib auth."""

    def __init__(self, auth: AuthService):
        super().__init__()
        self.auth = auth
        self.username_input = ""
        self.setWindowTitle("CineVault — Sign In")
        self.setFixedSize(380, 480)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addStretch()

        logo = QLabel("🎬 CINEVAULT")
        logo.setStyleSheet("font-size: 28px; font-weight: 800; color: #e50914;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        sub = QLabel("Your personal trailer vault")
        sub.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        form = QFormLayout()
        layout.addLayout(form)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Username")
        form.addRow("Username", self.user_edit)

        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Password")
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Password", self.pass_edit)

        login_btn = QPushButton("Log In")
        login_btn.clicked.connect(self._on_login_click)
        layout.addWidget(login_btn)

        reg_btn = QPushButton("Create New Account")
        reg_btn.setProperty("class", "secondary")
        reg_btn.setStyleSheet("background: #26262f; border: 1px solid #3a3a48;")
        reg_btn.clicked.connect(self._on_register_click)
        layout.addWidget(reg_btn)

        hint = QLabel("Demo: guest / guest123  •  Passwords salted-hashed (hashlib)")
        hint.setStyleSheet("color: #71717a; font-size: 11px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        layout.addStretch()
        self.pass_edit.returnPressed.connect(self._on_login_click)

    def _on_login_click(self):
        try:
            self.auth.authenticate(self.user_edit.text(), self.pass_edit.text())
            self.username_input = self.user_edit.text().strip()
            self.accept()
        except AuthError as e:
            QMessageBox.warning(self, "Login failed", str(e))

    def _on_register_click(self):
        try:
            self.auth.register(self.user_edit.text(), self.pass_edit.text())
            self.username_input = self.user_edit.text().strip()
            QMessageBox.information(self, "Welcome!", f"Account created for {self.username_input}")
            self.accept()
        except AuthError as e:
            QMessageBox.warning(self, "Registration failed", str(e))
