# 工作流守卫（NWA Submission Guard）

多轮次、多提交者（含 AI）的仓库里，一次手滑就能把内容搞坏：
文件被 base64 编码后提交、某轮误删了上一轮、往别人的轮次目录里写东西。
本工作流在每个 PR 上自动做几项廉价但有效的检查，充当**自动验收闸门**。

## 检查项

| # | 检查 | 通过标准 |
| --- | --- | --- |
| 1 | 内容编码 | `rounds/**` 下的文本文件不能是一整段 base64；不得只有占位串 `base64` |
| 2 | 文档内容 | 根 `README.md` / `CONTRIBUTING.md` 不得退化为 base64 或空占位 |
| 3 | 只增不改 | PR 只能**新增** `rounds/` 下的文件；修改或删除已有轮次文件视为违规（维护者可在 PR 说明里写 `allow-modify` 豁免） |
| 4 | 语法 | `rounds/**/NWA_SRC/*.py` 与 `main.py` 通过 `python -m py_compile` |
| 5 | 冒烟 | 各轮 `main.py selftest` 能跑通（缺失依赖或未实现时记为警告而非失败） |

失败时 PR 会显示红色 ❌，并输出具体是哪个文件不合格。

## 安装

已内置在 `.github/workflows/nwa-guard.yml`，推送到 `main` 或提交 PR 时自动运行，无需额外配置。

## 说明

- 只读取仓库内容，不联网、不需要任何 token 之外的 secret。
- 检查脚本内联在 GitHub Actions 的 `run:` 步骤里，仓库里不放额外脚本文件。
- 想放宽第 3 条：在 PR 标题或说明里加上 `allow-modify` 字样。
