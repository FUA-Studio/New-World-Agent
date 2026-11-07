#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NWA 桌面 GUI 成品（tkinter）：横幅 / 会话 / 自检。

主题与 CLI 共用 NWA_SRC/theme.py：deep green #14532d + silver gray #c0c0c0。
用法: python3 nwa_gui.py   （需 python3-tk）
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# 兼容三种布局：仓库内 NWA_MAIN/gui/、单文件包根目录、~/.nwa_pkg
for _cand in (os.path.join(_HERE, "NWA_SRC"),
              os.path.join(_HERE, "..", "NWA_SRC"),
              os.path.join(_HERE, "..", "..", "NWA_SRC"),
              os.path.join(os.path.expanduser("~"), ".nwa_pkg", "NWA_SRC")):
    if os.path.isdir(_cand):
        sys.path.insert(0, _cand)
        break

try:
    import tkinter as tk
except Exception:
    print("需要 python3-tk（sudo apt install python3-tk）")
    sys.exit(1)

from theme import DEEP_GREEN, DEEP_GREEN_2, SILVER_GRAY, GRAY_2
from banner import BANNER
import main as nwa_impl


def _run_selftest():
    from selftest import run_all
    res = run_all()
    print("self-test 结果:", {k: ("PASS" if v else "FAIL") for k, v in res.items()})
    return res


def main():
    root = tk.Tk()
    root.title("NWA · New World Agent")
    root.configure(bg=SILVER_GRAY)
    root.geometry("720x480")

    tk.Label(root, text=BANNER.splitlines()[0] if BANNER else "NWA",
             bg=DEEP_GREEN, fg="white", font=("Courier", 12)).pack(pady=8)

    box = tk.Text(root, width=90, height=18, bg=DEEP_GREEN_2, fg="white",
                  insertbackground=SILVER_GRAY)
    box.pack(padx=10, pady=4)

    def send():
        import llm
        q = entry.get().strip()
        if not q:
            return
        box.insert("end", "\n你: %s\n" % q)
        box.insert("end", "NWA: %s\n" % llm.call_llm(q))
        entry.delete(0, "end")
        box.see("end")

    entry = tk.Entry(root, width=90)
    entry.bind("<Return>", lambda e: send())
    entry.pack(padx=10)

    tk.Button(root, text="selftest", bg=GRAY_2, command=_run_selftest).pack(side="left", padx=6, pady=6)
    tk.Button(root, text="banner", bg=GRAY_2,
              command=lambda: box.insert("end", BANNER + "\n")).pack(side="left")
    tk.Button(root, text="发送", bg=DEEP_GREEN, command=send).pack(side="left", padx=6)
    root.mainloop()


if __name__ == "__main__":
    main()
