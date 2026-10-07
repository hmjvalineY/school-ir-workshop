let
    篩選 = Table.SelectRows(學習歷程, each [學號] = null)
in
    篩選
