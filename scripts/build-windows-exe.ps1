# Build Standalone MetaRang-3D-Tester-V5.exe locally on Windows
$ErrorActionPreference = "Stop"
python -m pip install --upgrade pip pillow pyinstaller
pyinstaller --noconfirm --onefile --windowed `
    --name "MetaRang-3D-Tester-V5" `
    --add-data "scripts/analyze_3d_model.py;scripts" `
    --add-data "scripts/validators;scripts/validators" `
    --add-data "schemas/category-registry.json;schemas" `
    tools/metarang_3d_tester_gui.py
Write-Host "Done! Executable created at: dist\MetaRang-3D-Tester-V5.exe" -ForegroundColor Green
