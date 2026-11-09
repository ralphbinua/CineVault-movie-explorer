"""Movie player — embedded QMediaPlayer, plays trailers in UI (no redirect)."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QMessageBox
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt

# Dummy trailer MP4s for Step 5 UI only
TRAILER_URLS = {
    "Big Buck Bunny": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "Sintel": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    "Tears of Steel": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    "Elephants Dream": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    "For Bigger Blazes": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "For Bigger Escapes": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "For Bigger Fun": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
    "For Bigger Joyrides": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
    "Neon Horizon": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    "Blender Vault": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "Subaru: Street & Dirt": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
    "For Bigger Meltdowns": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
}
DEFAULT_URL = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"


class MoviePlayer(QWidget):
    """Player panel above the grid. Hidden until a trailer is played."""

    def __init__(self, parent=None):
        super().__init__(parent)
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

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        self.title_label = QLabel("▶ No trailer selected")
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 700; padding: 8px;")
        header.addWidget(self.title_label, 1)
        close_btn = QPushButton("✕ Close")
        close_btn.setStyleSheet("background: #26262f; padding: 6px 12px;")
        close_btn.clicked.connect(self._stop_and_hide)
        header.addWidget(close_btn)
        lay.addLayout(header)

        self.video = QVideoWidget()
        self.video.setMinimumHeight(300)
        self.video.setStyleSheet("background: black; border-radius: 8px;")
        lay.addWidget(self.video, 1)

        ctrl = QHBoxLayout()
        self.play_pause = QPushButton("▶ Play")
        self.play_pause.setFixedWidth(90)
        self.play_pause.clicked.connect(self._toggle_play)
        ctrl.addWidget(self.play_pause)

        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.sliderMoved.connect(lambda p: self.player.setPosition(p))
        ctrl.addWidget(self.seek, 1)

        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setFixedWidth(100)
        ctrl.addWidget(self.time_label)

        self.mute_btn = QPushButton("🔊")
        self.mute_btn.setFixedWidth(44)
        self.mute_btn.clicked.connect(self._toggle_mute)
        ctrl.addWidget(self.mute_btn)

        self.full_btn = QPushButton("⛶")
        self.full_btn.setFixedWidth(44)
        self.full_btn.clicked.connect(self._toggle_fullscreen)
        ctrl.addWidget(self.full_btn)
        lay.addLayout(ctrl)

    # Public API — dashboard calls this
    def play_movie(self, movie: dict):
        title = movie["title"]
        self.title_label.setText(f"▶ Now Playing: {title} ({movie['year']}) — {movie['genre']}")
        url = TRAILER_URLS.get(title, DEFAULT_URL)
        self.player.setSource(QUrl(url))
        self.player.play()
        self.setVisible(True)

    # Internals
    def _toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _toggle_mute(self):
        self.audio_output.setMuted(not self.audio_output.isMuted())
        self.mute_btn.setText("🔇" if self.audio_output.isMuted() else "🔊")

    def _toggle_fullscreen(self):
        if self.video.isFullScreen():
            self.video.setWindowState(Qt.WindowState.WindowNoState)
            self.video.showNormal()
        else:
            self.video.setWindowState(Qt.WindowState.WindowFullScreen)
            self.video.showFullScreen()

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
        self.play_pause.setText("⏸ Pause" if state == QMediaPlayer.PlaybackState.PlayingState else "▶ Play")

    def _on_error(self, err, msg):
        QMessageBox.warning(self, "Playback error", f"Could not play trailer.\n{msg}\n\nCheck your internet connection.")
