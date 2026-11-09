"""Movie dashboard — search + tabs (Browse / Favorites / History), UI only."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QLabel, QScrollArea, QGridLayout,
    QTabWidget, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from ui.movie_card import MovieCard
from ui.movie_player import MoviePlayer

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
        self.favorites: set[str] = set()  # UI-only
        self.history: list[dict] = []  # UI-only, newest first
        self.logged_out = False
        self.setWindowTitle(f"CineVault — Welcome, {username}")
        self.resize(1180, 780)
        self._build()
        self._refresh_all()

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
        self.search.textChanged.connect(self._refresh_browse)
        top.addWidget(self.search, 1)

        genres = ["All"] + sorted({m["genre"] for m in DUMMY_MOVIES})
        self.genre_box = QComboBox()
        self.genre_box.addItems(genres)
        self.genre_box.currentTextChanged.connect(self._refresh_browse)
        top.addWidget(self.genre_box)

        user_lbl = QLabel(f"👤 {self.username}")
        user_lbl.setStyleSheet("color: #a1a1aa; font-weight: bold; padding: 0 8px;")
        top.addWidget(user_lbl)

        logout_btn = QPushButton("Log Out")
        logout_btn.setStyleSheet("background: #26262f; border: 1px solid #3a3a48; padding: 8px 14px;")
        logout_btn.clicked.connect(self._on_logout)
        top.addWidget(logout_btn)
        root.addLayout(top)

        # Player — hidden until Play is clicked
        self.player = MoviePlayer()
        root.addWidget(self.player)

        # Tabs: Browse / Favorites / History
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        self.browse_tab = self._make_tab()
        self.fav_tab = self._make_tab()
        self.hist_tab = self._make_tab()
        self.tabs.addTab(self.browse_tab[0], "🎬 Browse")
        self.tabs.addTab(self.fav_tab[0], "♥ Favorites")
        self.tabs.addTab(self.hist_tab[0], "🕘 History")

    def _make_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        holder = QWidget()
        scroll.setWidget(holder)
        grid = QGridLayout(holder)
        grid.setSpacing(12)
        grid.setContentsMargins(8, 8, 8, 8)
        return (scroll, grid)

    # --- Filtering & rendering ---
    def _filtered_browse(self):
        q = self.search.text().strip().lower()
        genre = self.genre_box.currentText()
        return [m for m in DUMMY_MOVIES
                if (genre == "All" or m["genre"] == genre)
                and (not q or q in m["title"].lower() or q in m["desc"].lower())]

    def _clear_grid(self, grid):
        while grid.count():
            item = grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _fill_grid(self, grid, movies):
        for i, movie in enumerate(movies):
            card = MovieCard(movie, is_fav=movie["title"] in self.favorites)
            card.play_btn.clicked.connect(lambda _, m=movie: self._on_play(m))
            card.fav_btn.clicked.connect(lambda _, m=movie: self._on_fav(m))
            grid.addWidget(card, i // 4, i % 4)

    def _refresh_browse(self):
        _, grid = self.browse_tab
        self._clear_grid(grid)
        movies = self._filtered_browse()
        if not movies:
            grid.addWidget(QLabel("No movies match your search."), 0, 0)
        else:
            self._fill_grid(grid, movies)

    def _refresh_favorites(self):
        _, grid = self.fav_tab
        self._clear_grid(grid)
        movies = [m for m in DUMMY_MOVIES if m["title"] in self.favorites]
        if not movies:
            grid.addWidget(QLabel("No favorites yet — tap ♡ on a card to save it."), 0, 0)
        else:
            self._fill_grid(grid, movies)

    def _refresh_history(self):
        _, grid = self.hist_tab
        self._clear_grid(grid)
        if not self.history:
            grid.addWidget(QLabel("Nothing watched yet — play a trailer to start your history."), 0, 0)
        else:
            self._fill_grid(grid, self.history)

    def _refresh_all(self):
        self._refresh_browse()
        self._refresh_favorites()
        self._refresh_history()

    # --- Actions ---
    def _on_play(self, movie):
        self.player.play_movie(movie)
        self.history = [movie] + [m for m in self.history if m["title"] != movie["title"]]
        self._refresh_history()

    def _on_fav(self, movie):
        title = movie["title"]
        if title in self.favorites:
            self.favorites.remove(title)
        else:
            self.favorites.add(title)
        self._refresh_all()

    def _on_logout(self):
        reply = QMessageBox.question(self, "Log out", "Log out of CineVault?")
        if reply == QMessageBox.StandardButton.Yes:
            self.logged_out = True
            self.close()
