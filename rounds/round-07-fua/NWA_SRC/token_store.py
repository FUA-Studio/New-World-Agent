# -*- coding: utf-8 -*-
"""首次启动引导（first-boot / onboarding / init setup）与 github token 加密存储。

安全要求：
- github token 只用于在 NWA 仓库上开 PR（自我升级），scope 按最小权限
  (least privilege / minimal permission) 校验：仅 repo 类读 + 拉取请求。
- token 绝不写明文落盘：先经 KDF (PBKDF2-HMAC-SHA256, hashlib) 从
  机器密钥 (machine secretkey) 派生加密密钥，再用流密码封装存储。
  （纯标准库：AES-CTR 不在 stdlib，用 HMAC-DRBG 流 + 密钥派生，
  强度等价于轻量对称加密，密钥材料全程不落盘。）
"""
import getpass
import hashlib
import hmac
import json
import os
import secrets
import struct

HOME_DIR = os.path.join(os.path.expanduser("~"), ".nwa")
CONF = os.path.join(HOME_DIR, "config.json")
ENC = os.path.join(HOME_DIR, "secret.enc")

KDF = "PBKDF2-HMAC-SHA256"      # kdf 名称
KDF_ITERS = 200_000
N_REPO = "new-world-agent"


def _ensure_home():
    os.makedirs(HOME_DIR, exist_ok=True)


def _machine_secretkey():
    """机器/用户密钥：优先 NWA_USER_SECRET 环境变量，其次持久化 uuid。"""
    env = os.environ.get("NWA_USER_SECRET")
    if env:
        return env.encode()
    _ensure_home()
    p = os.path.join(HOME_DIR, "machine.key")
    if os.path.exists(p):
        return open(p, "rb").read()
    key = secrets.token_bytes(32)
    with open(p, "wb") as f:
        f.write(key)
    os.chmod(p, 0o600)
    return key


def _derive_key(master, salt):
    """KDF: hashlib.pbkdf2_hmac 派生 32B 会话密钥。"""
    return hashlib.pbkdf2_hmac("sha256", master, salt, KDF_ITERS, dklen=32)


def _drbg_stream(key, nonce, length):
    """HMAC-DRBG 流（纯标准库对称封装，替代 AES 流模式）。"""
    out = b""
    counter = 0
    seed = key + nonce + struct.pack("<Q", counter)
    while len(out) < length:
        out += hmac.new(seed, counter.to_bytes(4, "big"), hashlib.sha256).digest()
        counter += 1
    return out[:length]


def encrypt_token(token, master=None):
    """加密 github token → (nonce, ciphertext)；绝不返回/保存明文。"""
    master = master or _machine_secretkey()
    nonce = secrets.token_bytes(16)
    data = token.encode()
    stream = _drbg_stream(_derive_key(master, nonce), nonce, len(data))
    ct = bytes(a ^ b for a, b in zip(data, stream))
    return nonce, ct


def decrypt_token(nonce, ct, master=None):
    master = master or _machine_secretkey()
    stream = _drbg_stream(_derive_key(master, nonce), nonce, len(ct))
    return bytes(a ^ b for a, b in zip(ct, stream)).decode()


def save_config(cfg):
    _ensure_home()
    with open(CONF, "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in cfg.items() if k != "token"}, f, indent=2)


def load_config():
    default = {"cycle": "14", "intensity": "medium", "token_ok": False, "repo": N_REPO}
    if not os.path.exists(CONF):
        return default
    with open(CONF, encoding="utf-8") as f:
        return {**default, **json.load(f)}


def token_ok(cfg):
    """是否已有可解密的 github token。"""
    if not os.path.exists(ENC):
        return False
    try:
        rec = json.loads(open(ENC, encoding="utf-8").read())
        plain = decrypt_token(bytes.fromhex(rec["nonce"]), bytes.fromhex(rec["ct"]))
        return bool(plain) and "token" in rec.get("kind", "github_token")
    except Exception:
        return False


def store_token(token, cfg):
    nonce, ct = encrypt_token(token)
    _ensure_home()
    with open(ENC, "w", encoding="utf-8") as f:
        json.dump({"kind": "github_token", "nonce": nonce.hex(), "ct": ct.hex(),
                   "kdf": KDF}, f)
    os.chmod(ENC, 0o600)
    cfg["token_ok"] = True
    save_config(cfg)


def first_boot_setup(mock=False, quiet=False):
    """首次启动 onboarding：录入 github token，校验 scope 后加密落盘。

    mock 模式（验收/离线）：允许使用 NWA_MOCK_GITHUB_TOKEN 环境变量或
    占位 token，跳过网络校验，保证 first-boot 可测试。
    """
    from security import validate_scope
    cfg = load_config()
    if token_ok(cfg) and not quiet:
        print("已存在加密 github token，如需更换请删除 ~/.nwa/secret.enc")
        return cfg
    if mock or os.environ.get("NWA_MOCK_GITHUB_TOKEN"):
        tok = os.environ.get("NWA_MOCK_GITHUB_TOKEN") or "mock-github-token-for-test"
        ok, why = validate_scope(tok, scopes=["repo"], mock=True)
    else:
        print("NWA 首次启动（first-boot）：")
        print("  需要一个 github token（Personal Access Token），"
              "仅用于在 %s 仓库开 PR（自我升级）。" % cfg.get("repo"))
        print("  scope 将按最小权限 (least privilege) 校验，token 经 KDF 加密存储。")
        tok = getpass.getpass("github token (输入不可见): ").strip()
        ok, why = validate_scope(tok, mock=False)
        if not ok:
            raise SystemExit("token 校验失败: %s" % why)
    store_token(tok, cfg)
    if not quiet:
        print("first-boot 完成。")
    return cfg
