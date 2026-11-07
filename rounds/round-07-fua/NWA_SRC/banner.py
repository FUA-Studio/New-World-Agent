# -*- coding: utf-8 -*-
"""NWA 主题横幅：深绿 + 银灰（deep green + silver gray）。"""
import os
import sys

_NO_COLOR = os.environ.get("NO_COLOR")
_IS_TTY = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
ENABLE_COLOR = _NO_COLOR is None and _IS_TTY

_DEEP = "\x1b[38;2;20;83;45m"      # 深绿 #14532d
_SIL = "\x1b[38;2;192;192;192m"    # 银灰 #c0c0c0
if not ENABLE_COLOR:
    _DEEP = ""
    _SIL = ""

GREEN = _DEEP                       # 主色 deep green
GREEN_DARK = "\x1b[38;2;6;78;59m" if ENABLE_COLOR else ""
SILVER = _SIL                      # 主色 silver gray
SILVER_DIM = "\x1b[38;2;140;140;140m" if ENABLE_COLOR else ""
RESET = "\x1b[0m" if ENABLE_COLOR else ""
BOLD = "\x1b[1m" if ENABLE_COLOR else ""
DIM = "\x1b[2m" if ENABLE_COLOR else ""


def _c(code, s):
    return (code + s + (RESET if ENABLE_COLOR else "")) if code else s


def cyan(s):
    return _c(("\x1b[38;2;0;190;210m" if ENABLE_COLOR else ""), s)


def yellow(s):
    return _c(("\x1b[38;2;230;200;80m" if ENABLE_COLOR else ""), s)


def red(s):
    return _c(("\x1b[38;2;220;90;90m" if ENABLE_COLOR else ""), s)


def gray(s):
    return _c(SILVER_DIM, s)


def green(s):
    return _c(GREEN, s)


def bold(s):
    return _c(BOLD, s)


_lines = [
    "   ####  ##### #####  ####  #    #  #    #  #####  #   #",
    "  #      #    #   # #    # ##   #  #    # #    # #   #  ",
    "  #      #    #   # #      # #  #   #    # #    # #   #  ",
    "  #   ## #    #####  #  #  # #  #   #####  #    ##  #   ",
    "   ##### #    #   #  ####   ##  #   #    #  ##### #   # ",
]
BANNER = SILVER + "\n".join(_lines) + RESET + "\n"
BANNER += GREEN_DARK + "   NWA · New World Agent · deep green + silver gray theme\n"
BANNER += GREEN_DARK + "   self-upgrade (PR, human review only) · encrypted token store · rollback\n"
