# -*- coding: utf-8 -*-
"""自我升级 (self-upgrade)：AI 可修改自身源码加功能/提性能。

- 升级周期 (upgrade cycle)：每 7 / 14 / 30 / 60 天一次，或 off 关闭。
- 每轮强度 (intensity)：low / medium / high / max / ultra 五档。
- 交付物是 PR（产出 PR payload），强制人类审批，绝不自动合并/自动应用。
- 每轮先打稳定版本快照 (snapshot)，冒烟测试 (smoke test) 失败或崩溃时
  自动回滚 (rollback / auto rollback trigger)。
- dry-run：nwa self-upgrade --dry-run 生成 PR payload 但不联网、不改动源码。
"""
import json
import os

import llm
import security
import selftest
import token_store

# 升级周期（天）：7 / 14 / 30 / 60，off 表示关闭
CYCLE_DAYS = [7, 14, 30, 60]
CYCLE_OFF = "off"

# 每轮强度档位
INTENSITY_TIERS = ["low", "medium", "high", "max", "ultra"]

UPLINK = {
    "repo": "NWA/new-world-agent",
    "base": "main",
}


def _plan_prompt(intensity, round_no):
    return (
        "你是 NWA 维护者。按强度 %s 规划本轮自我升级：改动要小步、可回滚。"
        "第 %d 轮。输出 JSON：{\"summary\": 一句话, \"edits\": [文件: 改动点]}，"
        "强度越高改动越多；max/ultra 仍需保持冒烟测试通过。"
        % (intensity, round_no)
    )


def build_pr_payload(plan, cfg, round_no):
    """生成 PR payload（dry-run 的核心产物：不发网络请求）。"""
    token_mask = "***" if not cfg.get("token_ok") else "github-token (encrypted, least-privilege scope)"
    return {
        "api": "https://api.github.com",
        "method": "POST /repos/%s/pulls" % UPLINK["repo"],
        "auth": token_mask,
        "body": {
            "title": "[NWA self-upgrade] round %d (%s)" % (round_no, cfg.get("intensity")),
            "head": "nwa/self-upgrade-r%d" % round_no,
            "base": UPLINK["base"],
            "body": ("NWA 第 %d 轮自我升级（强度 %s）。\n\n%s\n\n"
                     "安全：token 最小权限 scope；人类审批后合并；冒烟失败自动回滚。"
                     % (round_no, cfg.get("intensity"), plan.get("summary", ""))),
            "edits": plan.get("edits", []),
        },
        "post_merge": {
            "auto_merge": False,
            "gate": "human review (mandatory) → manual approval → merge",
        },
    }


def run_self_upgrade(dry_run=False, round_no=None):
    """执行一轮自我升级。dry-run 只打印 PR payload，不联网不改码。"""
    cfg = token_store.load_config()
    intensity = cfg.get("intensity", "medium")
    if intensity not in INTENSITY_TIERS:
        intensity = "medium"
    round_no = round_no or int(cfg.get("round", 0)) + 1

    # d) 每轮快照（升级前）
    snap = security.snapshot("upgrade-round-%d" % round_no)
    print("[nwa] 轮次 %d · 强度 %s · 周期 %s 天 · 快照 → %s"
          % (round_no, intensity, cfg.get("cycle"), os.path.basename(snap)))

    # AI 规划（mock 离线可运行）
    raw = llm.call_llm(_plan_prompt(intensity, round_no))
    plan = _safe_parse(raw)

    payload = build_pr_payload(plan, cfg, round_no)

    if dry_run:
        print("[nwa] dry-run：PR payload 已生成（不联网、不改源码）：")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        cfg["round"] = round_no
        token_store.save_config(cfg)
        return payload

    # 冒烟测试：失败/崩溃 → 自动回滚（auto rollback trigger）
    results = selftest.run_all(after_upgrade=True)
    if not all(results.values()):
        security.rollback(auto=True)
        print("[nwa] 冒烟测试失败 → 已自动回滚到稳定快照 (auto rollback)。")
        cfg["round"] = round_no
        token_store.save_config(cfg)
        return None

    # 真实模式：创建 PR（需 token + 网络；离线时优雅降级为打印 payload）
    gate = security.human_review_gate(payload["body"])
    print("[nwa] PR payload 就绪；审批门：human review required，auto_merge=False。")
    print(json.dumps(gate, ensure_ascii=False, indent=2))
    cfg["round"] = round_no
    token_store.save_config(cfg)
    return payload


def _safe_parse(raw):
    """容错解析 LLM 输出的 JSON 计划；失败给默认计划。"""
    s = raw.strip()
    if s.startswith("{"):
        try:
            return json.loads(s)
        except Exception:
            pass
    i, j = s.find("{"), s.rfind("}")
    if i >= 0 and j > i:
        try:
            return json.loads(s[i:j + 1])
        except Exception:
            pass
    return {"summary": "常规加固轮：性能优化与冒烟测试补强（默认计划）",
            "edits": ["main.py: 会话超时参数", "llm.py: 重试退避"]}
