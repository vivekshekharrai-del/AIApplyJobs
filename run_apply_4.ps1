$env:APPLYPILOT_DIR = $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\applypilot.exe" apply --limit 4 --min-score 7
