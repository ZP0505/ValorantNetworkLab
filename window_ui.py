from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QGraphicsDropShadowEffect
from core import NODES, REGIONS, REGION_COLORS
from widgets import MetricCard, RegionCard, AnimatedButton, TitleBar, TrendChart

class MainWindowUI:
    def build_ui(self):
        outer = QWidget()
        outer.setObjectName("outer")
        self.setCentralWidget(outer)

        outer_lay = QVBoxLayout(outer)
        outer_lay.setContentsMargins(8, 8, 8, 8)
        outer_lay.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("shell")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 140))
        shell.setGraphicsEffect(shadow)
        outer_lay.addWidget(shell)

        root_lay = QVBoxLayout(shell)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        root_lay.addWidget(TitleBar(self))

        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(212)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 24, 18, 20)
        side.setSpacing(10)

        brand = QLabel("无畏契约\n网络测速")
        brand.setObjectName("brand")
        side.addWidget(brand)

        sub = QLabel("独立网络检测工具")
        sub.setObjectName("subtle")
        side.addWidget(sub)

        side.addSpacing(26)

        section = QLabel("监控")
        section.setObjectName("sideSection")
        side.addWidget(section)

        overview = QLabel("  ▦  测速总览")
        overview.setObjectName("sideActive")
        overview.setMinimumHeight(40)
        overview.setAlignment(Qt.AlignVCenter)
        side.addWidget(overview)

        side.addStretch()

        author = QLabel("by:0xze")
        author.setObjectName("author")
        side.addWidget(author)

        body_lay.addWidget(sidebar)

        content = QWidget()
        content.setObjectName("content")
        main = QVBoxLayout(content)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(14)

        header = QHBoxLayout()
        hb = QVBoxLayout()
        title = QLabel("网络测速面板"); title.setObjectName("pageTitle")
        desc = QLabel("实时检测广东、南京、重庆、天津 4 个区域的 16 个测速节点"); desc.setObjectName("subtle")
        hb.addWidget(title); hb.addWidget(desc)
        header.addLayout(hb); header.addStretch()

        self.count = self.make_combo(
            ["10 次（快速）", "20 次", "50 次（推荐）", "100 次", "200 次（精确）"],
            "50 次（推荐）"
        )
        self.timeout = self.make_combo(
            ["300 ms", "500 ms", "800 ms（推荐）", "1000 ms", "1500 ms"],
            "800 ms（推荐）"
        )
        self.gap = self.make_combo(
            ["20 ms", "40 ms", "60 ms（推荐）", "100 ms", "200 ms"],
            "60 ms（推荐）"
        )

        self.count.setToolTip("每个节点发送多少次 UDP 探测。次数越多，丢包率统计越准确。")
        self.timeout.setToolTip("保留为兼容参数；异步模型不会因单包超时立即判定丢包。最终以发送结束后的回包统计为准。")
        self.gap.setToolTip("两次探测之间的发送间隔。默认 60 ms，避免发送过于密集。")

        count_box = self.make_param_box("探测次数", self.count)
        timeout_box = self.make_param_box("超时时间", self.timeout)
        gap_box = self.make_param_box("探测间隔", self.gap)

        self.start_btn = AnimatedButton("开始测速")
        self.start_btn.setToolTip("开始同时检测 16 个节点")
        self.start_btn.clicked.connect(self.start_test)

        header.addLayout(count_box)
        header.addLayout(timeout_box)
        header.addLayout(gap_box)
        header.addWidget(self.start_btn, 0, Qt.AlignBottom)
        main.addLayout(header)

        metrics = QHBoxLayout(); metrics.setSpacing(12)
        self.metric_best = MetricCard("最佳区域", "--", "等待测速")
        self.metric_avg = MetricCard("全局平均延迟", "-- ms", "4 个区域")
        self.metric_loss = MetricCard("综合丢包率", "--", "UDP 回包")
        self.metric_jitter = MetricCard("平均抖动", "-- ms", "越低越稳定")
        for w in (self.metric_best, self.metric_avg, self.metric_loss, self.metric_jitter):
            metrics.addWidget(w)
        main.addLayout(metrics)

        middle = QHBoxLayout(); middle.setSpacing(12)

        region_wrap = QFrame(); region_wrap.setObjectName("panel")
        region_lay = QVBoxLayout(region_wrap); region_lay.setContentsMargins(14, 12, 14, 14); region_lay.setSpacing(10)
        region_title = QLabel("区域状态"); region_title.setObjectName("sectionTitle")
        region_lay.addWidget(region_title)

        rg = QGridLayout(); rg.setSpacing(10)
        self.region_cards = {}
        for i, region in enumerate(REGIONS):
            card = RegionCard(region)
            self.region_cards[region] = card
            rg.addWidget(card, i // 2, i % 2)
        region_lay.addLayout(rg)
        middle.addWidget(region_wrap, 3)

        trend_wrap = QFrame(); trend_wrap.setObjectName("panel")
        trend_lay = QVBoxLayout(trend_wrap); trend_lay.setContentsMargins(14, 12, 14, 12); trend_lay.setSpacing(8)

        legend = QHBoxLayout()
        trend_title = QLabel("区域延迟趋势"); trend_title.setObjectName("sectionTitle")
        legend.addWidget(trend_title); legend.addStretch()
        for region in REGIONS:
            dot = QLabel(f"● {region}")
            dot.setStyleSheet(f"color:{REGION_COLORS[region]}; font-size:11px;")
            legend.addWidget(dot)
        trend_lay.addLayout(legend)

        self.trend = TrendChart(self.history)
        trend_lay.addWidget(self.trend, 1)

        hint = QLabel("保留当前程序运行期间的每次测速结果")
        hint.setObjectName("subtle")
        trend_lay.addWidget(hint)
        middle.addWidget(trend_wrap, 2)
        main.addLayout(middle)

        table_panel = QFrame(); table_panel.setObjectName("panel")
        tl = QVBoxLayout(table_panel); tl.setContentsMargins(14, 11, 14, 13); tl.setSpacing(8)

        th = QHBoxLayout()
        table_title = QLabel("节点明细"); table_title.setObjectName("sectionTitle")
        self.status = QLabel("等待测速"); self.status.setObjectName("status")
        th.addWidget(table_title); th.addStretch(); th.addWidget(self.status)
        tl.addLayout(th)

        self.table = QTableWidget(len(NODES), 8)
        self.table.setHorizontalHeaderLabels(["节点", "区域", "IP 地址", "平均延迟", "最低", "最高", "抖动", "丢包率"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setCurrentCell(-1, -1)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(210)
        hv = self.table.horizontalHeader()
        hv.setSectionResizeMode(QHeaderView.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        for i, (region, name, ip) in enumerate(NODES):
            for j, value in enumerate([name, region, ip, "--", "--", "--", "--", "--"]):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
        tl.addWidget(self.table)
        main.addWidget(table_panel, 1)

        body_lay.addWidget(content, 1)
        root_lay.addWidget(body, 1)

    def make_param_box(self, title, widget):
        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        label = QLabel(title)
        label.setObjectName("paramLabel")

        lay.addWidget(label)
        lay.addWidget(widget)
        return lay

    def make_combo(self, items, current):
        box = QComboBox()
        box.addItems(items)
        box.setCurrentText(current)
        box.setMinimumWidth(160)
        box.setCursor(Qt.PointingHandCursor)
        return box

    def combo_number(box):
        text = box.currentText()
        digits = ""
        for ch in text:
            if ch.isdigit():
                digits += ch
            elif digits:
                break
        return int(digits) if digits else 0

    def apply_styles(self):
        self.setStyleSheet("""
        #outer { background: transparent; }
        #shell {
            background: #0B1115;
            border: 1px solid #1A252B;
            border-radius: 16px;
        }
        #titleBar {
            background: rgba(12,18,22,245);
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
            border-bottom: 1px solid #172229;
        }
        #windowTitle {
            color: #B9C6CC;
            font-size: 12px;
        }
        QPushButton#windowButton {
            color: #95A4AB;
            background: transparent;
            border: none;
            border-radius: 7px;
            font-size: 15px;
        }
        QPushButton#windowButton:hover { background: #182228; color: white; }
        QPushButton#windowButton:pressed { background: #223138; color: #CFF8F4; }

        * {
            font-family: "Microsoft YaHei UI", "Segoe UI";
            font-size: 13px;
        }
        #content { background: #0B1115; }
        #sidebar {
            background: #080D10;
            border-right: 1px solid #172229;
            border-bottom-left-radius: 16px;
        }
        #brand {
            color: #F4F7F8;
            font-size: 20px;
            font-weight: 800;
        }
        #pageTitle {
            color: #F4F7F8;
            font-size: 25px;
            font-weight: 700;
        }
        #sectionTitle, #regionTitle {
            color: #EDF2F4;
            font-size: 14px;
            font-weight: 700;
        }
        #subtle { color: #70838D; font-size: 11px; }
        #paramLabel {
            color: #70838D;
            font-size: 10px;
            font-weight: 600;
            padding-left: 2px;
        }
        #sideSection { color: #61727B; font-size: 10px; font-weight: 600; }
        #sideActive {
            color: #DDF5F4;
            background: #152229;
            border-radius: 8px;
            padding-left: 8px;
            font-weight: 600;
        }
        #author {
            color: #7F929B;
            font-size: 12px;
            font-weight: 600;
            padding-bottom: 2px;
        }
        QComboBox {
            background: #10181D;
            color: #DDE6E9;
            border: 1px solid #25333A;
            border-radius: 8px;
            padding: 7px 12px;
            min-height: 26px;
        }
        QComboBox:hover {
            border: 1px solid #3A515C;
            background: #121D22;
        }
        QComboBox:focus {
            border: 1px solid #5F9E9A;
        }
        QComboBox::drop-down {
            border: none;
            width: 26px;
        }
        QComboBox QAbstractItemView {
            background: #10181D;
            color: #DDE6E9;
            border: 1px solid #26363E;
            selection-background-color: #183038;
            selection-color: #EAF8F7;
            outline: 0;
            padding: 5px;
        }

        QToolTip {
            color: #DDE6E9;
            background: #111A1F;
            border: 1px solid #2B3A42;
            padding: 6px 8px;
        }

        #metricCard, #regionCard, #panel {
            background: rgba(16,23,27,238);
            border: 1px solid #1D2A31;
            border-radius: 11px;
        }
        #metricValue {
            color: #F0F5F6;
            font-size: 24px;
            font-weight: 700;
        }
        #regionLatency {
            color: #CDF7F3;
            font-size: 27px;
            font-weight: 700;
        }
        #badge {
            color: #A6B6BD;
            background: #152229;
            border: 1px solid #22343C;
            border-radius: 8px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 600;
        }
        #status { color: #6F858F; font-size: 11px; }

        QTableWidget {
            background: #0D1418;
            color: #C6D2D7;
            border: none;
            border-radius: 7px;
            gridline-color: transparent;
        }
        QTableWidget::item {
            padding: 6px;
            border-bottom: 1px solid #172228;
        }
        QTableWidget::item:focus {
            outline: none;
            border: none;
            border-bottom: 1px solid #172228;
        }
        QHeaderView::section {
            background: #111A1F;
            color: #748891;
            border: none;
            border-bottom: 1px solid #25343B;
            padding: 8px;
            font-weight: 600;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 7px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #293A42;
            border-radius: 3px;
            min-height: 30px;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical { height: 0; }
        """)
