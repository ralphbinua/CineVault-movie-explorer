"""Movie dashboard — search + tabs (Browse / Favorites / History), backed by SQLite services."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QLabel, QScrollArea, QGridLayout,
    QTabWidget, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from ui.movie_card import MovieCard
from ui.movie_player import MoviePlayer
from backend.services.catalog_service import CatalogService
from backend.services.history_service import HistoryService


class VaultMovieDashboard(QMainWindow):
    def __init__(self, username: str, user_id: int, catalog: CatalogService, history: HistoryService):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.catalog = catalog
        self.history_service = history
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

        genres = ["All"] + self.catalog.genres()
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
        movies = self.catalog.search(q, genre)
        return [m for m in movies if (not q or q in m.title.lower() or q in m.description.lower())]

    def _clear_grid(self, grid):
        while grid.count():
            item = grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _fill_grid(self, grid, movies):
        for i, movie in enumerate(movies):
            is_fav = self.history_service.is_favorite(self.user_id, movie.id)
            card = MovieCard(movie.to_dict(), is_fav=is_fav)
            card.play_btn.clicked.connect(lambda _, m=movie.to_dict(): self._on_play(m))
            card.fav_btn.clicked.connect(lambda _, m=movie.to_dict(): self._on_fav(m))
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
        movies = self.history_service.get_favorites(self.user_id)
        if not movies:
            grid.addWidget(QLabel("No favorites yet — tap ♡ on a card to save it."), 0, 0)
        else:
            self._fill_grid(grid, movies)

    def _refresh_history(self):
        _, grid = self.hist_tab
        self._clear_grid(grid)
        records = self.history_service.get_history(self.user_id)
        if not records:
            grid.addWidget(QLabel("Nothing watched yet — play a trailer to start your history."), 0, 0)
        else:
            movies = [r.movie for r in records if r.movie]
            self._fill_grid(grid, movies)

    def _refresh_all(self):
        self._refresh_browse()
        self._refresh_favorites()
        self._refresh_history()

    # --- Actions ---
    def _on_play(self, movie: dict):
        self.player.play_movie(movie)
        self.history_service.log_watch(self.user_id, movie["id"])
        self._refresh_history()

    def _on_fav(self, movie: dict):
        self.history_service.toggle_favorite(self.user_id, movie["id"])
        self._refresh_all()

    def _on_logout(self):
        reply = QMessageBox.question(self, "Log out", "Log out of CineVault?")
        if reply == QMessageBox.StandardButton.Yes:
            self.logged_out = True
            self.close()
