NWA round-10 交付说明（2026-10-25）
一 LINUX 真双成品 nwa-linux 与 nwa-gui-linux 已重建，内嵌源码自解包
二 GUI 版修复：缺 python3-tk 时不再报错退出，自动降级命令行版并透传参数，返回码 0
三 验收：真实测试文件八项全过，证据见 VERIFY.md，入口 help 返回 0
四 Windows exe：宿主 32 位 Python 3.14 无 PyInstaller、MinGW 两头皆缺，本轮未出，构建脚本与一行命令已备（build 目录）
五 Android APK：两头无 SDK，按既定口径如实说明，android 目录留一键构建脚本
六 试跑 nwa6 已按放宽超时 5400/3600 重开，失败计数清零，自恢复链路可继续接力
