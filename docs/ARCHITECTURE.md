# TonyAI v0.2 Architecture

```text
Angular UI
    |
.NET 10 Gateway
    |
Python FastAPI Orchestrator
    |
    +---------------------------+
    | Model Router / Registry   |
    +-------------+-------------+
                  |
          OpenRouter Primary
                  |
           openrouter/free
                  |
          request/API failure
                  |
            Ollama Fallback
                  |
               qwen3:8b
                  |
             Agent Manager
                  |
     +------------+------------+
     |      |       |     |    |
  Planner Coder Reviewer Debugger Tester
                  |
           Memory / State
                  |
               SQLite
                  |
            Future Tool Layer
            Files / Terminal / Git
```

## Model strategy

TonyAI is hosted-first.

- **Primary provider:** OpenRouter
- **Primary model route:** `openrouter/free`
- **Local fallback:** Ollama `qwen3:8b`

The hosted model can change behind `openrouter/free`, so TonyAI does not hard-code a specific hosted model into agent code.

The local machine only needs Qwen3 8B. A larger local model is intentionally not required for the normal workflow.

## Provider selection

Default:

`AI_PROVIDER=openrouter`

For local-only operation:

`AI_PROVIDER=ollama`

When OpenRouter execution fails, the orchestrator automatically retries the same agent task using the local `qwen3:8b` model.

## Why provider abstraction

The model provider is deliberately separated from the agent layer. Agents send standard chat messages to a client interface, so switching between local Ollama and hosted OpenRouter does not require changing planner/coder/reviewer code.

## Safety

The V0.2 provider layer does not grant the model unrestricted machine access.

The existing safety policy remains:
- Read/search operations: automatic.
- File writes: approval-gated.
- Shell mutation: approval-gated.
- Git mutation: approval-gated.

Actual tool execution and approval UI are V0.3 work.

## Runtime flow

1. Angular sends a task to the .NET gateway.
2. Gateway forwards the task to FastAPI.
3. ModelRouter selects planner, engineer, reviewer, debugger or tester.
4. OpenRouter is used first.
5. If hosted execution fails, Ollama `qwen3:8b` is used.
6. The selected agent receives task + recent project memory.
7. Result is stored in SQLite.
8. Result is returned through the gateway to Angular.

## Hardware note

Qwen3 8B is the only local model required by TonyAI.

On a 32 GB RAM Windows machine with integrated graphics, CPU inference is expected. The 8B model is intended as a practical local fallback rather than the normal primary path.
