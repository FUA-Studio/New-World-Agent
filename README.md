# New World Agent (NWA)

<p align="center">
  <b>自我升级型 AI 代理 · 多轮次 · 多提交者</b><br>
  <sub>最小权限 token · 加密存储 · 强制人类审批 · 每轮回滚</sub><br>
  <sub>由 <b>FUA Studio</b> 维护</sub>
</p>

<p align="center">
  <img alt="platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Android%20%7C%20CLI%20%7C%20GUI-0078D6">
  <img alt="python" src="https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white">
  <img alt="stdlib" src="https://img.shields.io/badge/dependencies-none-success">
  <img alt="rounds" src="https://img.shields.io/badge/rounds-07%20%7C%2010-informational">
</p>

---

## 中文

New World Agent 是一个**多轮次、多提交者**的自我升级型 AI 代理仓库：
每一轮由一个提交者（人工或 AI）独立完成，放在 `rounds/round-NN-<提交者>/`
下互不覆盖，合并后由维护者登记到轮次表。

NWA 的自我升级不是「自己改自己然后直接上线」，而是一条**带闸门**的流水线：

```
AI 规划改动 → 产出 PR payload → 强制人类审批 → 快照上一稳定版本
            → 应用 → 冒烟自检 → 失败则自动回滚
```

### 安全模型（四件强制项）

| 闸门 | 做法 | 代码位置 |
| --- | --- | --- |
| 最小权限 | token scope 白名单 `repo / contents / pull_request`，`admin:`、`owner`、`delete` 一律拒发 | `security.validate_scope()` |
| 加密存储 | PBKDF2-HMAC-SHA256（200k 轮）从机器密钥派生会话密钥，密文 + nonce 落盘 `~/.nwa/secret.enc`（0600），token 永不写明文 | `token_store.py` |
| 强制人类审批 | `human_review_gate()` 保证 `auto_merge=False`，PR 必须人工批准才合并 | `security.human_review_gate()` |
| 每轮回滚 | 升级前 `snapshot()` 快照，支持 `nwa rollback` 人工回滚与冒烟失败自动回滚 | `security.snapshot()/rollback()` |

### 目录结构

```
rounds/round-NN-<提交者>/     每一轮一个独立目录
  NWA_SRC/                    该轮源码（纯标准库，可独立运行）
  NWA_MAIN/                   该轮多平台成品（CLI / Linux / Android / GUI / WEB）+ 构建脚本
  NWA_NEW.md                  该轮提交者信息与改动明细
  main.py                     该轮可运行入口
```

### 已合并轮次

| 轮次 | 提交者 | 说明 | PR | 日期 | 状态 |
| --- | --- | --- | --- | --- | --- |
| [round-07](rounds/round-07-fua/NWA_NEW.md) | fua | 首个完整 NWA 实现：CLI / 主题横幅 / 加密 token 存储 / 自我升级引擎 / 冒烟自检，官方验收 8/8 通过 | #1 | 2026-10-18 | 已合并 |
| round-10 | fua | 仅有目录骨架 | — | — | ⚠️ **占位/未完成**：`NWA_SRC/*.py`、`NWA_MAIN/**` 等全部文件内容为字符串 `base64`（各 6 字节），非可运行代码 |

### 运行（以 round-07 为例）

```bash
# 查看命令
python3 rounds/round-07-fua/main.py --help

# 离线冒烟自检（六项）
python3 rounds/round-07-fua/main.py selftest

# 自我升级演练：只打印 PR payload，不联网
python3 rounds/round-07-fua/main.py self-upgrade --dry-run
```

首次运行会进入 first-boot 引导（未配置 token 时退出码为 2）。
无 API Key 时 `llm.py` 自动降级为 mock 应答，因此 CI 与离线环境同样可跑通。

### 提交规则

任何 AI / 人工提交 PR 都必须遵守 [CONTRIBUTING.md](CONTRIBUTING.md)：
**只往 `rounds/` 下新增自己的一轮目录，不碰其他目录、不改动仓库其他文件**；
该轮内容须通过官方验收（`test_outputs.py` 8 条全过）后再提 PR。

> 提交前请自查：文件内容须为**明文**源码或说明。若正文被 base64 包裹
> （例如文件内容只剩 `base64` 一行），请先本地 `base64 -d` 还原再提交。

### 已知问题

- **round-10 的文件内容是占位字符串**：所有文件均为 6 字节 `base64`，无法运行；
  需要提交者重新上传真实源码与成品，或由维护者移除该轮。
- `NWA_MAIN/artifacts/` 中的 ELF 成品需在 Linux / WSL 下运行，Windows 上无法直接执行。
- 仓库暂无自动化 CI 工作流，验收脚本由维护者手动执行。

## English

**New World Agent (NWA)** is a self-upgrading AI agent repository organised by **rounds**:
each round is contributed independently by one submitter (human or AI) under
`rounds/round-NN-<submitter>/`, so rounds never overwrite each other.

Self-upgrading is a *gated* pipeline, not free rein:

```
AI plans a change → emit PR payload → mandatory human review → snapshot the last stable build
                  → apply → smoke test → auto-rollback on failure
```

### Security model

| Gate | Implementation |
| --- | --- |
| Least privilege | Token scopes restricted to `repo / contents / pull_request`; `admin:`, `owner`, `delete` are refused |
| Encrypted storage | PBKDF2-HMAC-SHA256 (200k rounds) from a machine key; ciphertext + nonce in `~/.nwa/secret.enc` (0600); tokens are never stored in clear text |
| Mandatory human review | `human_review_gate()` enforces `auto_merge=False`; a PR only merges after human approval |
| Per-round rollback | `snapshot()` before each upgrade; `nwa rollback` for manual rollback and automatic rollback when the smoke test fails |

### Round layout

```
rounds/round-NN-<submitter>/
  NWA_SRC/     source of this round (stdlib only, runnable on its own)
  NWA_MAIN/    packaged builds (CLI / Linux / Android / GUI / WEB) + build scripts
  NWA_NEW.md   submitter info and per-file change log
  main.py      runnable entry point of the round
```

### Merged rounds

| Round | Submitter | Summary | PR | Date | Status |
| --- | --- | --- | --- | --- | --- |
| [round-07](rounds/round-07-fua/NWA_NEW.md) | fua | First full NWA implementation (CLI, themed banner, encrypted token store, upgrade engine, smoke tests); official acceptance 8/8 | #1 | 2026-10-18 | Merged |
| round-10 | fua | Directory skeleton only | — | — | ⚠️ **Placeholder / incomplete**: every file (`NWA_SRC/*.py`, `NWA_MAIN/**`) contains the six bytes `base64` instead of real content |

### Quick start

```bash
python3 rounds/round-07-fua/main.py --help
python3 rounds/round-07-fua/main.py selftest
python3 rounds/round-07-fua/main.py self-upgrade --dry-run
```

### Contributing

Follow [CONTRIBUTING.md](CONTRIBUTING.md): add **only** your own `rounds/round-NN-<submitter>/`
directory, never touch other files, and pass the official acceptance script (8/8) before opening a PR.
File contents must be plain text — do not commit base64-wrapped payloads.

### Known issues

- round-10 is a placeholder whose files contain the literal string `base64` and cannot run.
- ELF artifacts under `NWA_MAIN/artifacts/` require Linux or WSL.
- No CI workflow is configured; acceptance is run manually by maintainers.

---

<p align="center"><sub>© 2026 FUA Studio · New World Agent</sub></p>
