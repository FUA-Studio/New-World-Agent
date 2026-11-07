# -*- coding: utf-8 -*-
"""LLM 调用接口：支持 OpenAI 兼容 API（环境变量 NWA_API_BASE / NWA_API_KEY）。

无密钥时自动降级为本地 mock 应答，保证离线/CI/验收环境可运行
（dry-run、selftest 均不依赖网络）。
"""
import json
import os
import urllib.request

API_BASE = os.environ.get("NWA_API_BASE", "https://api.openai.com/v1")
API_KEY = os.environ.get("NWA_API_KEY", "")
MODEL = os.environ.get("NWA_MODEL", "gpt-4o-mini")

MOCK = not API_KEY


def is_mock():
    return MOCK


def call_llm(prompt, history=None):
    """单轮对话。真实模式走 HTTP；mock 模式给确定性本地应答。"""
    history = history or []
    if MOCK:
        return _mock_reply(prompt, history)
    msgs = [{"role": "user", "content": h} for h in history[-5:]]
    msgs.append({"role": "user", "content": prompt})
    payload = json.dumps({"model": MODEL, "messages": msgs}).encode()
    req = urllib.request.Request(
        API_BASE + "/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + API_KEY})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


def _mock_reply(prompt, history):
    p = prompt.lower()
    if "banner" in p or "横幅" in p:
        return "NWA 横幅：深绿 #14532d + 银灰 #c0c0c0 主题。"
    if "token" in p or "密钥" in p:
        return "github token 仅加密存储（KDF 派生密钥），绝不写明文；scope 限定单仓最小权限。"
    if "升级" in p or "upgrade" in p:
        return "自我升级按周期 7/14/30/60 天运行，强度 low..ULTRA，产出 PR 需人工审批。"
    return "[mock] 已收到：%s（离线模式，设置 NWA_API_KEY 可切换真实模型）" % prompt[:40]
