from pathlib import Path
import os
class Workspace:
    def __init__(self):
        self.root = Path(os.getenv("AI_WORKSPACE", "./workspace/projects")).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
    def safe_path(self, relative: str) -> Path:
        candidate = (self.root / relative).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise PermissionError("Path is outside AI_WORKSPACE")
        return candidate
