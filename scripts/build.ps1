$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Removing previous build output..."

Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
Remove-Item -Force "XAtlasGUI.spec" -ErrorAction SilentlyContinue

Write-Host "Building XAtlasGUI.exe..."

uv run pyinstaller `
    --noconfirm `
    --clean `
    --onefile `
    --name "XAtlasGUI" `
    --paths "src" `
    --collect-all "xatlas" `
    --collect-all "trimesh" `
    --hidden-import "xatlas_gui" `
    --hidden-import "xatlas_gui.cli" `
    --hidden-import "xatlas_gui.gui" `
    --hidden-import "xatlas_gui.core" `
    --hidden-import "xatlas_gui.obj_io" `
    --hidden-import "xatlas_gui.settings" `
    "launcher.py"

Write-Host ""
Write-Host "Build complete:"
Write-Host "$ProjectRoot\dist\XAtlasGUI.exe"