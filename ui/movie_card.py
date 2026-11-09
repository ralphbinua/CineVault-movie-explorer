"""Movie card — one movie tile in the grid."""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class MovieCard(QFrame):
    def __init__(self, movie: dict, is_fav: bool = False, parent=None):
        super().__init__(parent)
        self.movie = movie
        self.setFixedSize(230, 340)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_fav = is_fav
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Poster placeholder (colored block + initial)
        poster = QLabel(self.movie["title"][0] if self.movie["title"] else "?")
        poster.setAlignment(Qt.AlignmentFlag.AlignCenter)
        poster.setStyleSheet(
            f"background: {self.movie['color']}; border-radius: 8px;"
            f" font-size: 64px; font-weight: 900; color: white; min-height: 140px;"
        )
        layout.addWidget(poster)

        title = QLabel(self.movie["title"])
        title.setStyleSheet("font-size: 15px; font-weight: 700;")
        title.setWordWrap(True)
        layout.addWidget(title)

        meta = QLabel(f"{self.movie['genre']}  •  {self.movie['year']}  •  ★ {self.movie['rating']}")
        meta.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        layout.addWidget(meta)

        desc = QLabel(self.movie["desc"])
        desc.setStyleSheet("color: #71717a; font-size: 12px;")
        desc.setWordWrap(True)
        desc.setFixedHeight(36)
        layout.addWidget(desc)

        row = QHBoxLayout()
        self.play_btn = QPushButton("▶ Play Trailer")
        self.play_btn.setStyleSheet("padding: 8px;")
        row.addWidget(self.play_btn)

        self.fav_btn = QPushButton("♥" if self.is_fav else "♡")
        self.fav_btn.setFixedWidth(44)
        self.fav_btn.setStyleSheet("background: #26262f; border: 1px solid #3a3a48; padding: 8px;")
        row.addWidget(self.fav_btn)
        layout.addLayout(row)
