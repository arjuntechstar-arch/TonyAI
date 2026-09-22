import asyncio
import os
import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agents.coder import CoderAgent
from .agents.planner import PlannerAgent
from .agents.reviewer import ReviewerAgent
from .memory.store import MemoryStore
from .models.model_router import ModelRouter
from .models.ollama_client import OllamaClient
from .models.openrouter_client import OpenRouterClient


app = FastAPI(title="TonyAI Orchestrator", version="0.2.1")

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

task_states: dict[str, dict] = {}


class TaskRequest(BaseModel):
    task: str = Field(min_length=1)
    project: str = "default"
    complexity: int = Field(default=5, ge=1, le=10)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_task_state(request: TaskRequest) -> tuple[str, float]:
    task_id = str(uuid.uuid4())
    started = time.perf_counter()
    task_states[task_id] = {
        "task_id": task_id,
        "project": request.project,
        "status": "received",
        "progress_percent": 0,
        "current_step": "Task received",
        "message": "TonyAI accepted the task.",
        "agent": None,
        "provider": None,
        "model": None,
        "start_time": utc_now(),
        "end_time": None,
        "duration_seconds": None,
        "_started_perf": started,
        "result": None,
        "error": None,
    }
    return task_id, started


def update_task(task_id: str, **changes):
    state = task_states.get(task_id)
    if not state:
        return
    state.update(changes)
    state["duration_seconds"] = round(
        time.perf_counter() - state["_started_perf"], 2
    )


def finish_task(task_id: str, status: str, **changes):
    state = task_states.get(task_id)
    if not state:
        return
    state.update(changes)
    state["status"] = status
    state["end_time"] = utc_now()
    state["duration_seconds"] = round(
        time.perf_counter() - state["_started_perf"], 2
    )
    state.pop("_started_perf", None)


def public_task_state(state: dict) -> dict:
    return {k: v for k, v in state.items() if not k.startswith("_")}


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
        "local_fallback": router.registry.get("fallback")["name"],
        "ollama_models": ollama_models,
    }


@app.get("/models")
def models():
    return {
        "provider": provider_name(),
        "roles": router.registry.all(),
    }


@app.get("/task/{task_id}")
def task_status(task_id: str):
    state = task_states.get(task_id)
    if not state:
        raise HTTPException(404, "Task not found")
    return public_task_state(state)


async def execute_task(task_id: str, request: TaskRequest):
    try:
        update_task(
            task_id,
            status="planning",
            progress_percent=10,
            current_step="Selecting agent",
            message="Analyzing the task and selecting the appropriate TonyAI agent.",
        )

        role = router.choose_role(request.task, request.complexity)
        cfg = router.registry.get(role)

        update_task(
            task_id,
            status="routing",
            progress_percent=20,
            current_step=f"Agent selected: {role}",
            message=f"Preparing {role} agent.",
            agent=role,
        )

        provider = os.getenv(
            "AI_PROVIDER",
            cfg.get("provider", "openrouter"),
        ).lower()
        client = client_for(provider)

        model = (
            os.getenv("OPENROUTER_MODEL", "openrouter/free")
            if provider == "openrouter"
            else router.registry.get("fallback")["name"]
        )

        update_task(
            task_id,
            status="executing",
            progress_percent=30,
            current_step=f"Calling {provider}",
            message=f"Running {role} with {model}.",
            provider=provider,
            model=model,
        )

        context = "
".join(
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
            if provider != "openrouter":
                raise

            fallback = router.registry.get("fallback")
            update_task(
                task_id,
                status="fallback",
                progress_percent=55,
                current_step="Switching to local fallback",
                message=f"OpenRouter failed. Retrying with {fallback['name']}.",
                provider="ollama",
                model=fallback["name"],
            )

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
                raise RuntimeError(
                    f"OpenRouter execution failed: {exc}; "
                    f"local fallback failed: {fallback_exc}"
                ) from fallback_exc

        update_task(
            task_id,
            status="completed",
            progress_percent=100,
            current_step="Completed",
            message="Task execution completed successfully.",
            provider=provider,
            model=model,
            result=result,
        )
        memory.add(request.project, role, result)

    except Exception as exc:
        finish_task(
            task_id,
            "failed",
            progress_percent=100,
            current_step="Failed",
            message="TonyAI could not complete the task.",
            error=str(exc),
        )


@app.post("/task", status_code=202)
async def task(request: TaskRequest):
    task_id, _ = create_task_state(request)
    asyncio.create_task(execute_task(task_id, request))

    return {
        "task_id": task_id,
        "status": "received",
        "message": "Task accepted. Poll /task/{task_id} for live progress.",
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
