let
    來源 = Excel.Workbook(File.Contents(資料夾路徑 & "系統A_學生名冊.xlsx"), null, true),
    工作表 = 來源{[Item = "學生名冊", Kind = "Sheet"]}[Data],
    升階標頭 = Table.PromoteHeaders(工作表, [PromoteAllScalars = true]),
    移除個資 = Table.RemoveColumns(升階標頭, {"姓名", "出生日期", "戶籍地址"}),
    型態 = Table.TransformColumnTypes(移除個資, {{"學號", type text}, {"班級", type text}})
in
    型態
