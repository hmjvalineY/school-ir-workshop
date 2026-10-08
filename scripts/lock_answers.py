# -*- coding: utf-8 -*-
"""把解答打包並加密，讓網站上的解答需要「6 碼數字密碼」才能下載。

這是上課用的輕度保護（6 碼數字可以被暴力破解），目的是讓學員先做練習、再看解答。
  原始解答：private/（不進版控，只在講師電腦）
  密碼：    private/passwords.json（第一次執行時自動產生；要換密碼就刪掉它或用 --new）
  輸出：    materials/locked/*.zip.enc 與 materials/locked/locked.json（進版控、會上網站）
加密：PBKDF2-HMAC-SHA256（200,000 次）推出金鑰，AES-256-GCM 加密；瀏覽器用 WebCrypto 解密。

用法：pip install cryptography
      python scripts/lock_answers.py          # 沿用現有密碼重新加密
      python scripts/lock_answers.py --new    # 產生新密碼
"""
import io
import json
import os
import secrets
import sys
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT = Path(__file__).resolve().parents[1]
PRIV = ROOT / "private"
OUT = ROOT / "materials" / "locked"
ITER = 200_000

# 課程：(代號, 下載檔名, 說明, 要打包的 [(來源, 壓縮檔內路徑)])
LOCKS = [
    ("s2", "校務資料統整平台_解答.zip", "標準答案、Power Query 完成版與 12 段 M 公式",
     [(PRIV / "s2" / "解答", "解答")]),
    ("s3", "數據治理與高中校務研究_解答.zip", "21 個問題的列號、面向與處理建議，附乾淨版本",
     [(PRIV / "s3" / "治理研習_解答_問題清單.xlsx", "治理研習_解答_問題清單.xlsx")]),
]


def make_zip(items):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in items:
            if src.is_dir():
                for f in sorted(src.rglob("*")):
                    if f.is_file():
                        z.write(f, str(Path(arc) / f.relative_to(src)))
            else:
                z.write(src, arc)
    return buf.getvalue()


def main():
    pw_file = PRIV / "passwords.json"
    pw = {} if "--new" in sys.argv or not pw_file.exists() else json.loads(pw_file.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for sess, name, desc, items in LOCKS:
        if sess not in pw:
            pw[sess] = str(secrets.randbelow(900000) + 100000)
        data = make_zip(items)
        salt, iv = os.urandom(16), os.urandom(12)
        key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw[sess].encode())
        (OUT / (name + ".enc")).write_bytes(AESGCM(key).encrypt(iv, data, None))
        manifest.append({"session": sess, "name": name, "desc": desc, "file": name + ".enc", "size": len(data),
                         "salt": salt.hex(), "iv": iv.hex(), "iter": ITER})
        print(f"{sess}　{name}　密碼 {pw[sess]}　（{len(data) // 1024} KB）")
    (OUT / "locked.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    pw_file.write_text(json.dumps(pw, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"密碼存在 {pw_file.relative_to(ROOT)}（不進版控）")


if __name__ == "__main__":
    main()
