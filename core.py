import sys
import os
import random
import socket
import threading
import statistics
import time
from dataclasses import dataclass, field

from PySide6.QtCore import Qt, QObject, Signal, QRunnable, QThreadPool, QPoint, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QBrush, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSizePolicy, QGraphicsDropShadowEffect, QMessageBox, QDialog
)

PORT = 8181
NODES = [
    ("广东", "广东1", "119.147.190.224"),
    ("广东", "广东2", "183.47.120.86"),
    ("广东", "广东3", "183.60.79.106"),
    ("广东", "广东4", "14.22.9.152"),
    ("南京", "南京1", "49.65.30.206"),
    ("南京", "南京2", "58.217.183.63"),
    ("南京", "南京3", "49.65.30.210"),
    ("南京", "南京4", "222.94.109.246"),
    ("重庆", "重庆1", "113.249.150.19"),
    ("重庆", "重庆2", "113.250.170.205"),
    ("重庆", "重庆3", "113.250.170.109"),
    ("重庆", "重庆4", "113.250.2.102"),
    ("天津", "天津1", "42.81.21.205"),
    ("天津", "天津2", "42.81.179.209"),
    ("天津", "天津3", "42.81.21.208"),
    ("天津", "天津4", "123.151.48.219"),
]
REGIONS = ["广东", "南京", "重庆", "天津"]
REGION_COLORS = {
    "广东": "#65D6D1",
    "南京": "#C77DFF",
    "重庆": "#F6B84A",
    "天津": "#FF7474",
}
PAYLOAD_TEMPLATE = bytes.fromhex(
    "75b073b573cd4c130001c9409463d38b94af777932e4050044ec408b9b35f4000000aaaaaaaabbbbbbbb"
)


def resource_path(relative_path):
    """Return resource path for source mode and PyInstaller one-file mode."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


@dataclass
class Result:
    region: str
    name: str
    ip: str
    sent: int = 0
    received: int = 0
    rtts: list = field(default_factory=list)

    @property
    def loss(self):
        return 100.0 if self.sent == 0 else (self.sent - self.received) * 100.0 / self.sent
    @property
    def avg(self):
        return statistics.mean(self.rtts) if self.rtts else None
    @property
    def min(self):
        return min(self.rtts) if self.rtts else None
    @property
    def max(self):
        return max(self.rtts) if self.rtts else None
    @property
    def jitter(self):
        return statistics.pstdev(self.rtts) if len(self.rtts) >= 2 else 0.0

def build_payload(seq: int) -> bytes:
    p = bytearray(PAYLOAD_TEMPLATE)
    p[23] = seq & 0xFF
    ticks = time.perf_counter_ns()
    for i in range(7):
        p[24 + i] = (ticks >> (8 * i)) & 0xFF
    seed = (time.time_ns() ^ (seq * 7919)) & 0xFFFFFFFF
    rnd = random.Random(seed)
    for i in range(12, 17):
        p[i] = rnd.randrange(0, 256)
    return bytes(p)


class NodeSession:
    def __init__(self, region, name, ip, count, interval_ms, drain_seconds=2.0):
        self.region = region
        self.name = name
        self.ip = ip
        self.count = count
        self.interval_ms = interval_ms
        self.drain_seconds = drain_seconds
        self.remote = (ip, PORT)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.10)

        self.lock = threading.Lock()
        self.pending = {}
        self.seen = set()
        self.stop_event = threading.Event()

        self.result = Result(region, name, ip)
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)

    def start(self):
        self.recv_thread.start()

    def send_one(self, seq):
        payload = build_payload(seq)
        t0 = time.perf_counter()

        with self.lock:
            self.pending[payload] = t0
            self.result.sent += 1

        try:
            self.sock.sendto(payload, self.remote)
        except OSError:
            pass

    def _recv_loop(self):
        while not self.stop_event.is_set():
            try:
                data, addr = self.sock.recvfrom(4096)
                now = time.perf_counter()
            except socket.timeout:
                continue
            except OSError:
                break

            if not addr or addr[0] != self.ip or addr[1] != PORT:
                continue

            with self.lock:
                if data in self.seen:
                    continue

                t0 = self.pending.pop(data, None)
                if t0 is None:
                    continue

                self.seen.add(data)
                self.result.received += 1
                self.result.rtts.append((now - t0) * 1000.0)

    def finish(self):
        time.sleep(self.drain_seconds)
        self.stop_event.set()
        try:
            self.sock.close()
        except OSError:
            pass
        self.recv_thread.join(timeout=1.0)
        return self.result


def probe_node_async(region, name, ip, count, interval_ms):
    session = NodeSession(region, name, ip, count, interval_ms, drain_seconds=2.0)
    session.start()

    for seq in range(count):
        round_start = time.perf_counter()
        session.send_one(seq)

        elapsed = time.perf_counter() - round_start
        sleep_s = interval_ms / 1000.0 - elapsed
        if sleep_s > 0:
            time.sleep(sleep_s)

    return session.finish()


class WorkerSignals(QObject):
    result = Signal(object)
    done = Signal()


class Worker(QRunnable):
    def __init__(self, node, count, timeout_ms, gap_ms):
        super().__init__()
        self.node = node
        self.count = count
        self.timeout_ms = timeout_ms
        self.gap_ms = gap_ms
        self.signals = WorkerSignals()

    def run(self):
        region, name, ip = self.node
        result = probe_node_async(region, name, ip, self.count, self.gap_ms)
        self.signals.result.emit(result)
        self.signals.done.emit()
