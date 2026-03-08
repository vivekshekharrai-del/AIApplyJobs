$env:APPLYPILOT_DIR = "C:\Users\vivek\Jobs"
Set-Location "C:\Users\vivek\Jobs"
& "C:\Users\vivek\Jobs\venv\Scripts\applypilot.exe" apply --limit 9 --min-score 7
