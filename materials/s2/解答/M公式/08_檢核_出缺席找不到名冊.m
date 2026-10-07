let
    反向合併 = Table.NestedJoin(出缺席, {"學號"}, 名冊, {"學號"}, "名冊", JoinKind.LeftAnti),
    移除 = Table.RemoveColumns(反向合併, {"名冊"})
in
    移除
