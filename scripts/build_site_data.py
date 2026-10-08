# -*- coding: utf-8 -*-
"""把 materials/ 的研習素材轉成網站用的 JSON，並打包下載檔。

輸出（皆為建置產物，不進版控）：
  site/data/s0.json s1.json s2.json s3.json downloads.json
  site/downloads/…            個別檔案
  site/downloads/*.zip        各課程打包
GitHub Actions 每次部署前都會執行；本機預覽前也請先執行一次：
  python scripts/build_site_data.py
"""
import csv
import json
import re
import shutil
import zipfile
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
MAT = ROOT / "materials"
SITE = ROOT / "site"
DATA = SITE / "data"
DL = SITE / "downloads"


def jdump(obj, name):
    DATA.mkdir(parents=True, exist_ok=True)
    with open(DATA / name, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


def sheet_rows(path, sheet=None):
    wb = load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet else wb.worksheets[0]
    return [list(r) for r in ws.iter_rows(values_only=True)]


def read_csv(path):
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp950"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    return enc, [r for r in csv.reader(txt.splitlines())]


FULL = re.compile(r"[０-９]")


# ======================= S0 開場 50 問 =======================
def build_s0():
    d = json.load(open(MAT / "s0" / "data_50.json", encoding="utf-8"))
    jdump(d, "s0.json")


# ======================= S1 數據驅動的學校進化 =======================
def build_s1():
    f = MAT / "s1" / "模擬校務資料_研習用.xlsx"
    out = {}
    for key, sh in [("roster", "學生名冊"), ("courses", "選課紀錄"), ("lp", "學習歷程"), ("exams", "段考成績"),
                    ("plans", "計畫清單"), ("indicators", "指標登錄"), ("participation", "計畫參與")]:
        rows = sheet_rows(f, sh)
        out[key] = {"cols": rows[0], "rows": [r for r in rows[1:] if any(v is not None for v in r)]}
    jdump(out, "s1.json")


# ======================= S2 校務資料統整平台 =======================
def build_s2():
    base = MAT / "s2" / "練習資料"
    files = []

    # --- 系統A 名冊 ---
    rows = sheet_rows(base / "系統A_學生名冊.xlsx")
    head = rows[0]
    marks = []
    for c, h in enumerate(head):
        if h in ("姓名", "出生日期", "戶籍地址"):
            marks.append({"r": 0, "c": c, "k": "pii", "n": f"「{h}」是個資欄位，匯入後第一步就刪除"})
    for r, row in enumerate(rows[1:], 1):
        if isinstance(row[1], str) and row[1] != row[1].strip():
            marks.append({"r": r, "c": 1, "k": "space", "n": "姓名尾端多一個空白"})
    marks.append({"r": 0, "c": head.index("出生日期"), "k": "format", "n": "民國 7 碼（0950808），不是日期格式"})
    files.append({"id": "roster", "name": "系統A_學生名冊.xlsx", "role": "主檔",
                  "summary": ["學號是文字（好事），班級寫 301，是全校的標準寫法", "含姓名、生日、地址等個資欄位",
                              "部分姓名尾端有空白", "11 月轉入生 111204 已在名冊，但其他系統還沒有"],
                  "rows": rows, "marks": marks})

    # --- 系統B 段考成績（報表格式）---
    rows = sheet_rows(base / "系統B_段考成績.xlsx")
    marks = []
    seen_head = False
    for r, row in enumerate(rows):
        if r < 2:
            marks.append({"r": r, "c": -1, "k": "title", "n": "報表標題與列印資訊，不是資料"})
            continue
        if all(v is None for v in row):
            marks.append({"r": r, "c": -1, "k": "blank", "n": "空白列"})
            continue
        if row[0] == "班級":
            if seen_head:
                marks.append({"r": r, "c": -1, "k": "header", "n": "每一班重複一次的標題列"})
            seen_head = True
            continue
        if row[0] == "班平均":
            marks.append({"r": r, "c": -1, "k": "avg", "n": "「班平均」不是學生，要篩掉"})
            continue
        if isinstance(row[2], (int, float)) and r < 6:
            marks.append({"r": r, "c": 2, "k": "number", "n": "學號被存成數字（開頭 0 的學號會出事）"})
        for c in range(3, 8):
            v = row[c]
            if v == "缺":
                marks.append({"r": r, "c": c, "k": "absent", "n": "「缺」代表缺考，不是 0 分"})
            elif v is None:
                marks.append({"r": r, "c": c, "k": "missing", "n": "空白＝未登錄；逆透視會直接把這格丟掉"})
            elif isinstance(v, str) and FULL.search(v):
                marks.append({"r": r, "c": c, "k": "fullwidth", "n": f"全形數字「{v}」，要轉半形才能計算"})
    files.append({"id": "score", "name": "系統B_段考成績.xlsx", "role": "練習 2",
                  "summary": ["前 3 列是標題與列印日期", "每一班重複一次標題列、班級之間有空白列", "「班平均」列混在學生之間",
                              "學號存成數字", "「缺」、空白、全形數字混在成績裡", "含已休學的 3 位學生（名冊找不到）"],
                  "rows": rows, "marks": marks})

    # --- 系統C 出缺席 ---
    att = {}
    for p in sorted((base / "出缺席_每月匯出").glob("*.csv")) + sorted((base / "下個月才會拿到").glob("*.csv")):
        enc, rows = read_csv(p)
        marks = [{"r": 0, "c": 0, "k": "format", "n": "民國日期 113/09/02"},
                 {"r": 0, "c": 1, "k": "format", "n": "班級寫成「三年一班」，要用對照表換成 301"},
                 {"r": 0, "c": 4, "k": "pii", "n": "姓名：個資，整合時刪除"}]
        seen_exact, seen_trim = {}, {}
        for r, row in enumerate(rows[1:], 1):
            if row[3] != row[3].strip():
                marks.append({"r": r, "c": 3, "k": "space", "n": "學號尾端有空白，看起來一樣但對不起來"})
            key = tuple(row)
            tkey = tuple(v.strip() for v in row)
            if key in seen_exact:
                marks.append({"r": r, "c": -1, "k": "dup", "n": f"與第 {seen_exact[key]} 列完全重複"})
            elif tkey in seen_trim:
                marks.append({"r": r, "c": -1, "k": "dup", "n": f"與第 {seen_trim[tkey]} 列只差一個空白：先修剪才去得掉"})
            seen_exact.setdefault(key, r)
            seen_trim.setdefault(tkey, r)
        later = "下個月才會拿到" in str(p.parent)
        att[p.name] = {"enc": enc, "later": later, "rows": rows, "marks": marks}
    files.append({"id": "att", "name": "出缺席_每月匯出／系統C_出缺席_*.csv", "role": "練習 1",
                  "summary": ["每月一個檔，要用「從資料夾」一次接進來", "Big5（950）編碼，用錯會變亂碼", "民國日期、班級寫「三年一班」",
                              "學號尾端空白、重複登錄（其中一筆只差一個空白）", "12 月的檔案「下個月才會拿到」，用來示範自動更新"],
                  "months": att})

    # --- 對照表 ---
    idm = sheet_rows(base / "對照表.xlsx", "身分對照")
    cls = sheet_rows(base / "對照表.xlsx", "班級對照")
    term = sheet_rows(base / "對照表.xlsx", "學期對照")
    files.append({"id": "map", "name": "對照表.xlsx", "role": "練習 3",
                  "summary": ["身分對照：學號 ↔ 學校帳號，是整個平台的心臟", "2 個帳號後面多一個字母（s111045a），不能直接從帳號拆學號",
                              "11 月轉入生 111204 還沒寫進身分對照", "班級對照：同一個班有四種寫法"],
                  "sheets": {"身分對照": idm, "班級對照": cls, "學期對照": term}})

    # --- 系統D 學習歷程 ---
    enc, rows = read_csv(base / "系統D_學習歷程.csv")
    accts = {r[1] for r in idm[1:]}
    marks = [{"r": 0, "c": 0, "k": "format", "n": "學年度與學期分成兩欄"},
             {"r": 0, "c": 3, "k": "format", "n": "班級寫成「3年1班」"}]
    for r, row in enumerate(rows[1:], 1):
        acc = row[2]
        if re.match(r"s\d{6}[a-z]@", acc):
            marks.append({"r": r, "c": 2, "k": "acct", "n": "帳號多一個字母：直接拆字串會得到錯的學號"})
        if acc not in accts:
            marks.append({"r": r, "c": 2, "k": "unmatched", "n": "身分對照表裡找不到這個帳號（轉入生）"})
    files.append({"id": "lp", "name": "系統D_學習歷程.csv", "role": "練習 3",
                  "summary": ["只有學校帳號、沒有學號，要透過身分對照接上", "UTF-8 編碼", "學年度、學期分兩欄；班級寫「3年1班」"],
                  "rows": rows, "marks": marks, "enc": enc})

    # --- 表單 活動報名 ---
    rows = sheet_rows(base / "表單_活動報名.xlsx")
    marks = [{"r": 0, "c": 2, "k": "pii", "n": "姓名：個資；而且〇／O／o 混用"}]
    norm_seen = {}
    for r, row in enumerate(rows[1:], 1):
        v = str(row[1])
        if FULL.search(v):
            marks.append({"r": r, "c": 1, "k": "fullwidth", "n": "全形數字"})
        elif "-" in v:
            marks.append({"r": r, "c": 1, "k": "format", "n": "學號中間打了橫線"})
        elif v.upper().startswith("S"):
            marks.append({"r": r, "c": 1, "k": "format", "n": "前面多打了 S"})
        elif v != v.strip():
            marks.append({"r": r, "c": 1, "k": "space", "n": "前後有空白"})
        digits = "".join(chr(ord(ch) - 65248) if "０" <= ch <= "９" else ch for ch in v)
        digits = re.sub(r"\D", "", digits)
        if len(digits) != 6:
            marks.append({"r": r, "c": 1, "k": "typo", "n": f"清完只剩 {len(digits)} 碼：打錯，無法自動修正"})
        key = (digits, row[4])
        if key in norm_seen:
            marks.append({"r": r, "c": -1, "k": "dup", "n": f"與第 {norm_seen[key]} 列是同一人同一活動：重複提交，保留最後一次"})
        norm_seen[key] = r
    files.append({"id": "form", "name": "表單_活動報名.xlsx", "role": "挑戰題",
                  "summary": ["學號由學生手打：全形、橫線、S 開頭、前後空白、少打一碼", "同一人同一活動重複提交", "姓名的「O」有三種寫法"],
                  "rows": rows, "marks": marks})

    answers = json.load(open(MAT / "s2" / "answers.json", encoding="utf-8"))
    jdump({"files": files, "answers": answers}, "s2.json")


# ======================= S3 數據治理 =======================
def build_s3():
    d = json.load(open(MAT / "s3" / "s3_source.json", encoding="utf-8"))
    jdump(d, "s3.json")


# ======================= 下載檔 =======================
DESC = {
    "講義_高中校務50問_從現象數據到決策.pdf": "50 題逐題詳解：現象、提問、數據、分析步驟、根因與決策",
    "模擬校務資料_研習用.xlsx": "300 位學生的名冊、選課、學習歷程、段考成績，以及計畫與指標（已整理好的乾淨資料）",
    "範例_AI自製校務研究儀表板.html": "用 AI 產生的單一網頁儀表板範例，下載後直接用瀏覽器開啟",
    "講義A_Excel_Power_Query_逐步操作.pdf": "Excel Power Query 與樞紐分析逐步操作",
    "講義B_Google_Data_Studio_逐步操作.pdf": "Google Data Studio 儀表板逐步操作",
    "講義C_Power_BI_Desktop_逐步操作.pdf": "Power BI Desktop 儀表板逐步操作",
    "講義D_AI自製校務研究系統_逐步操作.pdf": "用 AI 自製校務研究網頁逐步操作",
    "講義E_多來源資料清洗與整合_逐步操作.pdf": "五個來源清成一張整合表的完整步驟（含 M 公式）",
    "講義F_資料自動化取得與同步_逐步操作.pdf": "Google／微軟兩條自動化路線",
    "範本_資料盤點與治理.xlsx": "資料盤點表、資料字典、品質檢核範本",
    "高中校務研究資料盤點清冊.docx": "11 大類、62 項高中校務研究資料的完整清冊",
    "治理研習_髒資料_學生學習.xlsx": "開場實驗與小操作用：58 列學生學習資料，藏了 21 個問題",
    "治理研習_去識別化練習.xlsx": "小操作三：10 位（虛構）學生的原始資料，練習假名化、概化、遮罩",
}
BUNDLES = [
    ("s0", "開場_高中校務50問.zip", [("s0/講義_高中校務50問_從現象數據到決策.pdf", None)]),
    ("s1", "數據驅動的學校進化_全部素材.zip", [("s1", "")]),
    ("s2", "校務資料統整平台_練習資料.zip", [("s2/練習資料", "練習資料")]),
    ("s3", "數據治理與高中校務研究_練習資料.zip", [("s3/治理研習_髒資料_學生學習.xlsx", None), ("s3/治理研習_去識別化練習.xlsx", None)]),
]
SINGLES = {
    "s0": ["講義_高中校務50問_從現象數據到決策.pdf"],
    "s1": ["模擬校務資料_研習用.xlsx", "範例_AI自製校務研究儀表板.html", "講義A_Excel_Power_Query_逐步操作.pdf",
           "講義B_Google_Data_Studio_逐步操作.pdf", "講義C_Power_BI_Desktop_逐步操作.pdf", "講義D_AI自製校務研究系統_逐步操作.pdf"],
    "s2": ["講義E_多來源資料清洗與整合_逐步操作.pdf", "講義F_資料自動化取得與同步_逐步操作.pdf", "範本_資料盤點與治理.xlsx",
           "高中校務研究資料盤點清冊.docx"],
    "s3": ["治理研習_髒資料_學生學習.xlsx", "治理研習_去識別化練習.xlsx"],
}
BUNDLE_DESC = {
    "開場_高中校務50問.zip": "50 問講義",
    "數據驅動的學校進化_全部素材.zip": "模擬資料、範例儀表板與講義 A–D",
    "校務資料統整平台_練習資料.zip": "五個系統的髒資料（保留資料夾結構，請解壓縮後再開啟）",
    "數據治理與高中校務研究_練習資料.zip": "髒資料與去識別化練習檔",
}


def build_downloads():
    if DL.exists():
        shutil.rmtree(DL)
    DL.mkdir(parents=True)
    manifest = {"bundles": {}, "files": {}}
    for sess, fname, items in BUNDLES:
        zp = DL / fname
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for src, arc in items:
                sp = MAT / src
                if sp.is_dir():
                    for f in sorted(sp.rglob("*")):
                        if f.is_file() and not f.name.endswith(".json"):
                            z.write(f, str(Path(arc) / f.relative_to(sp)) if arc else str(f.relative_to(sp)))
                else:
                    z.write(sp, sp.name)
        manifest["bundles"].setdefault(sess, []).append(
            {"name": fname, "href": f"downloads/{fname}", "size": zp.stat().st_size, "desc": BUNDLE_DESC[fname]})
    for sess, names in SINGLES.items():
        (DL / sess).mkdir(exist_ok=True)
        for n in names:
            shutil.copy2(MAT / sess / n, DL / sess / n)
            manifest["files"].setdefault(sess, []).append(
                {"name": n, "href": f"downloads/{sess}/{n}", "size": (DL / sess / n).stat().st_size, "desc": DESC.get(n, "")})
    # 校務資料統整平台：個別練習檔也開放單獨下載（給只想看其中一個檔的人）
    (DL / "s2" / "練習資料").mkdir(parents=True, exist_ok=True)
    for f in sorted((MAT / "s2" / "練習資料").rglob("*")):
        if f.is_file():
            rel = f.relative_to(MAT / "s2" / "練習資料")
            dst = DL / "s2" / "練習資料" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            manifest.setdefault("practice", []).append(
                {"name": str(rel).replace("\\", "／"), "href": f"downloads/s2/練習資料/{rel.as_posix()}", "size": f.stat().st_size})
    # 加密的解答：只複製 .enc，下載頁輸入密碼後在瀏覽器解密
    lk = MAT / "locked" / "locked.json"
    if lk.exists():
        (DL / "locked").mkdir(exist_ok=True)
        locked = json.load(open(lk, encoding="utf-8"))
        for it in locked:
            shutil.copy2(MAT / "locked" / it["file"], DL / "locked" / it["file"])
            it["href"] = f"downloads/locked/{it['file']}"
        manifest["locked"] = locked
    # 範例儀表板也放一份在網站上直接開
    shutil.copy2(MAT / "s1" / "範例_AI自製校務研究儀表板.html", SITE / "s1" / "dashboard-example.html")
    jdump(manifest, "downloads.json")


if __name__ == "__main__":
    build_s0()
    build_s1()
    build_s2()
    build_s3()
    build_downloads()
    n = sum(1 for _ in DL.rglob("*") if _.is_file())
    print(f"資料 → {DATA}；下載檔 {n} 個 → {DL}")
