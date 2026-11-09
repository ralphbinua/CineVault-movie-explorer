"""Movie dashboard — search + genre filter + scrollable card grid (UI only)."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QLabel, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt
from ui.movie_card import MovieCard
from ui.player_widget import PlayerWidget

# Dummy data for Step 4 UI only (DB comes later)
DUMMY_MOVIES = [
    {"title": "Big Buck Bunny", "genre": "Animation", "year": 2008, "rating": 8.3, "desc": "A giant rabbit takes revenge on three bullying rodents.", "color": "#2ea44f"},
    {"title": "Sintel", "genre": "Fantasy", "year": 2010, "rating": 8.4, "desc": "A lonely girl searches for her lost dragon friend.", "color": "#7c3aed"},
    {"title": "Tears of Steel", "genre": "Sci-Fi", "year": 2012, "rating": 7.8, "desc": "Scientists re-enact a past event to save the world from robots.", "color": "#0ea5e9"},
    {"title": "Elephants Dream", "genre": "Animation", "year": 2006, "rating": 7.5, "desc": "Two travelers explore the endless Machina machine.", "color": "#f59e0b"},
    {"title": "For Bigger Blazes", "genre": "Action", "year": 2014, "rating": 7.1, "desc": "Explosions, stunts, and big screen energy teaser.", "color": "#ef4444"},
    {"title": "For Bigger Escapes", "genre": "Adventure", "year": 2014, "rating": 7.2, "desc": "A jailbreak thriller teaser.", "color": "#06b6d4"},
    {"title": "For Bigger Fun", "genre": "Comedy", "year": 2014, "rating": 7.0, "desc": "Party comedy teaser for the big screen.", "color": "#ec4899"},
    {"title": "For Bigger Joyrides", "genre": "Action", "year": 2014, "rating": 7.4, "desc": "Car chase joyride teaser with high-octane stunts.", "color": "#f97316"},
    {"title": "Neon Horizon", "genre": "Sci-Fi", "year": 2024, "rating": 8.8, "desc": "Cyberpunk traders chase a signal from the edge of the Neon Horizon.", "color": "#14b8a6"},
    {"title": "Blender Vault", "genre": "Animation", "year": 2023, "rating": 8.0, "desc": "Behind-the-scenes vault of Blender shorts and animation magic.", "color": "#6366f1"},
    {"title": "Subaru: Street & Dirt", "genre": "Documentary", "year": 2015, "rating": 7.6, "desc": "Off-road adventure filmed on streets and dirt trails.", "color": "#10b981"},
    {"title": "For Bigger Meltdowns", "genre": "Drama", "year": 2014, "rating": 7.3, "desc": "Family drama teaser.", "color": "#8b5cf6"},
]


class VaultMovieDashboard(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.favorites: set[str] = set()  # UI-only favorites
        self.setWindowTitle(f"CineVault — Welcome, {username}")
        self.resize(1180, 780)
        self._build()
        self._refresh_grid()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 12)

        # Top bar
        top = QHBoxLayout()
        logo = QLabel("🎬 CINEVAULT")
        logo.setStyleSheet("font-size: 22px; font-weight: 900; color: #e50914;")
        top.addWidget(logo)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search titles or descriptions…")
        self.search.textChanged.connect(self._refresh_grid)
        top.addWidget(self.search, 1)

        genres = ["All"] + sorted({m["genre"] for m in DUMMY_MOVIES})
        self.genre_box = QComboBox()
        self.genre_box.addItems(genres)
        self.genre_box.currentTextChanged.connect(self._refresh_grid)
        top.addWidget(self.genre_box)

        user_lbl = QLabel(f"👤 {self.username}")
        user_lbl.setStyleSheet("color: #a1a1aa; font-weight: bold; padding: 0 8px;")
        top.addWidget(user_lbl)
        root.addLayout(top)

        # Trailer player (Step 5) — hidden until Play is clicked
        self.player = PlayerWidget()
        root.addWidget(self.player)

        # Scrollable grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.holder = QWidget()
        self.scroll.setWidget(self.holder)
        self.grid = QGridLayout(self.holder)
        self.grid.setSpacing(12)
        self.grid.setContentsMargins(8, 8, 8, 8)
        root.addWidget(self.scroll, 1)

    def _filtered(self):
        q = self.search.text().strip().lower()
        genre = self.genre_box.currentText()
        return [m for m in DUMMY_MOVIES
                if (genre == "All" or m["genre"] == genre)
                and (not q or q in m["title"].lower() or q in m["desc"].lower())]

    def _refresh_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        movies = self._filtered()
        if not movies:
            self.grid.addWidget(QLabel("No movies match your search."), 0, 0)
            return
        for i, movie in enumerate(movies):
            card = MovieCard(movie, is_fav=movie["title"] in self.favorites)
            card.play_btn.clicked.connect(lambda _, m=movie: self._on_play(m))
            card.fav_btn.clicked.connect(lambda _, m=movie: self._on_fav(m))
            self.grid.addWidget(card, i // 4, i % 4)

    def _on_play(self, movie):
        self.player.play_movie(movie)

    def _on_fav(self, movie):
        title = movie["title"]
        if title in self.favorites:
            self.favorites.remove(title)
        else:
            self.favorites.add(title)
        self._refresh_grid()
