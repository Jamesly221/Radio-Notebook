$ErrorActionPreference = 'Stop'
$AppRoot = $PSScriptRoot
if (!(Test-Path (Join-Path $AppRoot 'Radio-Notebook.exe'))) {
    $AppRoot = Split-Path $PSScriptRoot -Parent
}
$Exe = Join-Path $AppRoot 'Radio-Notebook.exe'
$Shell = New-Object -ComObject WScript.Shell
$Link = $Shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Radio Notebook.lnk'))
if (Test-Path $Exe) {
    $Link.TargetPath = $Exe
    $Link.IconLocation = "$Exe,0"
} else {
    $Python = Get-Command pythonw.exe -ErrorAction Stop
    $Link.TargetPath = $Python.Source
    $Link.Arguments = '"' + (Join-Path $AppRoot 'main.py') + '"'
}
$Link.WorkingDirectory = $AppRoot
$Link.Save()
Write-Host 'Created Radio Notebook desktop shortcut.'
