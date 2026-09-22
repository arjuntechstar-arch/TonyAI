# TonyAI Roadmap

## V0.1 — Foundation

- Ollama
- Qwen3 4B/8B
- Model registry
- Basic task routing
- Planner/coder/reviewer
- Workspace-safe tool layer
- SQLite memory
- .NET gateway
- Angular UI

## V0.2 — Provider + Agent Foundation

Completed:
- Qwen2.5 14B as the primary local model
- Configuration-driven provider abstraction
- Ollama provider
- OpenRouter provider
- `openrouter/free` support
- Local fallback when hosted inference fails
- Planner/engineer/reviewer/debugger/tester routing
- Improved health and model reporting
- V0.1 runtime path preserved

## V0.3 — Autonomous Tool Loop

- Structured tool calling
- Streaming agent events
- Approval UI
- File read/search/edit tools
- Terminal build/test execution
- Automatic debug -> fix -> test loop
- Git status/diff integration

## V0.4 — Repository Intelligence

- Git worktree isolation
- Repository indexing
- Embeddings/RAG
- Symbol-aware code context
- Persistent project memory
- Better context-window management

## V1.0 — Safe Autonomous Engineer

- Plan -> implement -> build -> test -> debug -> review loop
- Hardware-aware provider/model routing
- Hosted quota/rate-limit awareness
- Benchmarking
- Audit trail
- Production-grade approvals and recovery
