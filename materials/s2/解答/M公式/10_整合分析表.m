let
    成績平均 = Table.Group(Table.SelectRows(段考成績, each [狀態] = "正常"), {"學號"},
        {{"五科平均", each Number.Round(List.Average([成績]), 1), type number}}),
    曠課 = Table.Group(Table.SelectRows(出缺席, each [假別] = "曠課"), {"學號"},
        {{"曠課節數", each Table.RowCount(_), Int64.Type}}),
    歷程 = Table.AddColumn(
        Table.SelectColumns(Table.SelectRows(學習歷程, each [學號] <> null), {"學號", "課程學習成果_已上傳", "課程學習成果_應上傳"}),
        "上傳率", each Number.Round([課程學習成果_已上傳] / [課程學習成果_應上傳] * 100, 1), type number),
    名冊班群 = Table.ExpandTableColumn(
        Table.NestedJoin(名冊, {"班級"}, 班級對照, {"標準班級"}, "對照", JoinKind.LeftOuter), "對照", {"班群"}),
    接成績 = Table.ExpandTableColumn(Table.NestedJoin(名冊班群, {"學號"}, 成績平均, {"學號"}, "t", JoinKind.LeftOuter), "t", {"五科平均"}),
    接曠課 = Table.ExpandTableColumn(Table.NestedJoin(接成績, {"學號"}, 曠課, {"學號"}, "t", JoinKind.LeftOuter), "t", {"曠課節數"}),
    接歷程 = Table.ExpandTableColumn(Table.NestedJoin(接曠課, {"學號"}, 歷程, {"學號"}, "t", JoinKind.LeftOuter), "t", {"上傳率"}),
    曠課補零 = Table.ReplaceValue(接歷程, null, 0, Replacer.ReplaceValue, {"曠課節數"}),
    選欄 = Table.SelectColumns(曠課補零, {"學號", "班級", "班群", "入學管道", "五科平均", "曠課節數", "上傳率"}),
    排序 = Table.Sort(選欄, {{"學號", Order.Ascending}})
in
    排序
