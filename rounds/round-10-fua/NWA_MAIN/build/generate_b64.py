# -*- coding: utf-8 -*-
"""生成 nwa_b64.h：把 NWA_SRC/*.py + main.py + nwa_gui.py 内嵌为 C 字符串，
供 build/nwa_app.c 编译单文件二进制（ELF 或 MinGW 交叉编译 exe）。

用法:
  python3 generate_b64.py <源码目录> [输出头文件]
  源码目录 = 含 main.py 与 NWA_SRC/ 的那一层（如 rounds/round-07-fua）

然后:
  gcc -O2 -I. -DENTRY='"main.py"' -o nwa-linux nwa_app.c          # ELF
  x86_64-w64-mingw32-gcc -O2 -I. -DENTRY='"main.py"' -o nwa-win.exe nwa_app.c  # exe
"""
import base64
import os
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "."
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "nwa_b64.h")

files = {}
main_py = os.path.join(root, "main.py")
if os.path.exists(main_py):
    files["main.py"] = main_py
gui = os.path.join(root, "NWA_MAIN", "gui", "nwa_gui.py")
if os.path.exists(gui):
    files["nwa_gui.py"] = gui
src = os.path.join(root, "NWA_SRC")
for dirpath, dns, fns in os.walk(src):
    dns[:] = [d for d in dns if d != "__pycache__"]
    for fn in fns:
        p = os.path.join(dirpath, fn)
        files["NWA_SRC/" + os.path.relpath(p, src)] = p

with open(out, "w") as f:
    f.write("/* 由 generate_b64.py 生成，内嵌 %d 个文件 */\n" % len(files))
    f.write("static const char NWA_B64[] =\n")
    for rel, p in sorted(files.items()):
        f.write('"%s\\t%s\\n"\n' % (rel, base64.b64encode(open(p, "rb").read()).decode()))
    f.write(";\n")
print("已生成 %s（%d 个文件, %d 字节）" % (out, len(files), os.path.getsize(out)))
