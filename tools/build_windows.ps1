$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$venvPython = Join-Path $projectRoot 'venv\Scripts\python.exe'

if (Test-Path -LiteralPath $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonCommand = Get-Command python -ErrorAction Stop
    $pythonExe = $pythonCommand.Source
}

$tempPath = Join-Path $projectRoot '.tmp-pip'
New-Item -ItemType Directory -Path $tempPath -Force | Out-Null
$oldPath = $env:PATH
$oldTemp = $env:TEMP
$oldTmp = $env:TMP

try {
    $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
    $env:TEMP = $tempPath
    $env:TMP = $tempPath

    & $pythonExe -m PyInstaller --noconfirm --clean (Join-Path $projectRoot 'main_desktop.spec')
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }
} finally {
    $env:PATH = $oldPath
    $env:TEMP = $oldTemp
    $env:TMP = $oldTmp
}

$distPath = Join-Path $projectRoot 'dist\Controle de Buffs'
$exePath = Join-Path $distPath 'Controle de Buffs.exe'
$shortcutPath = Join-Path $distPath 'Controle de Buffs.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = $distPath
$shortcut.IconLocation = "$exePath,0"
$shortcut.Save()

$zipPath = Join-Path $projectRoot 'dist\Controle-de-Buffs-Windows.zip'
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath
}
Compress-Archive -Path $distPath -DestinationPath $zipPath -CompressionLevel Optimal

Write-Host "Portable folder created at $distPath"
Write-Host "Portable ZIP created at $zipPath"
