# ValorantNetworkLab

一个面向《无畏契约》网络质量检测的开源 Windows 桌面工具。

## 功能

- 独立测试广东、南京、重庆、天津 4 个区域共 16 个 UDP 测速节点
- 测量平均延迟、最低延迟、最高延迟、抖动和 UDP 探测未响应率
- 使用异步 UDP 收包模型，避免旧版 `send → recv → timeout` 带来的假丢包
- 深色现代化 PySide6 UI
- 测速完成后给出“适合游玩 / 可以游玩 / 勉强可玩 / 不适合游玩”判断
- 支持 PyInstaller 单文件 EXE 打包
- 支持 UPX 进一步压缩体积

## 默认参数

- 探测次数：50 次
- 超时时间：800 ms
- 探测间隔：60 ms

## 运行源码

```bash
pip install -r requirements.txt
python main.py
```

## 打包 EXE

1. 下载 Windows 版 UPX。
2. 将 `upx.exe` 放到 `tools/upx/upx.exe`。
3. 双击 `build_optimized.bat`。
4. 最终程序位于 `dist/ValorantNetworkLab.exe`。

即使没有 UPX，也可以继续打包，只是 EXE 会稍大。

## 技术说明

本工具的 UDP 丢包统计采用每个节点固定 socket、发送与接收分离、持续接收、payload 精确匹配以及发送完成后的缓冲等待方式。UI 中显示的“丢包率”更准确地说是对应测速节点的 UDP 探测未响应率，不能完全等同于运营商链路的物理丢包率。

## 免责声明

本项目为非官方开源工具，与 Riot Games、腾讯及《无畏契约》官方无隶属或合作关系。节点和协议行为可能随官方服务变化而变化。

## Author

by: 0xze
