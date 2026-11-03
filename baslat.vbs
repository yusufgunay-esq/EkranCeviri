Set fso = CreateObject("Scripting.FileSystemObject")
Set s = CreateObject("WScript.Shell")
s.Run "pyw """ & fso.GetParentFolderName(WScript.ScriptFullName) & "\baslat.pyw""", 0, False
