$env:APPLYPILOT_DIR = $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\applypilot.exe" apply --limit 1 --dry-run --min-score 7
