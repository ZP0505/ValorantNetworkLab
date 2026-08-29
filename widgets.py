import statistics
from PySide6.QtCore import Qt, QPoint, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QBrush
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect, QDialog
from core import REGIONS, REGION_COLORS

class MiniSparkline(QWidget):
    def __init__(self, color="#65D6D1"):
        super().__init__()
        self.values = []
        self.color = QColor(color)
        self.setMinimumHeight(54)

    def set_values(self, values):
        self.values = list(values[-30:])
        self.update()

    def paintEvent(self, event):
        if len(self.values) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        pad = 5
        lo, hi = min(self.values), max(self.values)
        span = max(hi - lo, 1.0)

        pts = []
        for i, v in enumerate(self.values):
            x = pad + (w - pad * 2) * i / (len(self.values) - 1)
            y = h - pad - (h - pad * 2) * ((v - lo) / span)
            pts.append((x, y))

        grad = QLinearGradient(0, 0, 0, h)
        c1 = QColor(self.color); c1.setAlpha(80)
        c2 = QColor(self.color); c2.setAlpha(0)
        grad.setColorAt(0, c1)
        grad.setColorAt(1, c2)

        from PySide6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(pts[0][0], h - pad)
        for x, y in pts:
            path.lineTo(x, y)
        path.lineTo(pts[-1][0], h - pad)
        path.closeSubpath()
        p.fillPath(path, QBrush(grad))

        p.setPen(QPen(self.color, 2))
        for a, b in zip(pts, pts[1:]):
            p.drawLine(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

class TrendChart(QWidget):
    def __init__(self, history):
        super().__init__()
        self.history = history
        self.setMinimumHeight(210)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        left, right, top, bottom = 42, 16, 18, 28

        p.setPen(QPen(QColor("#223039"), 1))
        for i in range(5):
            y = top + (h - top - bottom) * i / 4
            p.drawLine(left, int(y), w - right, int(y))

        vals = [v for arr in self.history.values() for v in arr]
        if not vals:
            p.setPen(QColor("#60737D"))
            p.drawText(0, 0, w, h, Qt.AlignCenter, "完成测速后显示趋势")
            return

        max_v = max(max(vals) * 1.18, 20)
        p.setPen(QColor("#71838C"))
        for i in range(5):
            value = max_v * (1 - i / 4)
            y = top + (h - top - bottom) * i / 4
            p.drawText(0, int(y - 8), left - 8, 16, Qt.AlignRight | Qt.AlignVCenter, f"{value:.0f}")

        max_len = max((len(x) for x in self.history.values()), default=2)
        max_len = max(max_len, 2)

        for region in REGIONS:
            arr = self.history[region][-30:]
            if not arr:
                continue
            color = QColor(REGION_COLORS[region])
            p.setPen(QPen(color, 2))
            pts = []
            for i, v in enumerate(arr):
                x = left + (w - left - right) * i / (max_len - 1)
                y = top + (h - top - bottom) * (1 - v / max(max_v, 1))
                pts.append((x, y))
            if len(pts) == 1:
                p.drawEllipse(int(pts[0][0] - 2), int(pts[0][1] - 2), 4, 4)
            else:
                for a, b in zip(pts, pts[1:]):
                    p.drawLine(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

class MetricCard(QFrame):
    def __init__(self, title, value="--", note=""):
        super().__init__()
        self.setObjectName("metricCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 13, 16, 13)
        lay.setSpacing(5)
        title_label = QLabel(title); title_label.setObjectName("muted")
        self.value = QLabel(value); self.value.setObjectName("metricValue")
        self.note = QLabel(note); self.note.setObjectName("subtle")
        lay.addWidget(title_label); lay.addWidget(self.value); lay.addWidget(self.note)

class RegionCard(QFrame):
    def __init__(self, region):
        super().__init__()
        self.setObjectName("regionCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 12, 15, 10)
        lay.setSpacing(6)

        top = QHBoxLayout()
        title = QLabel(region); title.setObjectName("regionTitle")
        self.badge = QLabel("等待测速"); self.badge.setObjectName("badge")
        top.addWidget(title); top.addStretch(); top.addWidget(self.badge)

        self.latency = QLabel("-- ms"); self.latency.setObjectName("regionLatency")
        self.detail = QLabel("最佳节点 --  ·  丢包 --  ·  抖动 --"); self.detail.setObjectName("subtle")
        self.spark = MiniSparkline(REGION_COLORS[region])

        lay.addLayout(top); lay.addWidget(self.latency); lay.addWidget(self.detail); lay.addWidget(self.spark)


class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None, normal="#D5F7F3", hover="#BFF0EA", pressed="#A6E4DD",
                 text_color="#071013"):
        super().__init__(text, parent)
        self.normal_color = QColor(normal)
        self.hover_color = QColor(hover)
        self.pressed_color = QColor(pressed)
        self.text_color = text_color
        self.current_color = QColor(normal)

        self.anim = QVariantAnimation(self)
        self.anim.setDuration(135)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.valueChanged.connect(self._apply_color)
        self._apply_color(self.current_color)

    def _apply_color(self, value):
        if isinstance(value, QColor):
            self.current_color = value
        c = self.current_color.name()
        self.setStyleSheet(
            "QPushButton {"
            f"background:{c}; color:{self.text_color};"
            "border:none; border-radius:8px; padding:0 18px;"
            "min-height:40px; font-weight:700;"
            "}"
        )

    def _animate_to(self, target):
        self.anim.stop()
        self.anim.setStartValue(self.current_color)
        self.anim.setEndValue(QColor(target))
        self.anim.start()

    def enterEvent(self, event):
        if self.isEnabled():
            self._animate_to(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.isEnabled():
            self._animate_to(self.normal_color)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.isEnabled() and event.button() == Qt.LeftButton:
            self._animate_to(self.pressed_color)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.isEnabled():
            if self.rect().contains(event.position().toPoint()):
                self._animate_to(self.hover_color)
            else:
                self._animate_to(self.normal_color)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        if enabled:
            self.current_color = QColor(self.normal_color)
        else:
            self.current_color = QColor("#243238")
        self._apply_color(self.current_color)


class TitleBar(QFrame):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.drag_pos = None
        self.setObjectName("titleBar")
        self.setFixedHeight(38)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 8, 0)
        lay.setSpacing(6)

        title = QLabel("无畏契约网络测速")
        title.setObjectName("windowTitle")
        lay.addWidget(title)
        lay.addStretch()

        self.min_btn = QPushButton("—")
        self.close_btn = QPushButton("×")
        for btn in (self.min_btn, self.close_btn):
            btn.setFixedSize(34, 28)
            btn.setObjectName("windowButton")
            btn.setCursor(Qt.PointingHandCursor)

        self.min_btn.clicked.connect(window.showMinimized)
        self.close_btn.clicked.connect(window.close)

        lay.addWidget(self.min_btn)
        lay.addWidget(self.close_btn)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag_pos = e.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and self.drag_pos is not None:
            self.window.move(e.globalPosition().toPoint() - self.drag_pos)
            e.accept()

    def mouseDoubleClickEvent(self, e):
        if self.window.isMaximized():
            self.window.showNormal()
        else:
            self.window.showMaximized()


class ResultDialog(QDialog):
    def __init__(self, parent, result):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setFixedWidth(520)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)

        panel = QFrame()
        panel.setObjectName("resultDialogPanel")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 150))
        panel.setGraphicsEffect(shadow)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(22, 20, 22, 18)
        lay.setSpacing(14)

        top = QHBoxLayout()

        badge = QLabel(result["title"])
        badge.setObjectName("resultBadge")

        close_btn = QPushButton("×")
        close_btn.setObjectName("dialogClose")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.accept)

        top.addWidget(badge)
        top.addStretch()
        top.addWidget(close_btn)

        title = QLabel("本次网络评估")
        title.setObjectName("dialogTitle")

        detail = QLabel(result["detail"])
        detail.setWordWrap(True)
        detail.setObjectName("dialogText")

        summary = QLabel(result["summary"])
        summary.setWordWrap(True)
        summary.setObjectName("dialogText")

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("dialogSeparator")

        info = QLabel(result.get("more", ""))
        info.setWordWrap(True)
        info.setObjectName("dialogInfo")

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        ok_btn = AnimatedButton(
            "知道了",
            normal="#D5F7F3",
            hover="#BFF0EA",
            pressed="#A6E4DD"
        )
        ok_btn.setFixedWidth(110)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)

        lay.addLayout(top)
        lay.addWidget(title)
        lay.addWidget(detail)
        lay.addWidget(summary)
        lay.addWidget(sep)
        lay.addWidget(info)
        lay.addLayout(btn_row)

        outer.addWidget(panel)

        styles = {
            "适合游玩": ("#89F2C7", "#143128", "#1E4A3B"),
            "可以游玩": ("#8FE1FF", "#112B36", "#214757"),
            "勉强可玩": ("#F6D06F", "#332712", "#5D4520"),
            "不适合游玩": ("#FF8A8A", "#38171A", "#603036"),
        }
        fg, bg, border = styles.get(result["title"], ("#A6B6BD", "#152229", "#22343C"))
        badge.setStyleSheet(
            f"color:{fg};"
            f"background:{bg};"
            f"border:1px solid {border};"
            "border-radius:9px;"
            "padding:6px 10px;"
            "font-size:12px;"
            "font-weight:700;"
        )

        self.setStyleSheet("""
        #resultDialogPanel {
            background: #0F171B;
            border: 1px solid #233139;
            border-radius: 14px;
        }
        #dialogTitle {
            color: #F4F7F8;
            font-size: 20px;
            font-weight: 700;
        }
        #dialogText {
            color: #C7D2D7;
            font-size: 12px;
            line-height: 1.5;
        }
        #dialogInfo {
            color: #8FA0A8;
            font-size: 11px;
            line-height: 1.5;
        }
        #dialogSeparator {
            color: #223039;
            background: #223039;
            max-height: 1px;
            border: none;
        }
        QPushButton#dialogClose {
            color: #81939B;
            background: transparent;
            border: none;
            border-radius: 7px;
            font-size: 17px;
        }
        QPushButton#dialogClose:hover {
            color: white;
            background: #19252B;
        }
        QPushButton#dialogClose:pressed {
            background: #24343C;
        }
        """)
