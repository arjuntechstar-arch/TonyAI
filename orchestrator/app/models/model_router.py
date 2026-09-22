from .model_registry import ModelRegistry

class ModelRouter:
    def __init__(self):
        self.registry = ModelRegistry()

    def choose_role(self, task: str, complexity: int = 5) -> str:
        text = task.lower()
        if any(x in text for x in ["review", "review code", "code review"]):
            return "reviewer"
        if any(x in text for x in ["plan", "architecture", "design"]):
            return "planner"
        if complexity >= 9 and self.registry.all()["heavy_coder"].get("enabled", False):
            return "heavy_coder"
        return "engineer"
