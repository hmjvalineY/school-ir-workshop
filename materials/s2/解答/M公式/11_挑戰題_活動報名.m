let
    來源 = Excel.Workbook(File.Contents(資料夾路徑 & "表單_活動報名.xlsx"), null, true),
    工作表 = 來源{[Item = "表單回應 1", Kind = "Sheet"]}[Data],
    升階標頭 = Table.PromoteHeaders(工作表, [PromoteAllScalars = true]),
    改名 = Table.RenameColumns(升階標頭, {{"請輸入你的學號", "原始學號"}, {"想參加的活動", "活動"}}),
    加序號 = Table.AddIndexColumn(改名, "提交順序", 1, 1, Int64.Type),
    半形 = Table.AddColumn(加序號, "學號", each Text.Select(
        Text.Combine(List.Transform(Text.ToList(Text.From([原始學號])),
            each let c = Character.ToNumber(_) in
                if c >= 65296 and c <= 65305 then Character.FromNumber(c - 65248) else _)),
        {"0".."9"}), type text),
    排序 = Table.Buffer(Table.Sort(半形, {{"提交順序", Order.Descending}})),
    去重 = Table.Distinct(排序, {"學號", "活動"}),
    對名冊 = Table.NestedJoin(去重, {"學號"}, 名冊, {"學號"}, "名冊", JoinKind.LeftOuter),
    標記 = Table.AddColumn(對名冊, "對照結果", each if Table.IsEmpty([名冊]) then "需人工確認" else "有效", type text),
    移除 = Table.RemoveColumns(標記, {"名冊"})
in
    移除
