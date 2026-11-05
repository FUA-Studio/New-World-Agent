fua (github 用户名: fua · 主页: https://fua-studio.us.ci)
联系方式: https://fua-studio.us.ci（按规范任选其一，填官网）

## 本次改动明细（build-nwa-from-fcd · 第 7 轮提交）

### 新增：完整 NWA 实现（全部为新写代码，非照抄 fcd_src）

**NWA_SRC/（源码树，fcd_src 风格组织，纯标准库）**
- `main.py`  CLI 主入口：交互式会话、first-boot 引导、self-upgrade（含 --dry-run）、
  rollback、snapshot、selftest、banner 子命令；argparse 参数化；首次启动检测
  （token 未配置时提示 onboarding 流程，exit code 2）。
- `banner.py` 主题横幅：deep green (#14532d) + silver gray (#c0c0c0) 双色 ANSI
  渲染；NO_COLOR / 非终端自动降级无色；提供 green/gray/red/cyan/yellow/bold 调色函数。
- `theme.py`  全平台共用 PALETTE（终端 256 色取值 + GUI/WEB CSS 变量导出
  css_variables()），主色 deep green #14532d / #064e3b，银灰 #c0c0c0 / #9ca3af。
- `llm.py`  OpenAI 兼容接口（urllib，标准库）；无密钥自动降级 mock 应答，
  保证离线 / CI / dry-run 可运行（NWA_API_BASE / NWA_API_KEY / NWA_MODEL 环境变量）。
- `token_store.py`  首次启动 (first-boot) 引导 + github token 加密存储：
  KDF = PBKDF2-HMAC-SHA256（hashlib，200k 轮）从机器密钥 (machine secretkey)
  派生会话密钥；HMAC-DRBG 流对称封装（stdlib 无 AES-CTR 的等价方案）；
  密文+nonce 落盘 ~/.nwa/secret.enc (0600)；token 绝不写明文；
  mock 模式支持离线验收（NWA_MOCK_GITHUB_TOKEN）。
- `security.py`  安全架构四件强制项：
  a) 最小权限 (least privilege / minimal permission)：validate_scope() 按
     scope 白名单 {repo, contents, pull_request} 校验，admin:/owner/delete 拒发；
  b) 加密存储引用 token_store；
  c) 强制人类审批 (mandatory human review)：human_review_gate() 保证
     auto_merge=False，PR 需 manual approval 才生效，永不自动合并/自动应用；
  d) 每轮回滚 (per-round rollback)：snapshot() 每轮升级前快照上一稳定版本，
     rollback() 支持 nwa rollback 人工触发 + 冒烟失败自动触发 (auto rollback)。
- `upgrade.py`  自我升级引擎：周期 7/14/30/60 天或 off（CYCLE_DAYS）；
  强度 low/medium/high/max/ultra（INTENSITY_TIERS）；run_self_upgrade()
  先打快照→AI 规划→产出 PR payload；--dry-run 不联网只打印 payload；
  冒烟测试 (smoke test) 失败自动回滚 (auto rollback trigger)。
- `selftest.py`  冒烟自检六项：import / banner / 升级 dry-run / 回滚演练
  (rollback drill) / token 加解密回环 / scope 校验；离线全通过。

**NWA_MAIN/（多平台打包成品，PR 规范目录：APK / LINUX / CLI / GUI）**
- `artifacts/`  本轮实际成品（已生成并验证）：
  - `nwa-linux`  **ELF 二进制**（x86-64）：CLI 成品，`./nwa-linux --help` 直接运行
    （内嵌全部源码，首跑解包到 ~/.nwa_pkg 再调系统 python3）
  - `nwa-gui-linux`  **ELF 二进制**：GUI 成品（需系统 python3-tk）
  - `nwa-android-assets.zip`  安卓临时资源包（**不是 APK**：里面只有
    AndroidManifest.xml + NWA Python 源码，给 Termux 直接跑用；真 .apk 需
    Android SDK，本环境编不出来，`android/build-apk.sh` 留给有 SDK 的机器）
- `build/nwa_app.c` + `build/generate_b64.py`  单文件启动器源码（两个 ELF 成品即由它在 WSL 里 gcc 编译产出）
- `cli/` `linux/` `gui/` `android/`  各平台构建脚本与壳工程（可复打包）

**本轮目录（rounds/round-07-fua/ 内）**
- `main.py`  可运行入口（sys.path 挂 NWA_SRC 后转发实现）。
- `README.md`  使用与安全模型文档。

### 未改动
- fcd_src/（只读参考，未复制未修改）
- 任务 tests/（验收脚本原样）

### 验收方式
- 容器内：`python3 /app/nwa/main.py --help`（exit 0）
- `python3 /app/nwa/main.py selftest`（六项 PASS）
- `python3 /app/nwa/main.py self-upgrade --dry-run`（PR payload，不联网）
