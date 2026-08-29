import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from core import resource_path
from window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("无畏契约网络测速")
    app.setApplicationDisplayName("无畏契约网络测速")
    app.setWindowIcon(QIcon(resource_path("app.ico")))
    win = MainWindow()
    win.setWindowIcon(QIcon(resource_path("app.ico")))
    win.show()
    sys.exit(app.exec())
