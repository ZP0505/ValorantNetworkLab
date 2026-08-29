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
- 自带原创应用图标生成脚本，打包时自动生成 `app.ico`

## 默认参数

- 探测次数：50 次
- 超时时间：800 ms
- 探测间隔：60 ms

## 运行源码

```bash
pip install -r requirements.txt
python generate_icon.py
python main.py
```

`app.ico` 不提交到仓库，使用 `generate_icon.py` 在本地生成。

## 打包 EXE

1. 安装 Python 3.10+。
2. 可选：下载 Windows 版 UPX，并将 `upx.exe` 放到 `tools/upx/upx.exe`。
3. 双击 `build_optimized.bat`。
4. 脚本会自动安装依赖、生成图标并执行 PyInstaller。
5. 最终程序位于 `dist/ValorantNetworkLab.exe`。

没有 UPX 也可以正常打包，只是 EXE 体积会更大。

## 项目结构

```text
main.py                 程序入口
core.py                 UDP 测速核心
widgets.py              自定义 UI 组件
window.py               主窗口组合
window_ui.py            主界面布局与样式
window_logic.py         测速结果与网络评估逻辑
generate_icon.py        原创 EXE 图标生成器
ValorantNetworkLab.spec PyInstaller 精简配置
build_optimized.bat     Windows 一键打包脚本
version_info.txt        EXE 文件版本信息
```

## 技术说明

本工具的 UDP 丢包统计采用每个节点固定 socket、发送与接收分离、持续接收、payload 精确匹配，以及发送完成后的缓冲等待方式。

UI 中显示的“丢包率”更准确地说，是对应测速节点的 **UDP 探测未响应率**，不能完全等同于运营商链路的物理丢包率。

测速节点及探测行为来自对现有客户端网络测速行为的研究，未来可能因为服务端调整而失效。

## 免责声明

本项目为非官方开源工具，与 Riot Games、腾讯及《无畏契约》官方无隶属、授权或合作关系。

项目名称中的 Valorant / 无畏契约仅用于描述工具的适用场景。应用图标为本项目原创图标，不使用官方游戏 Logo。

## Author

by: 0xze
