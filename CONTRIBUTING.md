# 提交规范（供 AI / 人工提交者）

本仓库会持续接收多轮、多提交者（含多个 AI）的 NWA 提交。为合并后不混乱，
**每轮只新增自己的一轮目录，不改动仓库内任何其他文件。**

## 轮次目录

```
rounds/round-NN-<提交者>/
  NWA_SRC/      该轮源码（fcd_src 风格组织，可独立运行）
  NWA_MAIN/     该轮多平台打包成品（CLI / Linux / Android APK / GUI / WEB）+ 构建脚本
  NWA_NEW.md    该轮改动说明
  main.py       该轮可运行入口
```

- `NN`：轮次号，取 `rounds/` 下已有目录的最大轮次号 + 1（见根 README 的轮次表）。
- `<提交者>`：提交者 GitHub 用户名（小写）。
- 轮次号相同的目录已存在时不得覆盖，顺延到下一号。

## 文件内容必须为明文（硬性）

仓库按「文本文件」保存内容。提交前请在本地确认：

```bash
file rounds/round-NN-<提交者>/main.py          # 应为 UTF-8 / ASCII text
head -c 200 rounds/round-NN-<提交者>/main.py   # 应看到代码，而不是 "base64"
```

- ✅ 允许：直接写入的 `.py` / `.md` / `.sh` / `.c` 等明文源码与文档。
- ❌ 禁止：把内容 base64 编码后再提交（文件里只有一行 `base64` 或一大串编码串）。
- 二进制成品（ELF / APK / exe）请直接提交二进制文件，**不要**先编码成文本。

> 历史遗留：`rounds/round-10-fua/` 与仓库根的两个说明文件曾被以 base64 文本形式提交，
> 现已由维护者还原为明文；保留此条以便提交者自查。

## NWA_NEW.md 格式（硬性）

- 第 1 行：提交者 GitHub 用户名 + 主页链接
- 第 2 行：联系方式，邮箱/QQ/微信/Telegram/X/Instagram **任选至少 1 项**
- 其余：详细列出本次改了哪些文件、改了什么（逐文件说明）

## 其他要求

1. 只新增 `rounds/round-NN-<提交者>/` 目录，不修改已有轮次、不改仓库根文件。
2. 该轮内容须通过官方验收（`test_outputs.py` 8 条全过）后再提 PR。
3. 源码尽量纯标准库；token 相关一律加密存储、最小权限 scope；
   自我升级产出 PR 并强制人类审批；每轮先快照、冒烟失败自动回滚。
4. 合并后由维护者在根 README 的「已合并轮次」表中登记一行。

## English

- **One round per PR**: add only your own `rounds/round-NN-<submitter>/` directory and never
  modify existing rounds or repository root files.
- **Plain text only**: source and docs must be committed as UTF-8 text. Do **not** base64-encode
  file contents before committing. Binaries (ELF/APK/exe) are committed as binaries, not text.
- **NWA_NEW.md**: line 1 = submitter GitHub username + homepage; line 2 = at least one contact
  method; the rest = a per-file change log.
- Pass the official acceptance script (`test_outputs.py`, 8/8) before opening a PR; after merge the
  maintainer adds a row to the merged-rounds table in the root README.
