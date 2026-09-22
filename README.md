# Local AI Engineer v0.1

Docker-free local AI Engineer for a 32 GB RAM + Intel UHD 620 Windows PC.

Architecture: Angular UI -> .NET 10 Gateway -> Python FastAPI Orchestrator -> Ollama -> local models.

## Models
Start with:
- qwen3:4b
- qwen3:8b

Optional later: qwen3:30b / qwen3-coder:30b. Keep heavy models disabled until the base workflow is tested.

## Prerequisites
- Windows 10/11
- Python 3.11+
- .NET 10 SDK
- Node.js 20+
- Ollama

Install:
```powershell
ollama pull qwen3:4b
ollama pull qwen3:8b
```

## Run
Terminal 1:
```powershell
cd orchestrator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

Terminal 2:
```powershell
dotnet run --project gateway/AiEngineer.Api
```

Terminal 3:
```powershell
cd frontend/ai-engineer-ui
npm install
npm start
```

Set the workspace before running the orchestrator:
```powershell
$env:AI_WORKSPACE="C:\AI\workspace"
```

Default tool policy: read/search allowed; write/shell/git mutation require approval in the tool layer.
