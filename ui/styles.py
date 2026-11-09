"""Dark vault theme — one place to change colors later."""

DARK_THEME = """
QMainWindow, QDialog { background: #0f0f14; color: #e4e4e7; font-family: Segoe UI, sans-serif; }
QLabel { color: #e4e4e7; }
QLineEdit { background: #1c1c24; border: 1px solid #2d2d3a; border-radius: 6px; padding: 8px; color: #fff; }
QLineEdit:focus { border: 1px solid #e50914; }
QComboBox { background: #1c1c24; border: 1px solid #2d2d3a; border-radius: 6px; padding: 6px 8px; color: #fff; }
QPushButton { background: #e50914; color: white; border: none; border-radius: 6px; padding: 10px; font-weight: bold; }
QPushButton:hover { background: #f6121d; }
QPushButton.secondary { background: #26262f; border: 1px solid #3a3a48; }
QPushButton.secondary:hover { background: #33333f; }
QScrollArea { background: transparent; border: none; }
QFrame { background: #1a1a22; border: 1px solid #2a2a36; border-radius: 10px; }
QSlider::groove:horizontal { height: 6px; background: #2d2d3a; border-radius: 3px; }
QSlider::handle:horizontal { background: #e50914; width: 14px; height: 14px; border-radius: 7px; margin: -4px 0; }
"""
