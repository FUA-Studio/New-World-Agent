# -*- coding: utf-8 -*-
"""NWA 主题配色：主色为深绿 (deep green) 与银灰 (silver gray)。

终端取色说明：
- 深绿：主色 #14532d（墨绿）/ #064e3b（深松绿），高亮 #2f855a
- 银灰：主色 #c0c0c0（silver），次级 #9ca3af / #808080（gray）
GUI/桌面成品（NWA_MAIN 内）沿用同一套 PALETTE。
"""

DEEP_GREEN = "#14532d"
DEEP_GREEN_2 = "#064e3b"
GREEN_ACCENT = "#2f855a"

SILVER_GRAY = "#c0c0c0"
GRAY_2 = "#9ca3af"
GRAY_3 = "#808080"

PALETTE = {
    "primary": DEEP_GREEN,          # deep green 主色
    "primary_dark": DEEP_GREEN_2,
    "accent": GREEN_ACCENT,
    "secondary": SILVER_GRAY,      # silver gray 主色
    "secondary_dim": GRAY_2,
    "bg_light": "#f4f4f4",
    "text_on_dark": SILVER_GRAY,
}

THEME_NAME = "deep-green-silver-gray"


def css_variables():
    """供 GUI/WEB 成品注入的 CSS 变量（主题与 CLI 共享）。"""
    return "\n".join("%s: %s;" % (k, v) for k, v in PALETTE.items())
