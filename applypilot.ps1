# ApplyPilot launcher — runs applypilot from the Jobs folder
# Usage: .\applypilot.ps1 [command] [args]
# Examples:
#   .\applypilot.ps1 run
#   .\applypilot.ps1 run discover
#   .\applypilot.ps1 status
#   .\applypilot.ps1 dashboard
#   .\applypilot.ps1 apply

$env:APPLYPILOT_DIR = $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\applypilot.exe" @args
