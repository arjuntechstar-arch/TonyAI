import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .models.ollama_client import OllamaClient
from .models.model_router import ModelRouter
from .agents.planner import PlannerAgent
from .agents.coder import CoderAgent
from .agents.reviewer import ReviewerAgent
from .memory.store import MemoryStore

app = FastAPI(title="Local AI Engineer Orchestrator", version="0.1.0")
client, router, memory = OllamaClient(), ModelRouter(), MemoryStore()
agents = {"planner": PlannerAgent(), "engineer": CoderAgent(), "reviewer": ReviewerAgent()}

class TaskRequest(BaseModel):
    task: str = Field(min_length=1)
    project: str = "default"
    complexity: int = Field(default=5, ge=1, le=10)

@app.get("/health")
async def health():
    try:
        return {"status":"ok", "ollama":True, "models":(await client.list_models()).get("models",[])}
    except Exception as e:
        return {"status":"degraded", "ollama":False, "error":str(e)}

@app.get("/models")
def models(): return router.registry.all()

@app.post("/task")
async def task(request: TaskRequest):
    role = router.choose_role(request.task, request.complexity)
    try: cfg = router.registry.get(role)
    except Exception as e: raise HTTPException(400, str(e))
    context = "\n".join(f"[{m['kind']}] {m['content']}" for m in memory.recent(request.project))
    try: result = await agents[role].run(client, cfg["name"], request.task, context)
    except Exception as e: raise HTTPException(502, f"Model execution failed: {e}")
    memory.add(request.project, role, result)
    return {"agent":role,"model":cfg["name"],"result":result}

@app.get("/memory/{project}")
def get_memory(project: str): return memory.recent(project)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=int(os.getenv("ORCHESTRATOR_PORT","8100")))
