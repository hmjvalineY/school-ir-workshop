let
    來源 = Csv.Document(File.Contents(資料夾路徑 & "系統D_學習歷程.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    升階標頭 = Table.PromoteHeaders(來源, [PromoteAllScalars = true]),
    型態 = Table.TransformColumnTypes(升階標頭, {
        {"課程學習成果_應上傳", Int64.Type}, {"課程學習成果_已上傳", Int64.Type},
        {"課程學習成果_已認證", Int64.Type}, {"多元表現_已上傳", Int64.Type}}),
    合併身分對照 = Table.NestedJoin(型態, {"帳號"}, 身分對照, {"學校帳號"}, "身分對照", JoinKind.LeftOuter),
    展開學號 = Table.ExpandTableColumn(合併身分對照, "身分對照", {"學號"}),
    學年學期 = Table.AddColumn(展開學號, "學年學期", each Text.From([學年度]) & "-" & Text.From([學期]), type text),
    刪系統D班級 = Table.RemoveColumns(學年學期, {"班級"}),
    合併名冊 = Table.NestedJoin(刪系統D班級, {"學號"}, 名冊, {"學號"}, "名冊", JoinKind.LeftOuter),
    展開班級 = Table.ExpandTableColumn(合併名冊, "名冊", {"班級", "入學管道"}),
    合併班級對照 = Table.NestedJoin(展開班級, {"班級"}, 班級對照, {"標準班級"}, "班級對照", JoinKind.LeftOuter),
    展開班群 = Table.ExpandTableColumn(合併班級對照, "班級對照", {"班群"})
in
    展開班群
