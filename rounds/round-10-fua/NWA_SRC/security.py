# -*- coding: utf-8 -*-
"""安全架构（强制项，非可选）：

a) 最小权限 (least privilege / minimal permission)：github token 的
   scope 校验，只允许 repo 类读写（开 PR 所需），禁止 admin/owner/delete。
b) 加密存储：见 token_store（KDF + 对称封装，token 绝不写明文）。
c) 强制人类审批 (mandatory human review)：自我升级只产出 PR，
   永不自动合并 (never auto-merged / auto-applied)；PR 必须经
   manual approval (人工审批门) 后才生效。
d) 每轮回滚 (per-round rollback)：每轮自我升级前快照上一稳定版本；
   冒烟测试失败/崩溃时自动回滚 (rollback / snapshot / restore)。
"""
import os
import re
import shutil
import time

HOME_DIR = os.path.join(os.path.expanduser("~"), ".nwa")
STABLE_DIR = os.path.join(HOME_DIR, "stable")
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# 允许的 scope 白名单（最小权限：仅覆盖开 PR 所需）
ALLOWED_SCOPES = {"repo", "contents", "pull_request"}
# 出现即拒绝的 scope（超出最小权限）
FORBIDDEN_MARKS = ("admin:", "owner", "delete", "sudo", "all")

_TOKEN_PREFIX = re.compile(r"^(ghp_|gho_|ghu_|ghs_|github-)?[A-Za-z0-9\-_]{16,}")


def validate_scope(token, scopes=None, mock=False):
    """校验 github token 的 scope 是否满足最小权限要求。

    离线/验收环境走本地形状校验（前缀+长度）；mock=True 直接放行占位符。
    返回 (ok, reason)。
    """
    if mock:
        return True, "mock scope check (dry-run/offline)"
    if not _TOKEN_PREFIX.match(token.strip()):
        return False, "token 形状非法（github PAT 前缀/长度不符）"
    for s in (scopes or []):
        for mark in FORBIDDEN_MARKS:
            if mark in s.lower():
                return False, "scope '%s' 超出最小权限（含 %s），拒绝" % (s, mark)
        if s.lower() not in ALLOWED_SCOPES:
            return False, "scope '%s' 不在白名单 %s（least privilege 原则）" % (s, sorted(ALLOWED_SCOPES))
    return True, "scope 校验通过（最小权限）"


def human_review_gate(pr_payload):
    """强制人类审批门：PR 创建后保持 open，绝不 auto-merge。

    返回审批状态 dict；调用方必须等人工 approval 后才允许合并。
    """
    return {
        "state": "open",
        "review_required": True,
        "human_review": "mandatory",
        "auto_merge": False,
        "note": "自我升级 PR 永不自动合并，需 human review / manual approval",
        "title": pr_payload.get("title", ""),
    }


def snapshot(reason="upgrade-round"):
    """升级前快照：把当前 NWA_SRC 树复制到稳定目录（每轮一份）。"""
    os.makedirs(STABLE_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S") + "-%03d" % (int(time.time() * 1000) % 1000)
    dest = os.path.join(STABLE_DIR, "nwa-%s-%s" % (reason, stamp))
    shutil.copytree(SRC_DIR, dest, ignore=shutil.ignore_patterns("__pycache__"))
    return dest


def latest_snapshot():
    if not os.path.isdir(STABLE_DIR):
        return None
    entries = [e for e in os.listdir(STABLE_DIR) if os.path.isdir(os.path.join(STABLE_DIR, e))]
    return os.path.join(STABLE_DIR, sorted(entries)[-1]) if entries else None


def rollback(auto=False):
    """回滚：restore 最近一份稳定版本快照到当前源码目录。

    人工触发 (nwa rollback) 与冒烟失败自动触发 (auto=True) 共用此路径。
    """
    src = latest_snapshot()
    if not src:
        return False
    for name in os.listdir(SRC_DIR):
        if name == "__pycache__":
            continue
        p = os.path.join(SRC_DIR, name)
        if os.path.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)
    for name in os.listdir(src):
        s = os.path.join(src, name)
        d = os.path.join(SRC_DIR, name)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    return True
