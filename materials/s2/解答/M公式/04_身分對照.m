let
    來源 = Excel.Workbook(File.Contents(資料夾路徑 & "對照表.xlsx"), null, true),
    工作表 = 來源{[Item = "身分對照", Kind = "Sheet"]}[Data],
    升階標頭 = Table.PromoteHeaders(工作表, [PromoteAllScalars = true]),
    型態 = Table.TransformColumnTypes(升階標頭, {{"學號", type text}, {"學校帳號", type text}})
in
    型態
