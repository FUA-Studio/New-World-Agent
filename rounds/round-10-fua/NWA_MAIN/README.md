# NWA_MAIN 多平台成品（APK / LINUX / CLI / GUI）

`NWA_MAIN/` 存放各平台成品，`NWA_SRC/` 存放源码。

## artifacts/（本轮实际产出）

| 文件 | 类型 | 说明 |
|------|------|------|
| `nwa-linux` | **ELF 二进制**（x86-64，Linux/CLI 成品） | `./nwa-linux --help` 直接跑，内嵌全部源码，首跑解到 `~/.nwa_pkg` 再调系统 python3 |
| `nwa-gui-linux` | **ELF 二进制**（x86-64，Linux/GUI 成品） | `./nwa-gui-linux`（需系统装 python3-tk） |
| `nwa-android-assets.zip` | 临时资源包（**不是** APK，**不是** ELF） | 内容只有 AndroidManifest.xml + NWA Python 源码，给 Termux 直接跑用；**真 .apk 本机编不出来** |

## 说明（如实标注）

- **安卓真 .apk 出不了**：本机没有 aapt2/d8/apksigner/gradle 安卓工具链，也没网下载。
  在装了 Android SDK 的机器上跑 `android/build-apk.sh` 才能出真 .apk。
  上面的 zip 只是"没 SDK 时先在 Termux 里跑起来"的过渡包，不算成品。
- **Windows .exe / Android APK**：后续按 FCD 办法（PyInstaller+NSIS、gradle+python-for-android）补做追加，本版先交 LINUX 真 ELF 两件套。

## 构建脚本

```
NWA_MAIN/build/              C 单文件启动器源码（ELF 就是用它在 WSL 里 gcc 编出来的）
NWA_MAIN/android/build-apk.sh   出真 APK（需 SDK）
```

主题统一深绿 + 银灰（取值见 NWA_SRC/theme.py）。
