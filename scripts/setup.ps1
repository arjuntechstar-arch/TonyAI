$ErrorActionPreference="Stop"
python --version
dotnet --version
node --version
ollama --version
ollama pull qwen3:4b
ollama pull qwen3:8b
Write-Host "Setup complete."
