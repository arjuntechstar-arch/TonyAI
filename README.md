# TonyAI v0.2

Docker-free local AI software engineer for Windows.

TonyAI uses:
- Angular UI
- .NET 10 Gateway
- Python FastAPI Orchestrator
- Configuration-driven model routing
- OpenRouter hosted inference as the primary provider
- Ollama with Qwen3 8B as the local fallback
- SQLite project memory

## V0.2 model strategy

TonyAI uses a hosted-first strategy:

**Primary:** OpenRouter `openrouter/free`

**Local fallback:** Ollama `qwen3:8b`

The local fallback is intentionally kept at 8B because this project targets a Windows machine with about 32 GB RAM and integrated graphics. It avoids requiring a larger local model for normal operation.

TonyAI does not require Qwen2.5 14B or Qwen3 4B.

## Providers

### OpenRouter (primary)

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

If OpenRouter fails, TonyAI automatically attempts the local `qwen3:8b` fallback.

### Task progress

TonyAI now returns a task ID immediately and the UI polls task status while the agent runs. Activity includes current step, approximate progress percentage, agent, provider, model, start time, end time, and duration. OpenRouter requests use a 120-second timeout before the local Qwen3 8B fallback is attempted.

### Local Ollama fallback

Install only:

```powershell
ollama pull qwen3:8b
```

You can force local-only mode when needed:

```powershell
$env:AI_PROVIDER="ollama"
```

In local-only mode TonyAI uses `qwen3:8b`.

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
ollama pull qwen3:8b

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

## Current V0.2 scope

Implemented:
- OpenRouter as the primary provider
- `openrouter/free` support
- Ollama provider with Qwen3 8B local fallback
- Provider abstraction for Ollama/OpenRouter
- OpenRouter health detection
- Automatic local fallback when hosted inference fails
- Live task progress with start/end time and duration
- Asynchronous task execution so the gateway does not wait on long model requests
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
