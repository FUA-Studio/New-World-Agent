# -*- coding: utf-8 -*-
"""NWA (New World Agent) CLI 主入口。

功能与 FCD 相似：交互式会话、工具调用、首次启动引导、自我升级、
回滚、自检验证。重新品牌化为 NWA（深绿 + 银灰主题）。

用法:
  python3 main.py                    交互式会话（首次启动先引导录入 github token）
  python3 main.py --help             显示帮助
  python3 main.py first-boot         首次启动引导（录入并加密保存 github token）
  python3 main.py self-upgrade --dry-run   生成 PR payload（不联网）
  python3 main.py self-upgrade --round 3   执行一轮自我升级（产出 PR，人工审批）
  python3 main.py rollback          回滚到最近一次稳定版本
  python3 main.py snapshot          手动打稳定版本快照
  python3 main.py selftest          自检（import/banner/升级dry-run/回滚演练）
  python3 main.py banner            显示主题横幅

纯标准库实现（加密用 hashlib+PBKDF2），可移植到 NWA_MAIN 各平台成品。
"""
import argparse
import json
import os
import sys

if sys.stdout is not None and hasattr(sys.stdout, "isatty"):
    pass

from banner import BANNER, GREEN, GREEN_DARK, SILVER, RESET, cyan, yellow, red, gray, green, bold
from theme import DEEP_GREEN, SILVER_GRAY, PALETTE
from usage import log_event, summary
from llm import call_llm, is_mock, MOCK
from token_store import load_config, save_config, first_boot_setup, token_ok
from security import validate_scope, human_review_gate, snapshot, rollback, STABLE_DIR
from upgrade import CYCLE_DAYS, INTENSITY_TIERS, run_self_upgrade


def _ensure_config():
    cfg = load_config()
    if not token_ok(cfg):
        print("检测到尚未完成首次启动：请先执行  python3 main.py first-boot")
        print("以录入 github token（将按最小权限 scope 校验并加密存储，绝不写明文）。")
        sys.exit(2)
    return cfg


def cmd_banner(_args):
    print(BANNER)
    print("主题: 深绿 #14532d/%s + 银灰 #c0c0c0/%s" % (DEEP_GREEN, SILVER_GRAY))


def cmd_first_boot(args):
    cfg = first_boot_setup(mock= getattr(args, "mock", False), quiet=True)
    print("首次启动完成：github token 已通过最小权限 scope 校验并以 KDF 派生密钥加密落盘。")
    print("升级周期=%s 天，强度=%s" % (cfg["cycle"], cfg["intensity"]))


def cmd_chat(args):
    _ensure_config()
    print(BANNER)
    print("NWA 交互式会话（%s）—— 输入 :quit 退出" % ("mock 模式" if is_mock() else "LLM 模式"))
    history = []
    while True:
        try:
            line = input(gray("nwa> "))
        except (EOFError, KeyboardInterrupt):
            break
        if not line.strip():
            continue
        if line.strip() in (":quit", ":q", "exit", "quit"):
            break
        if line.strip() == ":usage":
            print(json.dumps(summary(), ensure_ascii=False, indent=2))
            continue
        if line.strip() == ":banner":
            print(BANNER)
            continue
        ans = call_llm(line, history)
        history.append(line)
        print(GREEN + ans + RESET)
        log_event("chat", {"prompt": line[:80], "mock": is_mock()})


def cmd_self_upgrade(args):
    _ensure_config()
    run_self_upgrade(dry_run=getattr(args, "dry_run", False),
                     round_no=getattr(args, "round", None))


def cmd_rollback(_args):
    ok = rollback()
    if not ok:
        print("回滚失败：没有可用快照，请先 snapshot。")
        sys.exit(1)


def cmd_snapshot(_args):
    id_ = snapshot("manual")
    print("快照 %s 已保存至 %s" % (id_, STABLE_DIR))


def cmd_selftest(args):
    from selftest import run_all
    results = run_all()
    for name, ok in results.items():
        print((GREEN + "[PASS] " if ok else RED + "[FAIL] ") + name)
    sys.exit(0 if all(results.values()) else 1)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="nwa",
        description="NWA (New World Agent) —— 基于 FCD 源码重构的 CLI AI 代理，"
                    "支持自我升级/回滚/加密 token 存储/人类审批门禁。")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("banner", help="显示主题横幅")
    p_fb = sub.add_parser("first-boot", help="首次启动引导：录入 github token（onboarding）")
    p_fb.add_argument("--mock", action="store_true", help="mock 模式：不联网校验 scope")
    p_su = sub.add_parser("self-upgrade", help="自我升级（产出 PR，人工审批后才生效）")
    p_su.add_argument("--dry-run", "--dry-run-mode", dest="dry_run", action="store_true",
                      help="dryrun：仅生成 PR payload，不联网")
    p_su.add_argument("--round", type=int, default=None, help="指定轮次")
    sub.add_parser("rollback", help="回滚到最近稳定版本")
    sub.add_parser("snapshot", help="手动打稳定版本快照")
    sub.add_parser("selftest", help="自检：import/banner/升级dry-run/回滚演练")
    args = parser.parse_args(argv)
    if not args.cmd:
        cmd_chat(args)
        return
    if args.cmd == "banner":
        cmd_banner(args)
    elif args.cmd == "first-boot":
        cmd_first_boot(args)
    elif args.cmd == "self-upgrade":
        cmd_self_upgrade(args)
    elif args.cmd == "rollback":
        cmd_rollback(args)
    elif args.cmd == "snapshot":
        cmd_snapshot(args)
    elif args.cmd == "selftest":
        cmd_selftest(args)
        return


if __name__ == "__main__":
    main()
