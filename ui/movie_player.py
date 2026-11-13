"""Movie player — embedded QMediaPlayer, plays trailers in UI (no redirect)."""
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QMessageBox
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt, QEvent
from backend.services.playback_service import PlaybackService


class MoviePlayer(QWidget):
    def __init__(self, playback: PlaybackService, parent=None):
        super().__init__(parent)
        self.playback = playback
        self._build()
        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setVideoOutput(self.video)
        self.player.setAudioOutput(self.audio_output)
        self.player.positionChanged.connect(self._update_position)
        self.player.durationChanged.connect(self._update_duration)
        self.player.playbackStateChanged.connect(self._on_playback_state)
        self.player.errorOccurred.connect(self._on_error)
        self.setVisible(False)
        self._is_fullscreen = False
        self._dashboard_parent = None
        self._dashboard_layout = None
        self.video.installEventFilter(self)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        self.title_label = QLabel("No trailer selected")
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 700; padding: 8px;")
        header.addWidget(self.title_label, 1)
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background: #26262f; padding: 6px 12px;")
        close_btn.clicked.connect(self._stop_and_hide)
        header.addWidget(close_btn)
        lay.addLayout(header)

        self.video = QVideoWidget()
        self.video.setMinimumHeight(300)
        self.video.setStyleSheet("background: black; border-radius: 8px;")
        lay.addWidget(self.video, 1)

        ctrl = QHBoxLayout()
        self.play_pause = QPushButton("Play")
        self.play_pause.setFixedWidth(90)
        self.play_pause.clicked.connect(self._toggle_play)
        ctrl.addWidget(self.play_pause)

        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.sliderMoved.connect(lambda p: self.player.setPosition(p))
        ctrl.addWidget(self.seek, 1)

        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setFixedWidth(100)
        ctrl.addWidget(self.time_label)

        self.mute_btn = QPushButton("Mute")
        self.mute_btn.clicked.connect(self._toggle_mute)
        ctrl.addWidget(self.mute_btn)

        self.full_btn = QPushButton("Fullscreen")
        self.full_btn.clicked.connect(self._toggle_fullscreen)
        ctrl.addWidget(self.full_btn)
        lay.addLayout(ctrl)

    def play_movie(self, movie: dict, tmdb_id: int | None = None):
        title = movie["title"]
        year = movie.get("year", 0)
        genre = movie.get("genre", "")
        self.title_label.setText(f"Now Playing: {title} ({year}) — {genre}")
        path = self.playback.get_trailer_url(movie["id"], tmdb_id)
        if not path:
            QMessageBox.warning(self, "No trailer", f"No trailer available for {title}.")
            return
        # Local file path → QUrl.fromLocalFile; http(s) URL → QUrl
        if os.path.exists(path):
            url = QUrl.fromLocalFile(path)
        else:
            url = QUrl(path)
        self.player.setSource(url)
        self.player.play()
        self.setVisible(True)

    def _toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _toggle_mute(self):
        self.audio_output.setMuted(not self.audio_output.isMuted())
        self.mute_btn.setText("Muted" if self.audio_output.isMuted() else "Mute")

    def _toggle_fullscreen(self):
        if not self._is_fullscreen:
            # Save parent and detach from dashboard layout
            self._dashboard_parent = self.parentWidget()
            if self._dashboard_parent:
                self._dashboard_layout = self._dashboard_parent.layout()
                if self._dashboard_layout:
                    self._dashboard_layout.removeWidget(self)

            # Reparent to desktop so we become a top-level window
            self.setParent(None)
            self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
            self.showNormal()
            self.show()
            self.showFullScreen()
            self._is_fullscreen = True
        else:
            # Restore to dashboard layout
            self.showNormal()
            self.setWindowFlags(Qt.Widget)

            if self._dashboard_parent and self._dashboard_layout:
                self._dashboard_layout.addWidget(self)
                self.setParent(self._dashboard_parent)
                self._dashboard_parent.show()

            self._is_fullscreen = False
            # Re-establish video output after reparenting
            self.player.setVideoOutput(self.video)
            # Re-establish video output after reparenting
            self.player.setVideoOutput(self.video)

    def eventFilter(self, obj, event):
        if obj == self.video and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape and self._is_fullscreen:
                self._toggle_fullscreen()
                return True
        return super().eventFilter(obj, event)

    def _stop_and_hide(self):
        self.player.stop()
        self.player.setSource(QUrl())
        self.setVisible(False)

    def _update_position(self, pos: int):
        if not self.seek.isSliderDown():
            self.seek.setValue(pos)
        self._update_time()

    def _update_duration(self, dur: int):
        self.seek.setRange(0, dur if dur > 0 else 0)
        self._update_time()

    def _update_time(self):
        fmt = lambda ms: f"{ms // 60000}:{(ms % 60000) // 1000:02d}"
        self.time_label.setText(f"{fmt(self.player.position())} / {fmt(self.player.duration())}")

    def _on_playback_state(self, state):
        self.play_pause.setText("Pause" if state == QMediaPlayer.PlaybackState.PlayingState else "Play")

    def _on_error(self, err, msg):
        QMessageBox.warning(self, "Playback error", f"Could not play trailer.\n{msg}\n\nCheck your internet connection.")
