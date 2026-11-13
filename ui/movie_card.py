"""Movie card — one movie tile in the grid."""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest


class MovieCard(QFrame):
    def __init__(self, movie: dict, is_fav: bool = False, parent=None):
        super().__init__(parent)
        self.movie = movie
        self.setFixedSize(230, 420)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_fav = is_fav
        self.nam = QNetworkAccessManager(self)
        self.nam.finished.connect(self._on_poster_downloaded)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Poster image from TMDB URL
        self.poster = QLabel()
        self.poster.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poster.setStyleSheet(
            "background: #1a1a22; border-radius: 8px; color: #a1a1aa;"
            f" font-size: 48px; font-weight: 900;"
        )
        self.poster.setMinimumHeight(260)
        self.poster.setMaximumHeight(260)
        layout.addWidget(self.poster)

        # Load poster image from TMDB
        poster_url = self.movie.get("poster_url", "")
        if poster_url:
            self.nam.get(QNetworkRequest(QUrl(poster_url)))
        else:
            # Fallback: colored block with title initial
            title = self.movie["title"] if self.movie["title"] else "?"
            self.poster.setText(title[0])

        title = QLabel(self.movie["title"])
        title.setStyleSheet("font-size: 15px; font-weight: 700;")
        title.setWordWrap(True)
        title.setMaximumHeight(40)
        layout.addWidget(title)

        meta = QLabel(f"{self.movie['genre']}  •  {self.movie['year']}  •  ★ {self.movie['rating']}")
        meta.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        layout.addWidget(meta)

        desc = QLabel(self.movie["desc"])
        desc.setStyleSheet("color: #71717a; font-size: 12px;")
        desc.setWordWrap(True)
        desc.setMaximumHeight(80)
        layout.addWidget(desc)

        row = QHBoxLayout()
        self.play_btn = QPushButton("Play Trailer")
        self.play_btn.setStyleSheet("padding: 8px;")
        row.addWidget(self.play_btn)

        self.fav_btn = QPushButton("♥" if self.is_fav else "♡")
        self.fav_btn.clicked.connect(self._toggle_fav)
        self.fav_btn.setStyleSheet("background: #26262f; border: 1px solid #3a3a48; padding: 8px;")
        row.addWidget(self.fav_btn)
        layout.addLayout(row)

    def _on_poster_downloaded(self, reply):
        if reply.error() != reply.NetworkError.NoError:
            return
        data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                210, 260,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.poster.setPixmap(scaled)
            self.poster.setText("")
        reply.deleteLater()

    def _toggle_fav(self):
        self.is_fav = not self.is_fav
        self.fav_btn.setText("♥" if self.is_fav else "♡")
