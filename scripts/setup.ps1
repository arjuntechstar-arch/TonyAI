$ErrorActionPreference="Stop"

Write-Host "Checking prerequisites..."
python --version
dotnet --version
node --version
ollama --version

Write-Host "Pulling local fallback model: qwen3:8b"
ollama pull qwen3:8b

Write-Host "Creating Python environment..."
$root = Split-Path -Parent $PSScriptRoot
Set-Location "$root/orchestrator"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host "Primary provider: OpenRouter"
Write-Host "Primary model: openrouter/free"
Write-Host "Local fallback: qwen3:8b"
Write-Host "Set OPENROUTER_API_KEY before starting TonyAI."
