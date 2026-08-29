from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import QMainWindow
from core import REGIONS
from window_ui import MainWindowUI
from window_logic import MainWindowLogic

class MainWindow(QMainWindow, MainWindowUI, MainWindowLogic):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("无畏契约网络测速")
        self.resize(1360, 860)
        self.setMinimumSize(1180, 760)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.pool = QThreadPool.globalInstance()
        self.pending = 0
        self.results = {}
        self.history = {r: [] for r in REGIONS}

        self.build_ui()
        self.apply_styles()
        for card in self.region_cards.values():
            self.apply_badge_style(card.badge, '一般')
