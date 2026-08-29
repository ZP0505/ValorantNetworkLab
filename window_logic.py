import statistics
from PySide6.QtCore import Qt
from core import NODES, REGIONS, Worker, Result
from widgets import ResultDialog

class MainWindowLogic:
    def start_test(self):
        self.results.clear()
        self.pending = len(NODES)
        self.start_btn.setEnabled(False)
        self.status.setText("正在测速…")
        self.status.setStyleSheet("color:#65D6D1;")
        for row in range(self.table.rowCount()):
            for col in range(3, 8):
                self.table.item(row, col).setText("--")

        for card in self.region_cards.values():
            card.badge.setText("等待测速")
            self.apply_badge_style(card.badge, "一般")
            card.latency.setText("-- ms")
            card.detail.setText("最佳节点 --  ·  丢包 --  ·  抖动 --")

        for node in NODES:
            worker = Worker(node, self.combo_number(self.count), self.combo_number(self.timeout), self.combo_number(self.gap))
            worker.signals.result.connect(self.on_result)
            worker.signals.done.connect(self.on_done)
            self.pool.start(worker)

    def on_result(self, r: Result):
        self.results[r.name] = r
        row = next(i for i, n in enumerate(NODES) if n[1] == r.name)
        vals = [
            "--" if r.avg is None else f"{r.avg:.1f} ms",
            "--" if r.min is None else f"{r.min:.1f} ms",
            "--" if r.max is None else f"{r.max:.1f} ms",
            f"{r.jitter:.1f} ms",
            f"{r.loss:.1f}%"
        ]
        for idx, value in enumerate(vals, start=3):
            self.table.item(row, idx).setText(value)
        self.update_region(r.region)

    def on_done(self):
        self.pending -= 1
        if self.pending <= 0:
            self.start_btn.setEnabled(True)
            self.status.setText("测速完成")
            self.status.setStyleSheet("color:#86EFAC;")
            self.update_global_metrics()
            self.trend.update()
            self.show_result_dialog()

    def update_region(self, region):
        rs = [r for r in self.results.values() if r.region == region]
        if not rs:
            return
        good = [r for r in rs if r.avg is not None]
        card = self.region_cards[region]
        if not good:
            card.latency.setText("超时")
            card.badge.setText("不可达")
            card.detail.setText("没有收到 UDP 回包")
            return

        avg = statistics.mean(r.avg for r in good)
        loss = sum(r.sent - r.received for r in rs) * 100 / max(1, sum(r.sent for r in rs))
        jitter = statistics.mean(r.jitter for r in good)
        best = min(good, key=lambda x: x.avg)
        card.latency.setText(f"{avg:.1f} ms")
        card.detail.setText(f"最佳 {best.name}  ·  丢包 {loss:.1f}%  ·  抖动 {jitter:.1f} ms")

        if loss >= 10:
            badge = "丢包严重"
        elif loss > 1:
            badge = "存在丢包"
        elif avg <= 20:
            badge = "极佳"
        elif avg <= 40:
            badge = "良好"
        elif avg <= 70:
            badge = "一般"
        else:
            badge = "一般"
        card.badge.setText(badge)
        self.apply_badge_style(card.badge, badge)

    def update_global_metrics(self):
        good = [r for r in self.results.values() if r.avg is not None]
        if not good:
            self.metric_best.value.setText("--")
            self.metric_avg.value.setText("-- ms")
            self.metric_loss.value.setText("100%")
            self.metric_jitter.value.setText("-- ms")
            return

        region_avgs = {}
        for region in REGIONS:
            rs = [r for r in good if r.region == region]
            if rs:
                region_avgs[region] = statistics.mean(r.avg for r in rs)

        for region, avg in region_avgs.items():
            self.history[region].append(avg)
            self.region_cards[region].spark.set_values(self.history[region])

        best_region = min(region_avgs, key=region_avgs.get)
        global_avg = statistics.mean(r.avg for r in good)
        global_loss = sum(r.sent - r.received for r in self.results.values()) * 100 / max(1, sum(r.sent for r in self.results.values()))
        global_jitter = statistics.mean(r.jitter for r in good)

        self.metric_best.value.setText(best_region)
        self.metric_best.note.setText(f"{region_avgs[best_region]:.1f} ms")
        self.metric_avg.value.setText(f"{global_avg:.1f} ms")
        self.metric_loss.value.setText(f"{global_loss:.1f}%")
        self.metric_jitter.value.setText(f"{global_jitter:.1f} ms")

    def apply_badge_style(self, label, level):
        color_map = {
            "极佳": ("#89F2C7", "#143128", "#1E4A3B"),
            "良好": ("#8FE1FF", "#112B36", "#214757"),
            "一般": ("#F6D06F", "#332712", "#5D4520"),
            "存在丢包": ("#FFBC73", "#372412", "#5C3819"),
            "丢包严重": ("#FF8A8A", "#38171A", "#603036"),
            "不可达": ("#FF8A8A", "#38171A", "#603036"),
        }
        fg, bg, border = color_map.get(level, ("#A6B6BD", "#152229", "#22343C"))
        label.setStyleSheet(
            f"color:{fg};"
            f"background:{bg};"
            f"border:1px solid {border};"
            "border-radius:8px;"
            "padding:4px 8px;"
            "font-size:11px;"
            "font-weight:600;"
        )

    def evaluate_network(self):
        region_data = []
        for region in REGIONS:
            rs = [r for r in self.results.values() if r.region == region and r.avg is not None]
            if not rs:
                continue

            avg = statistics.mean(r.avg for r in rs)
            loss = sum(r.sent - r.received for r in rs) * 100 / max(1, sum(r.sent for r in rs))
            jitter = statistics.mean(r.jitter for r in rs)
            best = min(rs, key=lambda x: x.avg)

            region_data.append({
                "region": region,
                "avg": avg,
                "loss": loss,
                "jitter": jitter,
                "best": best
            })

        if not region_data:
            return {
                "title": "不适合游玩",
                "detail": "本次测速没有拿到有效结果，无法判断当前网络质量。",
                "summary": "建议稍后重新测速。",
            }

        best_region = min(region_data, key=lambda x: (x["avg"], x["jitter"], x["loss"]))
        avg = best_region["avg"]
        jitter = best_region["jitter"]
        loss = best_region["loss"]
        region_name = best_region["region"]
        best_node = best_region["best"].name

        if loss >= 5 or jitter >= 8 or avg >= 85:
            title = "不适合游玩"
            detail = (
                f"最佳区域为 {region_name}（{best_node}），但综合表现不理想："
                f"平均延迟 {avg:.1f} ms，抖动 {jitter:.1f} ms，丢包率 {loss:.1f}%。"
            )
            summary = (
                "《无畏契约》使用 128 tick 服务器，对抖动和丢包都比较敏感。"
                "即使平均延迟不是特别高，只要抖动偏大或存在明显丢包，实际手感也会发飘、对枪不稳定。"
            )
        elif loss >= 2 or jitter >= 5 or avg >= 60:
            title = "勉强可玩"
            detail = (
                f"最佳区域为 {region_name}（{best_node}），"
                f"平均延迟 {avg:.1f} ms，抖动 {jitter:.1f} ms，丢包率 {loss:.1f}%。"
            )
            summary = (
                "当前网络可以进入游戏，但体验可能不稳定。"
                "对于《无畏契约》这类 128 tick 的 FPS，抖动和丢包会明显影响拉枪、对枪和定位反馈。"
            )
        elif loss > 0.5 or jitter >= 3 or avg >= 40:
            title = "可以游玩"
            detail = (
                f"最佳区域为 {region_name}（{best_node}），"
                f"平均延迟 {avg:.1f} ms，抖动 {jitter:.1f} ms，丢包率 {loss:.1f}%。"
            )
            summary = (
                "当前网络整体适合进行《无畏契约》游玩。"
                "延迟和丢包控制得不错，虽然仍有轻微波动，但大多数对局中不会成为明显问题。"
            )
        else:
            title = "适合游玩"
            detail = (
                f"最佳区域为 {region_name}（{best_node}），"
                f"平均延迟 {avg:.1f} ms，抖动 {jitter:.1f} ms，丢包率 {loss:.1f}%。"
            )
            summary = (
                "当前网络非常适合《无畏契约》。"
                "对于 128 tick 服务器来说，稳定低抖动比单纯低延迟更重要；你现在这组数据已经属于比较理想的状态。"
            )

        more = (
            "判断重点：\n"
            "1. 抖动：优先级最高，数值越低越稳定。\n"
            "2. 丢包率：有明显丢包会直接影响手感。\n"
            "3. 平均延迟：决定基础响应速度。\n\n"
            f"推荐区域：{region_name}\n"
            f"推荐节点：{best_node}"
        )

        return {
            "title": title,
            "detail": detail,
            "summary": summary,
            "more": more,
        }

    def show_result_dialog(self):
        result = self.evaluate_network()
        dialog = ResultDialog(self, result)
        dialog.exec()
