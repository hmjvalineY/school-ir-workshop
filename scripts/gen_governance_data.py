# -*- coding: utf-8 -*-
"""第三場《數據治理與高中校務研究》練習用髒資料產生器。

全部為模擬資料（姓名遮罩、無真實個資）。固定亂數種子，每次產生結果相同。
輸出到 materials/s3/：
  治理研習_髒資料_學生學習.xlsx      —— 學員下載練習用（開場實驗、小操作一、二）
  private/s3/治理研習_解答_問題清單.xlsx —— 解答（不進版控，由 lock_answers.py 加密）
  治理研習_去識別化練習.xlsx          —— 小操作三
"""
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "materials" / "s3"
OUT.mkdir(parents=True, exist_ok=True)
random.seed(20261008)

SURN = "陳林黃張李王吳劉蔡楊許鄭謝郭洪曾邱廖賴周"
GIVEN = ["宇", "恩", "翔", "晴", "妤", "辰", "安", "庭", "睿", "涵", "彤", "哲", "佑", "萱", "誠"]
CLASSES = ["301", "302", "303"]
COLS = ["學號", "姓名", "性別", "班級", "學年學期", "學籍狀態", "國文", "英文", "數學", "本學期缺曠節數", "資料更新日"]

# ---------- 乾淨母體 ----------
clean = []
for i in range(1, 57):
    sid = f"111{i:03d}"
    base = random.gauss(0, 8)
    sc = lambda m: int(round(min(98, max(30, random.gauss(m + base, 10)))))
    clean.append({
        "學號": sid, "姓名": random.choice(SURN) + "O" + random.choice(GIVEN),
        "性別": random.choice(["男", "女"]), "班級": CLASSES[(i - 1) // 19],
        "學年學期": "113-1", "學籍狀態": "在學",
        "國文": sc(72), "英文": sc(68), "數學": sc(64),
        "本學期缺曠節數": min(30, int(random.expovariate(1 / 5))), "資料更新日": "2024/11/01",
    })
by = {r["學號"]: r for r in clean}

# 刻意設計的邊界個案（乾淨值），讓髒資料會改變「誰有學習落後風險」的答案
by["111005"].update(國文=58, 英文=52, 數學=38, 本學期缺曠節數=4)    # 真實：有風險
by["111044"].update(國文=62, 英文=65, 數學=60, 本學期缺曠節數=3)    # 真實：無風險
by["111023"].update(國文=45, 英文=50, 數學=48, 本學期缺曠節數=6)    # 真實：有風險
by["111017"].update(國文=64, 英文=62, 數學=35, 本學期缺曠節數=2)    # 真實：有風險
by["111012"].update(國文=55, 英文=50, 數學=42, 本學期缺曠節數=9)    # 真實：有風險
by["111031"].update(國文=40, 英文=38, 數學=35, 本學期缺曠節數=12, 學籍狀態="休學")  # 已休學
by["111048"].update(學籍狀態="轉出", 本學期缺曠節數=7)

# ---------- 注入問題 ----------
import copy
dirty = [copy.deepcopy(r) for r in clean]
D = {r["學號"]: r for r in dirty}
issues = []   # (學號, 欄位, 髒值, 問題, 面向, 處理建議)


def bad(sid, col, val, what, dim, fix):
    old = D[sid][col]
    D[sid][col] = val
    issues.append(dict(學號=sid, 欄位=col, 髒值=val, 正確值=old, 問題=what, 面向=dim, 處理建議=fix))


bad("111005", "數學", 120, "成績超出 0–100 值域", "正確性", "回查原始成績單，修正後再分析")
bad("111044", "英文", -5, "成績為負數", "正確性", "回查原始成績單；負數一律視為錯誤")
bad("111023", "國文", 999, "999 是系統的「缺考代碼」，被當成分數", "正確性", "代碼轉為「缺考」狀態，不納入平均")
bad("111017", "數學", None, "必填成績空白", "完整性", "確認是缺考還是漏登，不可直接略過")
bad("111029", "性別", None, "性別空白", "完整性", "由學籍系統補齊")
bad("111050", "班級", None, "班級空白", "完整性", "以名冊為準補齊")
for sid in ("111008", "111027", "111041"):
    bad(sid, "學年學期", "1131", "學期代碼寫成 1131，與其他列 113-1 不一致", "一致性", "統一為 113-1")
for sid, v in (("111003", "1"), ("111020", "2"), ("111039", "1")):
    bad(sid, "性別", v, f"性別用代碼 {v}，其他列用男／女", "一致性", "依代碼表轉換（1＝男、2＝女）")
for sid in ("111006", "111015"):
    bad(sid, "班級", "三年一班", "班級寫成「三年一班」，其他列為 301", "一致性", "以班級對照表統一為 301")
for sid in ("111034", "111052", "111055"):
    bad(sid, "資料更新日", "2023/06/30", "資料一年多未更新", "即時性", "重新匯出最新資料，並標明匯出日期")
issues.append(dict(學號="111031", 欄位="學籍狀態", 髒值="休學", 正確值="休學",
                   問題="已休學，卻仍有本學期成績與 12 節缺曠", 面向="有效性",
                   處理建議="與註冊組確認休學日期；休學後的紀錄不納入分析"))
issues.append(dict(學號="111048", 欄位="學籍狀態", 髒值="轉出", 正確值="轉出",
                   問題="已轉出，卻仍有本學期缺曠紀錄", 面向="有效性",
                   處理建議="確認轉出日期，轉出後的紀錄應排除"))

rows = list(dirty)
dup1 = copy.deepcopy(D["111012"])                      # 完全重複
dup2 = copy.deepcopy(D["111037"]); dup2["數學"] = dup2["數學"] - 17   # 同學號、成績不同
rows.insert(20, dup1)
rows.insert(45, dup2)
issues.append(dict(學號="111012", 欄位="（整列）", 髒值="重複", 正確值="—", 問題="同一位學生出現兩列，內容完全相同",
                   面向="唯一性", 處理建議="移除重複列；計算人數時特別注意"))
issues.append(dict(學號="111037", 欄位="（整列）", 髒值="重複", 正確值="—", 問題="同學號兩列，數學成績卻不同",
                   面向="唯一性", 處理建議="不能只刪一列，要回查哪一筆才正確"))

# Excel 列號（含標題列）
row_of = {}
for k, r in enumerate(rows, start=2):
    row_of.setdefault(r["學號"], []).append(k)
for it in issues:
    it["Excel列"] = "、".join(map(str, row_of[it["學號"]]))

# ---------- 寫檔 ----------
def write(path, sheets):
    wb = Workbook()
    wb.remove(wb.active)
    for name, header, data in sheets:
        ws = wb.create_sheet(name)
        ws.append(header)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="1F2A44")
        for r in data:
            ws.append([r.get(h) for h in header])
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 14
    wb.save(path)


write(OUT / "治理研習_髒資料_學生學習.xlsx", [("學生學習資料", COLS, rows)])
IK = ["Excel列", "學號", "欄位", "髒值", "正確值", "問題", "面向", "處理建議"]
PRIV = ROOT / "private" / "s3"          # 解答不進版控，由 lock_answers.py 加密後才上網站
PRIV.mkdir(parents=True, exist_ok=True)
write(PRIV / "治理研習_解答_問題清單.xlsx", [("問題清單", IK, issues), ("乾淨版本", COLS, clean)])

# 去識別化練習（姓名為示意用常見假名）
FAKE = ["王小明", "陳大華", "林美玲", "張志豪", "李佳穎", "黃建宏", "吳宜蓁", "劉冠廷", "蔡雅婷", "楊承恩"]
DIST = ["中壢區", "桃園區", "平鎮區", "八德區", "龜山區"]
deid = []
for k, nm in enumerate(FAKE):
    deid.append({"學號": f"111{k + 101:03d}", "姓名": nm, "出生日期": f"2007/{random.randint(1, 12):02d}/{random.randint(1, 28):02d}",
                 "班級": random.choice(CLASSES), "居住區": random.choice(DIST), "數學": random.randint(35, 95),
                 "輔導紀錄": random.choice(["無", "無", "無", "有（限閱）"])})
DK = ["學號", "姓名", "出生日期", "班級", "居住區", "數學", "輔導紀錄"]
write(OUT / "治理研習_去識別化練習.xlsx", [("原始資料", DK, deid)])

json.dump({"columns": COLS, "dirty": rows, "clean": clean, "issues": issues, "deid": deid, "deid_cols": DK},
          open(OUT / "s3_source.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"髒資料 {len(rows)} 列、問題 {len(issues)} 項 → {OUT}")
