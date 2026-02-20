$env:APPLYPILOT_DIR = $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\applypilot.exe" run tailor cover --min-score 7
