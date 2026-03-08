$env:APPLYPILOT_DIR = $PSScriptRoot
Set-Location $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\python.exe" "$PSScriptRoot\run_dice.py"
