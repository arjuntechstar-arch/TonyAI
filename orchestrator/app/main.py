import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agents.coder import CoderAgent
from .agents.planner import PlannerAgent
from .agents.reviewer import ReviewerAgent
from .memory.store import MemoryStore
from .models.model_router import ModelRouter
from .models.ollama_client import OllamaClient
from .models.openrouter_client import OpenRouterClient


app = FastAPI(title="TonyAI Orchestrator", version="0.2.0")

ollama = OllamaClient()
openrouter = OpenRouterClient()
router = ModelRouter()
memory = MemoryStore()

agents = {
    "planner": PlannerAgent(),
    "engineer": CoderAgent(),
    "reviewer": ReviewerAgent(),
    "debugger": CoderAgent(),
    "tester": CoderAgent(),
}


class TaskRequest(BaseModel):
    task: str = Field(min_length=1)
    project: str = "default"
    complexity: int = Field(default=5, ge=1, le=10)


def provider_name() -> str:
    return os.getenv("AI_PROVIDER", "openrouter").lower()


def client_for(provider: str):
    if provider == "openrouter":
        return openrouter
    if provider == "ollama":
        return ollama
    raise ValueError(
        f"Unsupported AI_PROVIDER '{provider}'. Use 'openrouter' or 'ollama'."
    )


@app.get("/health")
async def health():
    provider = provider_name()
    ollama_ok = False
    openrouter_ok = False
    ollama_models = []

    try:
        data = await ollama.list_models()
        ollama_ok = True
        ollama_models = data.get("models", [])
    except Exception:
        pass

    if provider == "openrouter":
        openrouter_ok = await openrouter.health()

    if provider == "ollama":
        healthy = ollama_ok
    elif provider == "openrouter":
        healthy = openrouter_ok or ollama_ok
    else:
        healthy = False

    return {
        "status": "ok" if healthy else "degraded",
        "provider": provider,
        "ollama": ollama_ok,
        "openrouter": openrouter_ok,
        "primary_model": (
            os.getenv("OPENROUTER_MODEL", "openrouter/free")
            if provider == "openrouter"
            else router.registry.get("fallback")["name"]
        ),
        "ollama_models": ollama_models,
    }


@app.get("/models")
def models():
    return {
        "provider": provider_name(),
        "roles": router.registry.all(),
    }


@app.post("/task")
async def task(request: TaskRequest):
    role = router.choose_role(request.task, request.complexity)

    try:
        cfg = router.registry.get(role)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc

    provider = os.getenv("AI_PROVIDER", cfg.get("provider", "openrouter")).lower()

    try:
        client = client_for(provider)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    model = (
        os.getenv("OPENROUTER_MODEL", "openrouter/free")
        if provider == "openrouter"
        else router.registry.get("fallback")["name"]
    )

    context = "\n".join(
        f"[{item['kind']}] {item['content']}"
        for item in memory.recent(request.project)
    )

    try:
        result = await agents[role].run(
            client,
            model,
            request.task,
            context,
        )
    except Exception as exc:
        if provider == "openrouter":
            fallback = router.registry.get("fallback")
            try:
                result = await agents[role].run(
                    ollama,
                    fallback["name"],
                    request.task,
                    context,
                )
                provider = "ollama"
                model = fallback["name"]
            except Exception as fallback_exc:
                raise HTTPException(
                    502,
                    f"OpenRouter execution failed: {exc}; "
                    f"local fallback failed: {fallback_exc}",
                ) from fallback_exc
        else:
            raise HTTPException(
                502,
                f"Model execution failed: {exc}",
            ) from exc

    memory.add(request.project, role, result)

    return {
        "agent": role,
        "provider": provider,
        "model": model,
        "result": result,
    }


@app.get("/memory/{project}")
def get_memory(project: str):
    return memory.recent(project)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=int(os.getenv("ORCHESTRATOR_PORT", "8100")),
    )
