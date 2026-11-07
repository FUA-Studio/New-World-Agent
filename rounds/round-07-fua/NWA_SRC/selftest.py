# -*- coding: utf-8 -*-
"""nwa selftest：冒烟自检（import / banner / 升级 dry-run / 回滚演练）。

self-test 全部离线可跑（mock LLM + 不联网），也是自我升级每轮的
冒烟测试 (smoke test)：失败即触发自动回滚 (auto rollback trigger)。
"""
import importlib

CHECKS = [
    "import",
    "banner",
    "upgrade_dryrun",
    "rollback_drill",
    "token_encrypt_roundtrip",
    "scope_validation",
]


def _t_import():
    for m in ("banner", "theme", "usage", "llm", "token_store", "security", "upgrade", "selftest"):
        importlib.import_module(m)
    return True


def _t_banner():
    from banner import BANNER
    return bool(BANNER.strip())


def _t_upgrade_dryrun():
    import upgrade
    payload = upgrade.run_self_upgrade(dry_run=True, round_no=1)
    # dry-run 必须产出 PR payload 且不联网
    return bool(payload) and payload.get("body", {}).get("title", "").startswith("[NWA self-upgrade]")


def _t_rollback_drill():
    import security
    snap = security.snapshot("selftest-drill")
    ok = security.rollback()
    return ok and bool(snap)


def _t_token_encrypt():
    import token_store
    nonce, ct = token_store.encrypt_token("test-github-token-123456")
    back = token_store.decrypt_token(nonce, ct)
    return back == "test-github-token-123456"


def _t_scope_validation():
    import security
    good, _ = security.validate_scope("ghp_" + "a" * 24, scopes=["repo", "pull_request"], mock=False)
    bad, _ = security.validate_scope("ghp_" + "a" * 24, scopes=["admin:org"], mock=False)
    return good and not bad


def run_all(after_upgrade=False):
    """执行全部 self-test。after_upgrade=True（升级冒烟）时跳过回滚演练。"""
    results = {
        "import": _t_import(),
        "banner": _t_banner(),
        "upgrade_dryrun": _t_upgrade_dryrun(),
        "token_encrypt_roundtrip": _t_token_encrypt(),
        "scope_validation": _t_scope_validation(),
    }
    if not after_upgrade:
        results["rollback_drill"] = _t_rollback_drill()
    return results
