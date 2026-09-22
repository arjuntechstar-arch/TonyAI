# TonyAI v0.2

Docker-free local AI software engineer for Windows.

TonyAI uses:
- Angular UI
- .NET 10 Gateway
- Python FastAPI Orchestrator
- Configuration-driven model routing
- Ollama local inference
- Optional OpenRouter hosted inference
- SQLite project memory

## V0.2 model strategy

The default local engineering model is **Qwen2.5 14B Instruct**:
`qwen2.5:14b-instruct`

The Ollama model is about 9 GB in the default Q4_K_M build. A 32 GB RAM machine can run it, although CPU-only inference will be slower than GPU inference.

The small `qwen3:4b` model is retained as an emergency local fallback when OpenRouter is enabled and hosted inference fails.

## Providers

### Local Ollama (default)

No API key is required.

```powershell
$env:AI_PROVIDER="ollama"
```

### OpenRouter (optional)

OpenRouter uses its OpenAI-compatible API. TonyAI defaults to:
`openrouter/free`

Set:

```powershell
$env:AI_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="YOUR_KEY"
```

Optional:

```powershell
$env:OPENROUTER_MODEL="openrouter/free"
$env:OPENROUTER_APP_NAME="TonyAI"
$env:OPENROUTER_APP_URL="http://localhost:4200"
```

If OpenRouter fails, TonyAI attempts the local `qwen3:4b` fallback.

## Prerequisites

- Windows 10/11
- Python 3.11+
- .NET 10 SDK
- Node.js 20+
- Ollama

## Setup

From the repository root:

```powershell
.\scripts\setup.ps1
```

Or manually:

```powershell
ollama pull qwen2.5:14b-instruct
ollama pull qwen3:4b

cd orchestrator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

### Recommended

```powershell
.\scripts\start.ps1
```

### Manual

Terminal 1:

```powershell
cd orchestrator
.\.venv\Scripts\Activate.ps1
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

Default ports:
- Angular: 4200
- .NET Gateway: 5000
- Orchestrator: 8100
- Ollama: 11434

## Test the orchestrator directly

```powershell
$body = '{"task":"Say hello in one sentence","project":"test","complexity":1}'
Invoke-RestMethod -Uri "http://127.0.0.1:8100/task" -Method Post -ContentType "application/json" -Body $body
```

## Important V0.1 fixes preserved

V0.2 keeps the V0.1 working path intact:
- FastAPI orchestrator remains on port 8100.
- .NET gateway remains the UI boundary.
- Angular continues to call the gateway rather than Ollama directly.
- Existing SQLite memory remains in place.
- Existing CORS behavior remains unchanged.
- Existing approval-oriented tool policy remains documented.
- No Docker requirement was introduced.

## Current V0.2 scope

Implemented:
- Qwen2.5 14B primary local model
- Provider abstraction for Ollama/OpenRouter
- OpenRouter free-model router support
- OpenRouter health detection
- Local fallback when hosted inference fails
- Planner/engineer/reviewer/debugger/tester routing
- Improved health/model information

Next:
- Structured tool calling
- Streaming events
- Approval UI
- File edit loop
- Build/test/debug execution loop
- Git worktree isolation
- Repository indexing/RAG
