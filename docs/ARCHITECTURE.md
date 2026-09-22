# AI Engineer v0.2 Architecture

```text
Angular UI
   |
.NET 10 Gateway
   |
Python FastAPI Orchestrator
   |
Model Router / Registry
   |
Qwen2.5-14B-Instruct (primary)
   |
Tool Layer ---- Files / Terminal / Git
   |
Build / Test / Debug / Review
   |
SQLite project memory
```

## Model strategy

Qwen2.5-14B-Instruct is the default model for planning, engineering, review, debugging and test analysis. This keeps one strong general engineering model active instead of switching between the previous Qwen3 4B/8B roles.

The client layer supports both Ollama and OpenRouter. The provider is selected with `AI_PROVIDER`. The model registry remains configuration-driven.

## Safety

Read/search operations are automatic. File writes, shell mutation and Git mutation remain approval-gated by the tool layer.
