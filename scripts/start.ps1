$ErrorActionPreference="Stop"
$root=Split-Path -Parent $PSScriptRoot
if(-not $env:AI_WORKSPACE){$env:AI_WORKSPACE=Join-Path $root "workspace/projects"}
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location '$root/orchestrator'; .\.venv\Scripts\Activate.ps1; python -m app.main"
Start-Sleep 2
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location '$root'; dotnet run --project gateway/AiEngineer.Api"
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location '$root/frontend/ai-engineer-ui'; npm install; npm start"
