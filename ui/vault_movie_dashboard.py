"""Movie dashboard — main vault after login. Real catalog comes next."""
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import Qt


class VaultMovieDashboard(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"CineVault — Welcome, {username}")
        self.resize(900, 600)
        label = QLabel(f"🎬 Welcome, {username}!\n\nStep 3 done: Login UI works.\nNext: Movie catalog grid.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px;")
        self.setCentralWidget(label)
