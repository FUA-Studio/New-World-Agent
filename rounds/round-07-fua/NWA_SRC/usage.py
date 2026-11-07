# -*- coding: utf-8 -*-
"""用量记录：会话事件与 token 消耗（纯标准库，落地 JSONL）。"""
import json
import os
import time

HOME_DIR = os.path.join(os.path.expanduser("~"), ".nwa")
EVENTS = os.path.join(HOME_DIR, "usage.jsonl")


def _ensure():
    os.makedirs(HOME_DIR, exist_ok=True)


def log_event(kind, extra=None):
    """记录一条事件。extra 里可带 input_tokens/output_tokens。"""
    _ensure()
    rec = {"ts": int(time.time()), "kind": kind}
    rec.update(extra or {})
    with open(EVENTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def summary():
    """近 7 天用量汇总。"""
    if not os.path.exists(EVENTS):
        return {"events": 0, "input_tokens": 0, "output_tokens": 0}
    now = time.time()
    ev, tin, tout = 0, 0, 0
    with open(EVENTS, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if now - rec.get("ts", 0) > 7 * 86400:
                continue
            ev += 1
            tin += int(rec.get("input_tokens", 0))
            tout += int(rec.get("output_tokens", 0))
    return {"events": ev, "input_tokens": tin, "output_tokens": tout}
