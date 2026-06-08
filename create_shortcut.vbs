Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oShellLink = WshShell.CreateShortcut(strDesktop & "\SitLessBunny.lnk")
oShellLink.TargetPath = "pythonw"
oShellLink.Arguments = Chr(34) & "D:\indieHacker\tools\sedentaryReminder\main.py" & Chr(34)
oShellLink.WorkingDirectory = "D:\indieHacker\tools\sedentaryReminder"
oShellLink.Description = "SitLessBunny"
oShellLink.IconLocation = "D:\indieHacker\tools\sedentaryReminder\app_icon.ico, 0"
oShellLink.WindowStyle = 7
oShellLink.Save
WScript.Echo "Done"
