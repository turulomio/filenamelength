Output howto.gif

Set FontSize 10
Set Width 1600
Set Height 595
Set Theme "Catppuccin Mocha"
Set Padding 15

Env LC_ALL "C.UTF-8"
Env LANG "C.UTF-8"
Env LANGUAGE "en_US:en"

Type "# Step 1: Filter files with filename length >= 25 and sort by length"
Sleep 1s
Enter
Sleep 500ms

Type "filenamelength --minimum_filename_length 25 --order_by FilenameLength"
Sleep 500ms
Enter
Sleep 4s

Type "# Step 2: Automatically rename files exceeding the limit"
Sleep 1s
Enter
Sleep 500ms

Type "filenamelength --minimum_filename_length 25 --rename"
Sleep 500ms
Enter
Sleep 4s

Type "# Step 3: Undo the rename operation and restore original filenames"
Sleep 1s
Enter
Sleep 500ms

Type "filenamelength --undo"
Sleep 500ms
Enter
Sleep 20s



