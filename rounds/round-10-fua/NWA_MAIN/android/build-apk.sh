#!/bin/sh
# 构建 ANDROID APK 成品：把 NWA_SRC 打包进 APK 资源 (assets)，
# 附带一个最小的 Android 终端壳 (terminal app) 用于在 Termux/设备内运行 CLI。
# 依赖 Android SDK (aapt2/d8/apksigner)。缺失时降级为 assets bundle + 安装说明。
set -e
cd "$(dirname "$0")/../../.."
SRC=NWA_SRC
OUT=NWA_MAIN/android

echo "== 收集 NWA 源码 assets =="
rm -rf "$OUT/assets"; mkdir -p "$OUT/assets/nwa"
cp -r "$SRC" "$OUT/assets/nwa/NWA_SRC"
cp main.py "$OUT/assets/nwa/main.py"

if command -v aapt2 >/dev/null 2>&1 && command -v d8 >/dev/null 2>&1; then
  echo "== 具备 Android SDK，产出真 APK =="
  # 极简壳：单 Activity 起 Termux chroot 运行 python3 main.py
  # （完整壳工程在 NWA_MAIN/android/app/ 下；此处给出资源打包 + 签名骨架）
  aapt2 compile --dir "$OUT/app/res" -o "$OUT/res.zip" 2>/dev/null || true
  aapt2 link -o "$OUT/nwa.apk.unsigned" -0 assets \
     "$OUT/app/AndroidManifest.xml" 2>/dev/null || true
  echo "请补全 NWA_MAIN/android/app/ 壳工程后用 aapt2/d8/apksigner 出包。"
  echo "assets bundle 已就绪: $OUT/assets/nwa"
else
  echo "== 无 Android SDK，降级产出 assets bundle =="
  if command -v zip >/dev/null 2>&1; then
    (cd "$OUT/assets" && zip -qr "$OUT/nwa-android-assets.zip" nwa)
    echo "已产出 $OUT/nwa-android-assets.zip（Termux 解压后: python3 nwa/main.py）"
  else
    echo "无 zip 工具：保留 $OUT/assets/nwa 目录供手动打包"
  fi
fi
ls -l "$OUT" | sed -n 1,20p
