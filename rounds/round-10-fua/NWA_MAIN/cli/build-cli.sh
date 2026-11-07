#!/bin/sh
# 构建 CLI/LINUX 成品：把顶层 main.py + NWA_SRC 源码树打成 nwa-cli.zip
set -e
cd "$(dirname "$0")/../../.."
OUT=NWA_MAIN/cli/nwa-cli.zip
rm -f "$OUT"
zip -r "$OUT" main.py NWA_SRC -x 'NWA_SRC/__pycache__/*' 2>/dev/null \
  || python3 - "$OUT" <<'PY'
import shutil, sys
shutil.make_archive(sys.argv[1].rsplit(".zip", 1)[0], "zip", root_dir=".",
                   base_dir=".")
PY
ls -l "$OUT"
echo "CLI/LINUX 成品: unzip nwa-cli.zip && python3 main.py --help"
