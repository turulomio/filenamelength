Output howto.gif

Set FontSize 10
Set Width 1600
Set Height 850
Set Theme "Catppuccin Mocha"
Set Padding 15

Env LC_ALL "C.UTF-8"
Env LANG "C.UTF-8"
Env LANGUAGE "en_US:en"


Type "filenamelength --minimum_filename_length 25 --order_by FilenameLength"
Sleep 500ms
Enter
Sleep 4s

Type "filenamelength --minimum_filename_length 25 --rename"
Sleep 500ms
Enter
Sleep 4s

Type "filenamelength --undo"
Sleep 500ms
Enter
Sleep 20s



