let
    來源 = Folder.Files(資料夾路徑 & "出缺席_每月匯出"),
    只留CSV = Table.SelectRows(來源, each Text.Lower([Extension]) = ".csv"),
    解析 = Table.AddColumn(只留CSV, "資料", each Table.PromoteHeaders(
        Csv.Document([Content], [Delimiter = ",", Encoding = 950, QuoteStyle = QuoteStyle.Csv]),
        [PromoteAllScalars = true])),
    保留 = Table.SelectColumns(解析, {"Name", "資料"}),
    展開 = Table.ExpandTableColumn(保留, "資料", {"日期", "班級", "座號", "學號", "姓名", "節次", "假別", "登錄者"}),
    改名 = Table.RenameColumns(展開, {{"Name", "來源檔"}}),
    學號文字 = Table.TransformColumnTypes(改名, {{"學號", type text}}),
    修剪 = Table.TransformColumns(學號文字, {{"學號", Text.Trim, type text}}),
    去重 = Table.Distinct(修剪),
    移除個資 = Table.RemoveColumns(去重, {"姓名", "班級", "座號"}),
    西元日期 = Table.AddColumn(移除個資, "西元日期", each #date(
        Number.From(Text.BeforeDelimiter([日期], "/")) + 1911,
        Number.From(Text.BetweenDelimiters([日期], "/", "/")),
        Number.From(Text.AfterDelimiter([日期], "/", 1))), type date),
    學年學期 = Table.AddColumn(西元日期, "學年學期", each
        let y = Date.Year([西元日期]) - 1911, m = Date.Month([西元日期])
        in if m >= 8 then Text.From(y) & "-1"
           else if m = 1 then Text.From(y - 1) & "-1"
           else Text.From(y - 1) & "-2", type text)
in
    學年學期
