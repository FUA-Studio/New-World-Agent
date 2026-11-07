#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NWA 顶层可运行入口（PR 规范：顶层 main.py → 源码在 NWA_SRC/）。

用法示例:
  python3 main.py --help
  python3 main.py first-boot
  python3 main.py self-upgrade --dry-run
  python3 main.py selftest
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "NWA_SRC"))

# 顶层入口与 NWA_SRC/main.py 同名，直接按模块名取实现：
# 脚本自身以 __main__ 运行，不会与 NWA_SRC/main 模块冲突。
import importlib
_impl = importlib.import_module("main", package=None)

if __name__ == "__main__":
    _impl.main()
