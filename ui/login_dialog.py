"""Login dialog — UI only, one file for easy debugging."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt


class LoginDialog(QDialog):
    """Sign-in screen. Stores username, no validation/db yet."""

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
