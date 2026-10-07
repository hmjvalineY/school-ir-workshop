let
    來源 = Excel.Workbook(File.Contents(資料夾路徑 & "系統B_段考成績.xlsx"), null, true),
    工作表 = 來源{[Item = "成績一覽表", Kind = "Sheet"]}[Data],
    移除頂端 = Table.Skip(工作表, 3),
    升階標頭 = Table.PromoteHeaders(移除頂端, [PromoteAllScalars = true]),
    篩選學號 = Table.SelectRows(升階標頭, each [學號] <> null and [學號] <> "學號"),
    移除欄 = Table.RemoveColumns(篩選學號, {"班級", "座號", "總分", "平均", "名次"}),
    學號文字 = Table.TransformColumnTypes(移除欄, {{"學號", type text}}),
    填未登錄 = Table.ReplaceValue(學號文字, null, "未登錄", Replacer.ReplaceValue, {"國文", "英文", "數學", "自然", "社會"}),
    逆透視 = Table.UnpivotOtherColumns(填未登錄, {"學號"}, "科目", "原始值"),
    半形值 = Table.AddColumn(逆透視, "半形值", each Text.Combine(List.Transform(
        Text.ToList(Text.From([原始值])),
        each let c = Character.ToNumber(_) in
            if c >= 65296 and c <= 65305 then Character.FromNumber(c - 65248) else _))),
    狀態 = Table.AddColumn(半形值, "狀態", each
        if [原始值] = "缺" then "缺考" else if [原始值] = "未登錄" then "未登錄" else "正常", type text),
    成績 = Table.AddColumn(狀態, "成績", each if [狀態] = "正常" then Number.From([半形值]) else null, Int64.Type),
    移除暫存欄 = Table.RemoveColumns(成績, {"原始值", "半形值"}),
    加學年學期 = Table.AddColumn(移除暫存欄, "學年學期", each "113-1", type text),
    加考試別 = Table.AddColumn(加學年學期, "考試別", each "第1次段考", type text)
in
    加考試別
