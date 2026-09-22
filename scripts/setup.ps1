$ErrorActionPreference="Stop"

Write-Host "Checking prerequisites..."
python --version
dotnet --version
node --version
ollama --version

Write-Host "Pulling primary local model: qwen2.5:14b-instruct"
ollama pull qwen2.5:14b-instruct

Write-Host "Pulling emergency fallback: qwen3:4b"
ollama pull qwen3:4b

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
Write-Host "Default provider: Ollama"
Write-Host "Primary model: qwen2.5:14b-instruct"
Write-Host "Optional hosted provider: set AI_PROVIDER=openrouter and OPENROUTER_API_KEY"
