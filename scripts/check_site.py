# -*- coding: utf-8 -*-
"""部署前檢查：所有頁面的本地連結都存在、目錄裡的每個實作都有頁面、資料檔都產生了。
有任何問題就以非 0 結束，讓 GitHub Actions 停止部署。"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

SITE = Path(__file__).resolve().parents[1] / "site"
errors = []

for html in sorted(SITE.rglob("*.html")):
    if html.name == "dashboard-example.html":
        continue
    text = html.read_text(encoding="utf-8")
    for ref in re.findall(r'(?:href|src)="([^"#?]+)', text):
        if re.match(r"^(https?:|mailto:|data:|javascript:)", ref) or "${" in ref or ref.startswith("+"):
            continue
        target = (html.parent / unquote(ref)).resolve()
        if not target.exists():
            errors.append(f"{html.relative_to(SITE)} → 找不到 {ref}")

common = (SITE / "assets" / "js" / "common.js").read_text(encoding="utf-8")
labs = re.findall(r'id: "(s\d/[\w-]+)"', common)
for lab in labs:
    if not (SITE / f"{lab}.html").exists():
        errors.append(f"目錄有「{lab}」，但沒有 {lab}.html")
for page in SITE.glob("s*/*.html"):
    lab = f"{page.parent.name}/{page.stem}"
    if lab not in labs:
        errors.append(f"{lab}.html 沒有列在 common.js 的目錄裡")

for name in ("s0.json", "s1.json", "s2.json", "s3.json", "downloads.json"):
    if not (SITE / "data" / name).exists():
        errors.append(f"缺少 site/data/{name}")

print(f"檢查 {len(labs)} 個實作頁面")
if errors:
    print("\n".join("✗ " + e for e in errors))
    sys.exit(1)
print("✓ 全部通過")
