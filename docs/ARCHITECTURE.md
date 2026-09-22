# TonyAI v0.2 Architecture

```text
Angular UI
    |
.NET 10 Gateway
    |
Python FastAPI Orchestrator
    |
    +----------------------+
    | Model Router/Registry|
    +----------+-----------+
               |
        +------+------+
        |             |
      Ollama       OpenRouter
        |             |
 Qwen2.5 14B     openrouter/free
        |
  qwen3:4b fallback
               |
          Agent Manager
               |
     +---------+---------+
     |    |      |       |
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

The default local model is `qwen2.5:14b-instruct`. All current agent roles use the same primary model so TonyAI does not need to keep multiple medium-sized models loaded.

The registry is configuration-driven. A provider can be selected with:

`AI_PROVIDER=ollama`

or:

`AI_PROVIDER=openrouter`

When OpenRouter is selected, TonyAI uses `OPENROUTER_MODEL`, defaulting to `openrouter/free`. If hosted execution fails, the orchestrator attempts the configured local fallback `qwen3:4b`.

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
4. Provider selection chooses Ollama or OpenRouter.
5. The selected agent receives task + recent project memory.
6. Result is stored in SQLite.
7. Result is returned through the gateway to Angular.

## Hardware note

Qwen2.5 14B is available in Ollama as `qwen2.5:14b-instruct`; the listed default Q4_K_M build is about 9 GB.

On a 32 GB RAM Windows machine with integrated graphics, CPU inference is expected. Keep only one primary model active at a time.
